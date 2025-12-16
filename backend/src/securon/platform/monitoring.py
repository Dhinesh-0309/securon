"""Platform monitoring and health checking"""

import asyncio
import time
import psutil
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

from .config import MonitoringConfig
from .logging import get_logger


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a platform component"""
    name: str
    status: HealthStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]
    process_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class PlatformMetrics:
    """Platform-specific metrics"""
    timestamp: datetime
    active_scans: int
    processed_logs: int
    active_rules: int
    candidate_rules: int
    anomalies_detected: int
    api_requests_per_minute: int
    average_response_time_ms: float
    error_rate_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


class HealthChecker:
    """Health checking for platform components"""
    
    def __init__(self):
        self.health_checks: Dict[str, Callable] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        self.logger = get_logger('securon.platform.monitoring')
    
    def register_health_check(self, component_name: str, check_func: Callable) -> None:
        """Register a health check function for a component"""
        self.health_checks[component_name] = check_func
        self.logger.info(f"Registered health check for component: {component_name}")
    
    async def check_component_health(self, component_name: str) -> ComponentHealth:
        """Check health of a specific component"""
        if component_name not in self.health_checks:
            return ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.now(),
                error_message="No health check registered"
            )
        
        start_time = time.time()
        
        try:
            check_func = self.health_checks[component_name]
            
            # Execute health check (handle both sync and async functions)
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Parse result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                metadata = {}
                error_message = None
            elif isinstance(result, dict):
                status = HealthStatus(result.get('status', 'healthy'))
                metadata = result.get('metadata', {})
                error_message = result.get('error')
            else:
                status = HealthStatus.HEALTHY
                metadata = {'result': str(result)}
                error_message = None
            
            health = ComponentHealth(
                name=component_name,
                status=status,
                last_check=datetime.now(),
                response_time_ms=response_time_ms,
                error_message=error_message,
                metadata=metadata
            )
            
            self.component_health[component_name] = health
            return health
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            
            health = ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.now(),
                response_time_ms=response_time_ms,
                error_message=str(e)
            )
            
            self.component_health[component_name] = health
            self.logger.error(f"Health check failed for {component_name}: {e}")
            return health
    
    async def check_all_components(self) -> Dict[str, ComponentHealth]:
        """Check health of all registered components"""
        tasks = []
        for component_name in self.health_checks.keys():
            task = self.check_component_health(component_name)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
        
        return self.component_health.copy()
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall platform health status"""
        if not self.component_health:
            return HealthStatus.UNHEALTHY
        
        statuses = [health.status for health in self.component_health.values()]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED


