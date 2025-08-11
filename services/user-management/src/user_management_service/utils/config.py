"""
Configuration management for the User Management Service.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class DatabaseConfig:
    """Database configuration."""
    data_directory: str = "user_management_service/data"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backup_files: int = 7


@dataclass
class EmailConfig:
    """Email service configuration."""
    smtp_server: str = "localhost"
    smtp_port: int = 587
    sender_email: str = "noreply@doctorplatform.com"
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: bool = True


@dataclass
class IntegrationConfig:
    """External service integration configuration."""
    admin_service_url: str = "http://localhost:8080"
    appointment_service_url: str = "http://localhost:8081"
    admin_service_api_key: Optional[str] = None
    appointment_service_api_key: Optional[str] = None
    request_timeout_seconds: int = 30
    retry_attempts: int = 3
    circuit_breaker_threshold: int = 5


@dataclass
class SecurityConfig:
    """Security configuration."""
    session_timeout_hours: int = 24
    max_login_attempts: int = 5
    password_min_length: int = 8
    require_password_complexity: bool = True
    jwt_secret_key: Optional[str] = None
    encryption_key: Optional[str] = None


@dataclass
class BusinessRulesConfig:
    """Business rules configuration."""
    max_daily_doctor_registrations: int = 100
    max_daily_patient_registrations: int = 1000
    max_system_users: int = 60000
    max_doctor_specialties: int = 10
    max_daily_slots_per_doctor: int = 12
    max_weekly_slots_per_doctor: int = 60
    max_profile_updates_per_day: int = 5
    booking_window_days: int = 30


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_correlation_ids: bool = True
    log_format: str = "json"
    max_log_file_size_mb: int = 100
    max_log_files: int = 5


@dataclass
class ServiceConfig:
    """Main service configuration."""
    service_name: str = "user-management-service"
    version: str = "1.0.0"
    environment: str = "development"
    debug_mode: bool = False
    
    # Sub-configurations
    database: DatabaseConfig = None
    email: EmailConfig = None
    integrations: IntegrationConfig = None
    security: SecurityConfig = None
    business_rules: BusinessRulesConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        """Initialize sub-configurations if not provided."""
        if self.database is None:
            self.database = DatabaseConfig()
        if self.email is None:
            self.email = EmailConfig()
        if self.integrations is None:
            self.integrations = IntegrationConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.business_rules is None:
            self.business_rules = BusinessRulesConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigManager:
    """Configuration manager for loading and managing service configuration."""
    
    def __init__(self):
        self._config: Optional[ServiceConfig] = None
    
    def load_config(self, config_file: Optional[str] = None) -> ServiceConfig:
        """Load configuration from environment variables and optional config file."""
        if self._config is not None:
            return self._config
        
        # Load from environment variables
        config = ServiceConfig(
            service_name=os.getenv("SERVICE_NAME", "user-management-service"),
            version=os.getenv("SERVICE_VERSION", "1.0.0"),
            environment=os.getenv("ENVIRONMENT", "development"),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
        )
        
        # Database configuration
        config.database = DatabaseConfig(
            data_directory=os.getenv("DATA_DIRECTORY", "user_management_service/data"),
            backup_enabled=os.getenv("BACKUP_ENABLED", "true").lower() == "true",
            backup_interval_hours=int(os.getenv("BACKUP_INTERVAL_HOURS", "24")),
            max_backup_files=int(os.getenv("MAX_BACKUP_FILES", "7"))
        )
        
        # Email configuration
        config.email = EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            sender_email=os.getenv("SENDER_EMAIL", "noreply@doctorplatform.com"),
            smtp_username=os.getenv("SMTP_USERNAME"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        )
        
        # Integration configuration
        config.integrations = IntegrationConfig(
            admin_service_url=os.getenv("ADMIN_SERVICE_URL", "http://localhost:8080"),
            appointment_service_url=os.getenv("APPOINTMENT_SERVICE_URL", "http://localhost:8081"),
            admin_service_api_key=os.getenv("ADMIN_SERVICE_API_KEY"),
            appointment_service_api_key=os.getenv("APPOINTMENT_SERVICE_API_KEY"),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            circuit_breaker_threshold=int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
        )
        
        # Security configuration
        config.security = SecurityConfig(
            session_timeout_hours=int(os.getenv("SESSION_TIMEOUT_HOURS", "24")),
            max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            require_password_complexity=os.getenv("REQUIRE_PASSWORD_COMPLEXITY", "true").lower() == "true",
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            encryption_key=os.getenv("ENCRYPTION_KEY")
        )
        
        # Business rules configuration
        config.business_rules = BusinessRulesConfig(
            max_daily_doctor_registrations=int(os.getenv("MAX_DAILY_DOCTOR_REGISTRATIONS", "100")),
            max_daily_patient_registrations=int(os.getenv("MAX_DAILY_PATIENT_REGISTRATIONS", "1000")),
            max_system_users=int(os.getenv("MAX_SYSTEM_USERS", "60000")),
            max_doctor_specialties=int(os.getenv("MAX_DOCTOR_SPECIALTIES", "10")),
            max_daily_slots_per_doctor=int(os.getenv("MAX_DAILY_SLOTS_PER_DOCTOR", "12")),
            max_weekly_slots_per_doctor=int(os.getenv("MAX_WEEKLY_SLOTS_PER_DOCTOR", "60")),
            max_profile_updates_per_day=int(os.getenv("MAX_PROFILE_UPDATES_PER_DAY", "5")),
            booking_window_days=int(os.getenv("BOOKING_WINDOW_DAYS", "30"))
        )
        
        # Logging configuration
        config.logging = LoggingConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
            enable_correlation_ids=os.getenv("ENABLE_CORRELATION_IDS", "true").lower() == "true",
            log_format=os.getenv("LOG_FORMAT", "json"),
            max_log_file_size_mb=int(os.getenv("MAX_LOG_FILE_SIZE_MB", "100")),
            max_log_files=int(os.getenv("MAX_LOG_FILES", "5"))
        )
        
        # Load from config file if provided
        if config_file:
            self._load_from_file(config, config_file)
        
        self._config = config
        return self._config
    
    def _load_from_file(self, config: ServiceConfig, config_file: str) -> None:
        """Load additional configuration from file (JSON or YAML)."""
        import json
        
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    file_config = json.load(f)
                    self._merge_config(config, file_config)
                elif config_file.endswith(('.yml', '.yaml')):
                    try:
                        import yaml
                        file_config = yaml.safe_load(f)
                        self._merge_config(config, file_config)
                    except ImportError:
                        print("PyYAML not installed, skipping YAML config file")
        except FileNotFoundError:
            print(f"Config file {config_file} not found, using environment variables only")
        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
    
    def _merge_config(self, config: ServiceConfig, file_config: Dict[str, Any]) -> None:
        """Merge file configuration with existing configuration."""
        # This is a simplified merge - in a real implementation,
        # you'd want more sophisticated merging logic
        
        if 'database' in file_config:
            db_config = file_config['database']
            if 'data_directory' in db_config:
                config.database.data_directory = db_config['data_directory']
            if 'backup_enabled' in db_config:
                config.database.backup_enabled = db_config['backup_enabled']
        
        if 'email' in file_config:
            email_config = file_config['email']
            if 'smtp_server' in email_config:
                config.email.smtp_server = email_config['smtp_server']
            if 'smtp_port' in email_config:
                config.email.smtp_port = email_config['smtp_port']
        
        # Add more merge logic as needed
    
    def get_config(self) -> ServiceConfig:
        """Get the current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self, config_file: Optional[str] = None) -> ServiceConfig:
        """Reload configuration."""
        self._config = None
        return self.load_config(config_file)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        config = self.get_config()
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate required fields
        if not config.email.sender_email:
            validation_results["errors"].append("Email sender address is required")
            validation_results["valid"] = False
        
        if not config.integrations.admin_service_url:
            validation_results["errors"].append("Admin service URL is required")
            validation_results["valid"] = False
        
        # Validate ranges
        if config.security.session_timeout_hours < 1:
            validation_results["errors"].append("Session timeout must be at least 1 hour")
            validation_results["valid"] = False
        
        if config.business_rules.max_daily_slots_per_doctor > 24:
            validation_results["warnings"].append("Daily slot limit exceeds 24 hours")
        
        # Validate environment-specific settings
        if config.environment == "production":
            if config.debug_mode:
                validation_results["warnings"].append("Debug mode enabled in production")
            
            if not config.security.jwt_secret_key:
                validation_results["errors"].append("JWT secret key required in production")
                validation_results["valid"] = False
        
        return validation_results


# Global configuration manager instance
_config_manager = ConfigManager()


def get_config() -> ServiceConfig:
    """Get the global service configuration."""
    return _config_manager.get_config()


def load_config(config_file: Optional[str] = None) -> ServiceConfig:
    """Load the global service configuration."""
    return _config_manager.load_config(config_file)


def reload_config(config_file: Optional[str] = None) -> ServiceConfig:
    """Reload the global service configuration."""
    return _config_manager.reload_config(config_file)


def validate_config() -> Dict[str, Any]:
    """Validate the global service configuration."""
    return _config_manager.validate_config()