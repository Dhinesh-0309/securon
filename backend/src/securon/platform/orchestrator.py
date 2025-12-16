"""Central platform orchestrator for component coordination"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from datetime import datetime

from ..interfaces import *
# Delayed import to avoid circular dependency
from ..ml_engine.factory import create_ml_engine
# Delayed import to avoid circular dependency
from ..log_processor.batch_processor import BatchLogProcessor

from .config import PlatformConfig
from .logging import setup_logging, get_logger, log_component_startup, log_component_shutdown, log_error_with_context, log_performance_metric
from .monitoring import PlatformMonitor, HealthStatus


class ComponentError(Exception):
    """Exception raised when a component fails to initialize or operate"""
    pass


class PlatformOrchestrator:
    """Central orchestrator for the Securon platform"""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.logger = get_logger('securon.platform.orchestrator')
        
        # Component instances
        self.iac_scanner: Optional[IaCScanner] = None
        self.ml_engine: Optional[MLEngine] = None
        self.rule_engine: Optional[RuleEngine] = None
        self.log_processor: Optional[BatchLogProcessor] = None
        self.monitor: Optional[PlatformMonitor] = None
        
        # State tracking
        self.initialized = False
        self.running = False
        self.startup_time: Optional[datetime] = None
        
        # Component health status
        self.component_status: Dict[str, bool] = {}
        
        # Error recovery
        self.max_retries = 3
        self.retry_delay_seconds = 5
    
    async def initialize(self) -> None:
        """Initialize all platform components"""
        if self.initialized:
            self.logger.warning("Platform already initialized")
            return
        
        self.logger.info("Initializing Securon Platform")
        self.startup_time = datetime.now()
        
        try:
            # Validate configuration
            self.config.validate()
            
            # Setup logging
            setup_logging(self.config.logging)
            log_component_startup('platform', '1.0.0')
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Initialize components in dependency order
            await self._initialize_rule_engine()
            await self._initialize_ml_engine()
            await self._initialize_iac_scanner()
            await self._initialize_log_processor()
            
            # Register health checks
            await self._register_health_checks()
            
            # Start monitoring
            if self.monitor:
                await self.monitor.start_monitoring()
            
            self.initialized = True
            self.running = True
            
            startup_duration = (datetime.now() - self.startup_time).total_seconds() * 1000
            log_performance_metric('platform', 'startup', startup_duration, True)
            self.logger.info(f"Platform initialization completed in {startup_duration:.2f}ms")
            
        except Exception as e:
            log_error_with_context('platform', e, {'phase': 'initialization'})
            await self._cleanup_on_error()
            raise ComponentError(f"Platform initialization failed: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown all platform components gracefully"""
        if not self.initialized:
            self.logger.warning("Platform not initialized")
            return
        
        self.logger.info("Shutting down Securon Platform")
        self.running = False
        
        try:
            # Stop monitoring
            if self.monitor:
                await self.monitor.stop_monitoring()
            
            # Shutdown components in reverse order
            await self._shutdown_log_processor()
            await self._shutdown_iac_scanner()
            await self._shutdown_ml_engine()
            await self._shutdown_rule_engine()
            
            log_component_shutdown('platform')
            self.initialized = False
            
        except Exception as e:
            log_error_with_context('platform', e, {'phase': 'shutdown'})
            raise ComponentError(f"Platform shutdown failed: {e}")
    
    async def _initialize_monitoring(self) -> None:
        """Initialize monitoring system"""
        try:
            self.monitor = PlatformMonitor(self.config.monitoring)
            self.component_status['monitoring'] = True
            log_component_startup('monitoring')
            
        except Exception as e:
            self.component_status['monitoring'] = False
            log_error_with_context('monitoring', e)
            raise ComponentError(f"Failed to initialize monitoring: {e}")
    
    async def _initialize_rule_engine(self) -> None:
        """Initialize Rule Engine component"""
        try:
            from ..rule_engine.factory import create_rule_engine
            self.rule_engine = create_rule_engine(self.config.rule_engine.storage_path)
            
            # Test the rule engine
            await self._test_component('rule_engine', self.rule_engine.get_active_rules)
            
            self.component_status['rule_engine'] = True
            log_component_startup('rule_engine')
            
        except Exception as e:
            self.component_status['rule_engine'] = False
            log_error_with_context('rule_engine', e)
            raise ComponentError(f"Failed to initialize Rule Engine: {e}")
    
    async def _initialize_ml_engine(self) -> None:
        """Initialize ML Engine component"""
        try:
            self.ml_engine = create_ml_engine(
                contamination=self.config.ml_engine.contamination,
                random_state=self.config.ml_engine.random_state
            )
            
            # Test the ML engine with empty logs
            await self._test_component('ml_engine', lambda: self.ml_engine.process_logs([]))
            
            self.component_status['ml_engine'] = True
            log_component_startup('ml_engine')
            
        except Exception as e:
            self.component_status['ml_engine'] = False
            log_error_with_context('ml_engine', e)
            raise ComponentError(f"Failed to initialize ML Engine: {e}")
    
    async def _initialize_iac_scanner(self) -> None:
        """Initialize IaC Scanner component"""
        try:
            from ..iac_scanner.factory import IaCScannerFactory
            self.iac_scanner = await IaCScannerFactory.create_scanner_async(self.rule_engine)
            
            self.component_status['iac_scanner'] = True
            log_component_startup('iac_scanner')
            
        except Exception as e:
            self.component_status['iac_scanner'] = False
            log_error_with_context('iac_scanner', e)
            raise ComponentError(f"Failed to initialize IaC Scanner: {e}")
    
    async def _initialize_log_processor(self) -> None:
        """Initialize Log Processor component"""
        try:
            self.log_processor = BatchLogProcessor()
            
            self.component_status['log_processor'] = True
            log_component_startup('log_processor')
            
        except Exception as e:
            self.component_status['log_processor'] = False
            log_error_with_context('log_processor', e)
            raise ComponentError(f"Failed to initialize Log Processor: {e}")
    
    async def _test_component(self, component_name: str, test_func) -> None:
        """Test a component to ensure it's working"""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                result = test_func()
                # If the function returns a coroutine, await it
                if asyncio.iscoroutine(result):
                    await result
            
            duration_ms = (time.time() - start_time) * 1000
            log_performance_metric(component_name, 'health_check', duration_ms, True)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_performance_metric(component_name, 'health_check', duration_ms, False)
            raise e
    
    async def _register_health_checks(self) -> None:
        """Register health checks for all components"""
        if not self.monitor:
            return
        
        # Rule Engine health check
        async def rule_engine_health():
            if not self.rule_engine:
                return {'status': 'unhealthy', 'error': 'Component not initialized'}
            try:
                rules = await self.rule_engine.get_active_rules()
                return {
                    'status': 'healthy',
                    'metadata': {'active_rules_count': len(rules)}
                }
            except Exception as e:
                return {'status': 'unhealthy', 'error': str(e)}
        
        # ML Engine health check
        async def ml_engine_health():
            if not self.ml_engine:
                return {'status': 'unhealthy', 'error': 'Component not initialized'}
            try:
                # Test with empty logs
                await self.ml_engine.process_logs([])
                return {'status': 'healthy'}
            except Exception as e:
                return {'status': 'unhealthy', 'error': str(e)}
        
        # IaC Scanner health check
        def iac_scanner_health():
            if not self.iac_scanner:
                return {'status': 'unhealthy', 'error': 'Component not initialized'}
            return {'status': 'healthy'}
        
        # Log Processor health check
        def log_processor_health():
            if not self.log_processor:
                return {'status': 'unhealthy', 'error': 'Component not initialized'}
            return {'status': 'healthy'}
        
        # Register all health checks
        self.monitor.register_health_check('rule_engine', rule_engine_health)
        self.monitor.register_health_check('ml_engine', ml_engine_health)
        self.monitor.register_health_check('iac_scanner', iac_scanner_health)
        self.monitor.register_health_check('log_processor', log_processor_health)
    
    async def _shutdown_rule_engine(self) -> None:
        """Shutdown Rule Engine component"""
        if self.rule_engine:
            try:
                # Rule engine doesn't have explicit shutdown, just clear reference
                self.rule_engine = None
                log_component_shutdown('rule_engine')
            except Exception as e:
                log_error_with_context('rule_engine', e, {'phase': 'shutdown'})
    
    async def _shutdown_ml_engine(self) -> None:
        """Shutdown ML Engine component"""
        if self.ml_engine:
            try:
                # ML engine doesn't have explicit shutdown, just clear reference
                self.ml_engine = None
                log_component_shutdown('ml_engine')
            except Exception as e:
                log_error_with_context('ml_engine', e, {'phase': 'shutdown'})
    
    async def _shutdown_iac_scanner(self) -> None:
        """Shutdown IaC Scanner component"""
        if self.iac_scanner:
            try:
                # IaC scanner doesn't have explicit shutdown, just clear reference
                self.iac_scanner = None
                log_component_shutdown('iac_scanner')
            except Exception as e:
                log_error_with_context('iac_scanner', e, {'phase': 'shutdown'})
    
    async def _shutdown_log_processor(self) -> None:
        """Shutdown Log Processor component"""
        if self.log_processor:
            try:
                # Log processor doesn't have explicit shutdown, just clear reference
                self.log_processor = None
                log_component_shutdown('log_processor')
            except Exception as e:
                log_error_with_context('log_processor', e, {'phase': 'shutdown'})
    
    async def _cleanup_on_error(self) -> None:
        """Cleanup resources when initialization fails"""
        try:
            await self.shutdown()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    # Public API methods for component access
    
    def get_iac_scanner(self) -> IaCScanner:
        """Get the IaC Scanner component"""
        if not self.iac_scanner:
            raise ComponentError("IaC Scanner not initialized")
        return self.iac_scanner
    
    def get_ml_engine(self) -> MLEngine:
        """Get the ML Engine component"""
        if not self.ml_engine:
            raise ComponentError("ML Engine not initialized")
        return self.ml_engine
    
    def get_rule_engine(self) -> RuleEngine:
        """Get the Rule Engine component"""
        if not self.rule_engine:
            raise ComponentError("Rule Engine not initialized")
        return self.rule_engine
    
    def get_log_processor(self) -> BatchLogProcessor:
        """Get the Log Processor component"""
        if not self.log_processor:
            raise ComponentError("Log Processor not initialized")
        return self.log_processor
    
    def get_monitor(self) -> PlatformMonitor:
        """Get the Platform Monitor"""
        if not self.monitor:
            raise ComponentError("Monitor not initialized")
        return self.monitor
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status"""
        if not self.initialized:
            return {
                'status': 'not_initialized',
                'components': {},
                'uptime_seconds': 0
            }
        
        # Calculate uptime
        uptime_seconds = 0
        if self.startup_time:
            uptime_seconds = (datetime.now() - self.startup_time).total_seconds()
        
        # Get component health
        health_status = {}
        if self.monitor:
            health_data = await self.monitor.get_health_status()
            health_status = health_data.get('components', {})
        
        return {
            'status': 'running' if self.running else 'stopped',
            'components': {
                name: {
                    'initialized': status,
                    'health': health_status.get(name, {}).get('status', 'unknown')
                }
                for name, status in self.component_status.items()
            },
            'uptime_seconds': int(uptime_seconds),
            'startup_time': self.startup_time.isoformat() if self.startup_time else None
        }
    
    async def restart_component(self, component_name: str) -> bool:
        """Restart a specific component"""
        self.logger.info(f"Restarting component: {component_name}")
        
        try:
            if component_name == 'rule_engine':
                await self._shutdown_rule_engine()
                await self._initialize_rule_engine()
            elif component_name == 'ml_engine':
                await self._shutdown_ml_engine()
                await self._initialize_ml_engine()
            elif component_name == 'iac_scanner':
                await self._shutdown_iac_scanner()
                await self._initialize_iac_scanner()
            elif component_name == 'log_processor':
                await self._shutdown_log_processor()
                await self._initialize_log_processor()
            else:
                raise ValueError(f"Unknown component: {component_name}")
            
            self.logger.info(f"Component {component_name} restarted successfully")
            return True
            
        except Exception as e:
            log_error_with_context(component_name, e, {'operation': 'restart'})
            return False
    
    @asynccontextmanager
    async def component_operation(self, component_name: str, operation_name: str):
        """Context manager for component operations with error handling and metrics"""
        start_time = time.time()
        success = False
        
        try:
            if self.monitor:
                self.monitor.increment_counter('active_scans' if 'scan' in operation_name else 'api_requests')
            
            yield
            success = True
            
        except Exception as e:
            if self.monitor:
                self.monitor.increment_counter('api_errors')
            
            log_error_with_context(component_name, e, {'operation': operation_name})
            raise
            
        finally:
            duration_ms = (time.time() - start_time) * 1000
            log_performance_metric(component_name, operation_name, duration_ms, success)
            
            if self.monitor:
                self.monitor.record_response_time(duration_ms)
    
    async def process_logs_workflow(self, logs: List[CloudLog]) -> Dict[str, Any]:
        """Complete workflow for processing logs through ML engine and rule generation"""
        async with self.component_operation('ml_engine', 'process_logs_workflow'):
            # Process logs through ML engine
            anomalies = await self.ml_engine.process_logs(logs)
            
            # Generate candidate rules
            candidate_rules = self.ml_engine.generate_candidate_rules(anomalies)
            
            # Store candidate rules in rule engine
            for rule in candidate_rules:
                await self.rule_engine.add_rule(rule)
            
            # Update metrics
            if self.monitor:
                self.monitor.increment_counter('processed_logs', len(logs))
                self.monitor.increment_counter('anomalies_detected', len(anomalies))
                self.monitor.set_counter('candidate_rules', len(candidate_rules))
            
            return {
                'logs_processed': len(logs),
                'anomalies_detected': len(anomalies),
                'candidate_rules_generated': len(candidate_rules),
                'anomalies': [anomaly.dict() for anomaly in anomalies]
            }
    
    async def scan_iac_workflow(self, file_path: str) -> List[ScanResult]:
        """Complete workflow for IaC scanning with rule enforcement"""
        async with self.component_operation('iac_scanner', 'scan_iac_workflow'):
            # Get active rules and apply them
            active_rules = await self.rule_engine.get_active_rules()
            self.iac_scanner.apply_rules(active_rules)
            
            # Perform scan
            results = await self.iac_scanner.scan_file(file_path)
            
            # Update metrics
            if self.monitor:
                self.monitor.set_counter('active_rules', len(active_rules))
            
            return results