class MetricsCollector:
    """Collects system and platform metrics"""
    
    def __init__(self):
        self.logger = get_logger('securon.platform.monitoring')
        self.platform_counters = {
            'active_scans': 0,
            'processed_logs': 0,
            'active_rules': 0,
            'candidate_rules': 0,
            'anomalies_detected': 0,
            'api_requests': 0,
            'api_errors': 0
        }
        self.response_times: List[float] = []
        self.last_api_request_count = 0
        self.last_metrics_time = datetime.now()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory_percent,
                disk_usage_percent=disk_percent,
                network_io_bytes=network_io,
                process_count=process_count
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            # Return default metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                disk_usage_percent=0.0,
                network_io_bytes={'bytes_sent': 0, 'bytes_recv': 0},
                process_count=0
            )
    
    def collect_platform_metrics(self) -> PlatformMetrics:
        """Collect platform-specific metrics"""
        now = datetime.now()
        time_diff = (now - self.last_metrics_time).total_seconds() / 60.0  # minutes
        
        # Calculate requests per minute
        current_requests = self.platform_counters['api_requests']
        requests_per_minute = (current_requests - self.last_api_request_count) / max(time_diff, 1.0)
        self.last_api_request_count = current_requests
        self.last_metrics_time = now
        
        # Calculate average response time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        
        # Calculate error rate
        total_requests = self.platform_counters['api_requests']
        total_errors = self.platform_counters['api_errors']
        error_rate = (total_errors / max(total_requests, 1)) * 100
        
        # Clear response times buffer (keep last 100 entries)
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
        
        return PlatformMetrics(
            timestamp=now,
            active_scans=self.platform_counters['active_scans'],
            processed_logs=self.platform_counters['processed_logs'],
            active_rules=self.platform_counters['active_rules'],
            candidate_rules=self.platform_counters['candidate_rules'],
            anomalies_detected=self.platform_counters['anomalies_detected'],
            api_requests_per_minute=int(requests_per_minute),
            average_response_time_ms=avg_response_time,
            error_rate_percent=error_rate
        )
    
    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a platform counter"""
        if counter_name in self.platform_counters:
            self.platform_counters[counter_name] += value
    
    def set_counter(self, counter_name: str, value: int) -> None:
        """Set a platform counter value"""
        if counter_name in self.platform_counters:
            self.platform_counters[counter_name] = value
    
    def record_response_time(self, response_time_ms: float) -> None:
        """Record an API response time"""
        self.response_times.append(response_time_ms)


class PlatformMonitor:
    """Main monitoring coordinator for the platform"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger('securon.platform.monitoring')
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
    
    def register_health_check(self, component_name: str, check_func: Callable) -> None:
        """Register a health check for a component"""
        self.health_checker.register_health_check(component_name, check_func)
    
    def register_alert_callback(self, callback: Callable) -> None:
        """Register a callback for alerts"""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self) -> None:
        """Start the monitoring loop"""
        if not self.config.enabled:
            self.logger.info("Monitoring is disabled")
            return
        
        self.running = True
        self.logger.info("Starting platform monitoring")
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self) -> None:
        """Stop the monitoring loop"""
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Platform monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect metrics
                system_metrics = self.metrics_collector.collect_system_metrics()
                platform_metrics = self.metrics_collector.collect_platform_metrics()
                
                # Check for alerts
                await self._check_alerts(system_metrics, platform_metrics)
                
                # Health checks (less frequent)
                if int(time.time()) % self.config.health_check_interval_seconds == 0:
                    await self.health_checker.check_all_components()
                
                # Wait for next interval
                await asyncio.sleep(self.config.metrics_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.metrics_interval_seconds)
    
    async def _check_alerts(self, system_metrics: SystemMetrics, platform_metrics: PlatformMetrics) -> None:
        """Check for alert conditions"""
        alerts = []
        
        # Check system thresholds
        if system_metrics.cpu_usage_percent > self.config.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'high_cpu_usage',
                'value': system_metrics.cpu_usage_percent,
                'threshold': self.config.alert_thresholds['cpu_usage']
            })
        
        if system_metrics.memory_usage_percent > self.config.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'high_memory_usage',
                'value': system_metrics.memory_usage_percent,
                'threshold': self.config.alert_thresholds['memory_usage']
            })
        
        # Check platform thresholds
        if platform_metrics.error_rate_percent > self.config.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'value': platform_metrics.error_rate_percent,
                'threshold': self.config.alert_thresholds['error_rate']
            })
        
        if platform_metrics.average_response_time_ms > self.config.alert_thresholds['response_time_ms']:
            alerts.append({
                'type': 'high_response_time',
                'value': platform_metrics.average_response_time_ms,
                'threshold': self.config.alert_thresholds['response_time_ms']
            })
        
        # Trigger alert callbacks
        for alert in alerts:
            self.logger.warning(f"ALERT: {alert['type']} - {alert['value']} exceeds threshold {alert['threshold']}")
            
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        component_health = await self.health_checker.check_all_components()
        overall_health = self.health_checker.get_overall_health()
        
        return {
            'overall_status': overall_health.value,
            'components': {name: asdict(health) for name, health in component_health.items()},
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        system_metrics = self.metrics_collector.collect_system_metrics()
        platform_metrics = self.metrics_collector.collect_platform_metrics()
        
        return {
            'system': system_metrics.to_dict(),
            'platform': platform_metrics.to_dict()
        }
    
    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a platform counter"""
        self.metrics_collector.increment_counter(counter_name, value)
    
    def set_counter(self, counter_name: str, value: int) -> None:
        """Set a platform counter value"""
        self.metrics_collector.set_counter(counter_name, value)
    
    def record_response_time(self, response_time_ms: float) -> None:
        """Record an API response time"""
        self.metrics_collector.record_response_time(response_time_ms)