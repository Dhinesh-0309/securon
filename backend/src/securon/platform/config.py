"""Platform configuration management"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "securon"
    user: str = "securon"
    password: str = ""
    # SQLite configuration for development
    sqlite_path: str = "data/securon.db"
    use_sqlite: bool = True
    # Connection pool settings
    max_connections: int = 20
    connection_timeout: int = 30
    # Backup settings
    backup_path: str = "data/backups"
    auto_backup: bool = True
    
    
@dataclass
class MLEngineConfig:
    """ML Engine configuration"""
    contamination: float = 0.1
    random_state: int = 42
    batch_size: int = 1000
    max_memory_mb: int = 512
    

@dataclass
class RuleEngineConfig:
    """Rule Engine configuration"""
    storage_path: str = "data/rules"
    max_rules: int = 1000
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    max_backups: int = 50
    use_database: bool = True
    

@dataclass
class IaCScannerConfig:
    """IaC Scanner configuration"""
    max_file_size_mb: int = 10
    supported_extensions: list = None
    timeout_seconds: int = 300
    
    def __post_init__(self):
        if self.supported_extensions is None:
            self.supported_extensions = ['.tf', '.hcl', '.json']


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    metrics_interval_seconds: int = 60
    health_check_interval_seconds: int = 30
    alert_thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                'cpu_usage': 80.0,
                'memory_usage': 85.0,
                'error_rate': 5.0,
                'response_time_ms': 5000.0
            }


@dataclass
class PlatformConfig:
    """Main platform configuration"""
    environment: str = "development"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Component configurations
    database: DatabaseConfig = None
    ml_engine: MLEngineConfig = None
    rule_engine: RuleEngineConfig = None
    iac_scanner: IaCScannerConfig = None
    logging: LoggingConfig = None
    monitoring: MonitoringConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.ml_engine is None:
            self.ml_engine = MLEngineConfig()
        if self.rule_engine is None:
            self.rule_engine = RuleEngineConfig()
        if self.iac_scanner is None:
            self.iac_scanner = IaCScannerConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()
    
    @classmethod
    def from_file(cls, config_path: str) -> 'PlatformConfig':
        """Load configuration from JSON file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            # Create default config file
            default_config = cls()
            default_config.save_to_file(config_path)
            return default_config
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Create nested dataclass instances
            if 'database' in config_data:
                config_data['database'] = DatabaseConfig(**config_data['database'])
            if 'ml_engine' in config_data:
                config_data['ml_engine'] = MLEngineConfig(**config_data['ml_engine'])
            if 'rule_engine' in config_data:
                config_data['rule_engine'] = RuleEngineConfig(**config_data['rule_engine'])
            if 'iac_scanner' in config_data:
                config_data['iac_scanner'] = IaCScannerConfig(**config_data['iac_scanner'])
            if 'logging' in config_data:
                config_data['logging'] = LoggingConfig(**config_data['logging'])
            if 'monitoring' in config_data:
                config_data['monitoring'] = MonitoringConfig(**config_data['monitoring'])
            
            return cls(**config_data)
            
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise ValueError(f"Invalid configuration file {config_path}: {e}")
    
    @classmethod
    def from_environment(cls) -> 'PlatformConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # Main platform settings
        config.environment = os.getenv('SECURON_ENVIRONMENT', config.environment)
        config.debug = os.getenv('SECURON_DEBUG', str(config.debug)).lower() == 'true'
        config.api_host = os.getenv('SECURON_API_HOST', config.api_host)
        config.api_port = int(os.getenv('SECURON_API_PORT', str(config.api_port)))
        
        # Database settings
        config.database.host = os.getenv('SECURON_DB_HOST', config.database.host)
        config.database.port = int(os.getenv('SECURON_DB_PORT', str(config.database.port)))
        config.database.name = os.getenv('SECURON_DB_NAME', config.database.name)
        config.database.user = os.getenv('SECURON_DB_USER', config.database.user)
        config.database.password = os.getenv('SECURON_DB_PASSWORD', config.database.password)
        
        # ML Engine settings
        config.ml_engine.contamination = float(os.getenv('SECURON_ML_CONTAMINATION', str(config.ml_engine.contamination)))
        config.ml_engine.random_state = int(os.getenv('SECURON_ML_RANDOM_STATE', str(config.ml_engine.random_state)))
        config.ml_engine.batch_size = int(os.getenv('SECURON_ML_BATCH_SIZE', str(config.ml_engine.batch_size)))
        config.ml_engine.max_memory_mb = int(os.getenv('SECURON_ML_MAX_MEMORY_MB', str(config.ml_engine.max_memory_mb)))
        
        # Rule Engine settings
        config.rule_engine.storage_path = os.getenv('SECURON_RULES_STORAGE_PATH', config.rule_engine.storage_path)
        config.rule_engine.max_rules = int(os.getenv('SECURON_RULES_MAX_RULES', str(config.rule_engine.max_rules)))
        config.rule_engine.backup_enabled = os.getenv('SECURON_RULES_BACKUP_ENABLED', str(config.rule_engine.backup_enabled)).lower() == 'true'
        
        # Logging settings
        config.logging.level = os.getenv('SECURON_LOG_LEVEL', config.logging.level)
        config.logging.file_path = os.getenv('SECURON_LOG_FILE_PATH', config.logging.file_path)
        
        return config
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict for JSON serialization
        config_dict = asdict(self)
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def validate(self) -> None:
        """Validate configuration values"""
        errors = []
        
        # Validate ML Engine config
        if not 0 < self.ml_engine.contamination < 1:
            errors.append("ML Engine contamination must be between 0 and 1")
        
        if self.ml_engine.batch_size <= 0:
            errors.append("ML Engine batch_size must be positive")
        
        # Validate Rule Engine config
        if self.rule_engine.max_rules <= 0:
            errors.append("Rule Engine max_rules must be positive")
        
        # Validate IaC Scanner config
        if self.iac_scanner.max_file_size_mb <= 0:
            errors.append("IaC Scanner max_file_size_mb must be positive")
        
        if self.iac_scanner.timeout_seconds <= 0:
            errors.append("IaC Scanner timeout_seconds must be positive")
        
        # Validate logging config
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level.upper() not in valid_log_levels:
            errors.append(f"Logging level must be one of: {valid_log_levels}")
        
        # Validate monitoring config
        if self.monitoring.metrics_interval_seconds <= 0:
            errors.append("Monitoring metrics_interval_seconds must be positive")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                else:
                    return default
            return value
        except (AttributeError, KeyError):
            return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)