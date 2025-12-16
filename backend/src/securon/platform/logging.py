"""Platform logging configuration and utilities"""

import logging
import logging.handlers
import sys
from typing import Optional
from pathlib import Path

from .config import LoggingConfig


class PlatformLogger:
    """Centralized logging for the Securon platform"""
    
    _instance: Optional['PlatformLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'PlatformLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.loggers = {}
            self._initialized = True
    
    def setup_logging(self, config: LoggingConfig) -> None:
        """Setup platform-wide logging configuration"""
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(config.format)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, config.level.upper()))
        root_logger.addHandler(console_handler)
        
        # File handler (if configured)
        if config.file_path:
            log_file = Path(config.file_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=config.file_path,
                maxBytes=config.max_file_size_mb * 1024 * 1024,
                backupCount=config.backup_count
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, config.level.upper()))
            root_logger.addHandler(file_handler)
        
        # Setup component-specific loggers
        self._setup_component_loggers()
    
    def _setup_component_loggers(self) -> None:
        """Setup loggers for each platform component"""
        
        components = [
            'securon.platform',
            'securon.iac_scanner',
            'securon.ml_engine',
            'securon.rule_engine',
            'securon.log_processor',
            'securon.api'
        ]
        
        for component in components:
            logger = logging.getLogger(component)
            self.loggers[component] = logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific component or module"""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]
    
    def log_component_startup(self, component_name: str, version: str = None) -> None:
        """Log component startup information"""
        logger = self.get_logger(f'securon.{component_name}')
        version_info = f" v{version}" if version else ""
        logger.info(f"{component_name.title()} component started{version_info}")
    
    def log_component_shutdown(self, component_name: str) -> None:
        """Log component shutdown information"""
        logger = self.get_logger(f'securon.{component_name}')
        logger.info(f"{component_name.title()} component shutting down")
    
    def log_error_with_context(self, component_name: str, error: Exception, context: dict = None) -> None:
        """Log error with additional context information"""
        logger = self.get_logger(f'securon.{component_name}')
        
        error_msg = f"Error in {component_name}: {str(error)}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            error_msg += f" (Context: {context_str})"
        
        logger.error(error_msg, exc_info=True)
    
    def log_performance_metric(self, component_name: str, operation: str, duration_ms: float, success: bool = True) -> None:
        """Log performance metrics for operations"""
        logger = self.get_logger(f'securon.{component_name}')
        
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"PERFORMANCE: {component_name}.{operation} - {duration_ms:.2f}ms - {status}")
    
    def log_security_event(self, event_type: str, details: dict) -> None:
        """Log security-related events"""
        security_logger = self.get_logger('securon.security')
        
        details_str = ", ".join(f"{k}={v}" for k, v in details.items())
        security_logger.warning(f"SECURITY_EVENT: {event_type} - {details_str}")


# Global logger instance
_platform_logger = PlatformLogger()


def setup_logging(config: LoggingConfig) -> None:
    """Setup platform logging with the given configuration"""
    _platform_logger.setup_logging(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific component"""
    return _platform_logger.get_logger(name)


def log_component_startup(component_name: str, version: str = None) -> None:
    """Log component startup"""
    _platform_logger.log_component_startup(component_name, version)


def log_component_shutdown(component_name: str) -> None:
    """Log component shutdown"""
    _platform_logger.log_component_shutdown(component_name)


def log_error_with_context(component_name: str, error: Exception, context: dict = None) -> None:
    """Log error with context"""
    _platform_logger.log_error_with_context(component_name, error, context)


def log_performance_metric(component_name: str, operation: str, duration_ms: float, success: bool = True) -> None:
    """Log performance metric"""
    _platform_logger.log_performance_metric(component_name, operation, duration_ms, success)


def log_security_event(event_type: str, details: dict) -> None:
    """Log security event"""
    _platform_logger.log_security_event(event_type, details)