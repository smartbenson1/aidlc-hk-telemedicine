"""
Logging utilities for the User Management Service.
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class UserManagementFormatter(logging.Formatter):
    """Custom formatter for User Management Service logs."""
    
    def __init__(self):
        super().__init__()
        self.format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(correlation_id)s] - %(message)s"
        )
    
    def format(self, record):
        """Format log record with correlation ID if available."""
        # Add correlation ID if not present
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = 'N/A'
        
        # Use the format string
        formatter = logging.Formatter(self.format_string)
        return formatter.format(record)


class CorrelationFilter(logging.Filter):
    """Filter to add correlation ID to log records."""
    
    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__()
        self.correlation_id = correlation_id or 'N/A'
    
    def filter(self, record):
        """Add correlation ID to the record."""
        record.correlation_id = self.correlation_id
        return True


def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[str] = None,
                 correlation_id: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration for the User Management Service."""
    
    # Create logger
    logger = logging.getLogger("user_management_service")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = UserManagementFormatter()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    
    # Add correlation filter if provided
    if correlation_id:
        correlation_filter = CorrelationFilter(correlation_id)
        console_handler.addFilter(correlation_filter)
    
    logger.addHandler(console_handler)
    
    # Create file handler if log file specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        
        if correlation_id:
            file_handler.addFilter(correlation_filter)
        
        logger.addHandler(file_handler)
    
    return logger


def log_service_operation(logger: logging.Logger, operation: str, 
                         user_id: Optional[UUID] = None,
                         details: Optional[Dict[str, Any]] = None):
    """Log a service operation with structured information."""
    log_data = {
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": str(user_id) if user_id else None
    }
    
    if details:
        log_data.update(details)
    
    logger.info(f"Service operation: {operation}", extra=log_data)


def log_validation_error(logger: logging.Logger, error_message: str,
                        field: Optional[str] = None,
                        value: Optional[Any] = None,
                        user_id: Optional[UUID] = None):
    """Log validation errors with structured information."""
    log_data = {
        "error_type": "validation",
        "field": field,
        "value": str(value) if value is not None else None,
        "user_id": str(user_id) if user_id else None,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.warning(f"Validation error: {error_message}", extra=log_data)


def log_business_rule_violation(logger: logging.Logger, rule: str, 
                               message: str, user_id: Optional[UUID] = None,
                               details: Optional[Dict[str, Any]] = None):
    """Log business rule violations."""
    log_data = {
        "error_type": "business_rule",
        "rule": rule,
        "user_id": str(user_id) if user_id else None,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    logger.warning(f"Business rule violation [{rule}]: {message}", extra=log_data)


def log_integration_error(logger: logging.Logger, service_name: str,
                         error_message: str, status_code: Optional[int] = None,
                         details: Optional[Dict[str, Any]] = None):
    """Log integration errors with external services."""
    log_data = {
        "error_type": "integration",
        "service_name": service_name,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    logger.error(f"Integration error with {service_name}: {error_message}", extra=log_data)


def log_security_event(logger: logging.Logger, event_type: str,
                      user_id: Optional[UUID] = None,
                      ip_address: Optional[str] = None,
                      details: Optional[Dict[str, Any]] = None):
    """Log security-related events."""
    log_data = {
        "event_type": "security",
        "security_event": event_type,
        "user_id": str(user_id) if user_id else None,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    logger.warning(f"Security event [{event_type}]", extra=log_data)


def log_performance_metric(logger: logging.Logger, operation: str,
                          duration_ms: float, success: bool = True,
                          details: Optional[Dict[str, Any]] = None):
    """Log performance metrics for operations."""
    log_data = {
        "metric_type": "performance",
        "operation": operation,
        "duration_ms": duration_ms,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"Performance metric [{operation}]: {duration_ms}ms", extra=log_data)


class LoggingContext:
    """Context manager for adding correlation ID to logs."""
    
    def __init__(self, correlation_id: str, logger: logging.Logger):
        self.correlation_id = correlation_id
        self.logger = logger
        self.original_filters = []
    
    def __enter__(self):
        """Add correlation filter to all handlers."""
        correlation_filter = CorrelationFilter(self.correlation_id)
        
        for handler in self.logger.handlers:
            self.original_filters.append(handler.filters.copy())
            handler.addFilter(correlation_filter)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove correlation filter from all handlers."""
        for i, handler in enumerate(self.logger.handlers):
            # Remove all filters and restore original ones
            handler.filters.clear()
            if i < len(self.original_filters):
                for filter_obj in self.original_filters[i]:
                    handler.addFilter(filter_obj)


# Global logger instance
_logger = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance for the User Management Service."""
    global _logger
    
    if _logger is None:
        _logger = setup_logging()
    
    if name:
        return _logger.getChild(name)
    
    return _logger


def configure_logging(log_level: str = "INFO", 
                     log_file: Optional[str] = None) -> None:
    """Configure global logging settings."""
    global _logger
    _logger = setup_logging(log_level, log_file)