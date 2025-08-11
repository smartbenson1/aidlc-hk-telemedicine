"""
Custom exception classes for the User Management Service.
"""

from typing import Optional, Dict, Any
from uuid import UUID


class UserManagementException(Exception):
    """Base exception for User Management Service."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}


class ValidationError(UserManagementException):
    """Raised when validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class BusinessRuleError(UserManagementException):
    """Raised when business rules are violated."""
    
    def __init__(self, message: str, rule: Optional[str] = None):
        super().__init__(message, "BUSINESS_RULE_ERROR")
        self.rule = rule


class RegistrationError(UserManagementException):
    """Raised when user registration fails."""
    
    def __init__(self, message: str, email: Optional[str] = None, 
                 user_type: Optional[str] = None):
        super().__init__(message, "REGISTRATION_ERROR")
        self.email = email
        self.user_type = user_type


class ProfileUpdateError(UserManagementException):
    """Raised when profile update fails."""
    
    def __init__(self, message: str, user_id: Optional[UUID] = None, 
                 field: Optional[str] = None):
        super().__init__(message, "PROFILE_UPDATE_ERROR")
        self.user_id = user_id
        self.field = field


class AvailabilityError(UserManagementException):
    """Raised when availability management fails."""
    
    def __init__(self, message: str, doctor_id: Optional[UUID] = None, 
                 slot_id: Optional[UUID] = None):
        super().__init__(message, "AVAILABILITY_ERROR")
        self.doctor_id = doctor_id
        self.slot_id = slot_id


class SessionError(UserManagementException):
    """Raised when session management fails."""
    
    def __init__(self, message: str, session_id: Optional[UUID] = None):
        super().__init__(message, "SESSION_ERROR")
        self.session_id = session_id


class IntegrationError(UserManagementException):
    """Raised when external service integration fails."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, 
                 status_code: Optional[int] = None):
        super().__init__(message, "INTEGRATION_ERROR")
        self.service_name = service_name
        self.status_code = status_code


class RepositoryError(UserManagementException):
    """Raised when repository operations fail."""
    
    def __init__(self, message: str, entity_type: Optional[str] = None, 
                 entity_id: Optional[UUID] = None):
        super().__init__(message, "REPOSITORY_ERROR")
        self.entity_type = entity_type
        self.entity_id = entity_id


class NotFoundError(UserManagementException):
    """Raised when requested entity is not found."""
    
    def __init__(self, message: str, entity_type: Optional[str] = None, 
                 entity_id: Optional[UUID] = None):
        super().__init__(message, "NOT_FOUND_ERROR")
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateError(UserManagementException):
    """Raised when duplicate entity creation is attempted."""
    
    def __init__(self, message: str, entity_type: Optional[str] = None, 
                 field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message, "DUPLICATE_ERROR")
        self.entity_type = entity_type
        self.field = field
        self.value = value


class PermissionError(UserManagementException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str, user_id: Optional[UUID] = None, 
                 required_permission: Optional[str] = None):
        super().__init__(message, "PERMISSION_ERROR")
        self.user_id = user_id
        self.required_permission = required_permission


class ConcurrencyError(UserManagementException):
    """Raised when concurrent modification conflicts occur."""
    
    def __init__(self, message: str, entity_type: Optional[str] = None, 
                 entity_id: Optional[UUID] = None):
        super().__init__(message, "CONCURRENCY_ERROR")
        self.entity_type = entity_type
        self.entity_id = entity_id


class ConfigurationError(UserManagementException):
    """Raised when service configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key