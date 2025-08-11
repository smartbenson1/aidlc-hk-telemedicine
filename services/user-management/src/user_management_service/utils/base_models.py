"""
Base models and data classes for the User Management Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from .enums import UserStatus, UserType, ErrorSeverity


@dataclass
class BaseEntity:
    """Base entity with common fields."""
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    def update_timestamp(self, updated_by: Optional[UUID] = None) -> None:
        """Update the timestamp and updated_by fields."""
        self.updated_at = datetime.utcnow()
        if updated_by:
            self.updated_by = updated_by


@dataclass
class ServiceResult:
    """Generic service operation result."""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, data: Any = None) -> 'ServiceResult':
        """Create a successful result."""
        return cls(success=True, data=data)
    
    @classmethod
    def error_result(cls, error_message: str, error_code: Optional[str] = None, 
                    details: Optional[Dict[str, Any]] = None) -> 'ServiceResult':
        """Create an error result."""
        return cls(
            success=False,
            error_message=error_message,
            error_code=error_code,
            details=details
        )


@dataclass
class EmailResult:
    """Result of email sending operation."""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    recipient: Optional[str] = None
    sent_at: Optional[datetime] = None


@dataclass
class ConflictCheckResult:
    """Result of appointment conflict check."""
    has_conflict: bool
    conflicting_appointments: List[Dict[str, Any]] = field(default_factory=list)
    message: Optional[str] = None


@dataclass
class SessionData:
    """User session data."""
    user_name: str
    user_email: str
    permissions: List[str] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)


@dataclass
class SessionValidationResult:
    """Result of session validation."""
    is_valid: bool
    user_id: Optional[UUID] = None
    user_type: Optional[UserType] = None
    error_message: Optional[str] = None


@dataclass
class ProfileChanges:
    """Tracks changes made to a user profile."""
    changed_fields: List[str] = field(default_factory=list)
    previous_values: Dict[str, Any] = field(default_factory=dict)
    new_values: Dict[str, Any] = field(default_factory=dict)
    
    def add_change(self, field_name: str, old_value: Any, new_value: Any) -> None:
        """Add a field change."""
        self.changed_fields.append(field_name)
        self.previous_values[field_name] = old_value
        self.new_values[field_name] = new_value


@dataclass
class AvailabilityChanges:
    """Tracks changes made to doctor availability."""
    change_type: str  # added, modified, removed
    availability_id: UUID
    previous_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None


@dataclass
class EmailTemplate:
    """Email template data."""
    name: str
    subject: str
    body: str
    variables: List[str] = field(default_factory=list)


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for external service calls."""
    is_open: bool = False
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    success_count: int = 0
    
    def record_success(self) -> None:
        """Record a successful operation."""
        self.success_count += 1
        self.failure_count = 0
        if self.is_open and self.success_count >= 3:
            self.is_open = False
    
    def record_failure(self) -> None:
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= 5:
            self.is_open = True
            self.success_count = 0


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


@dataclass
class SystemError:
    """System error tracking."""
    id: UUID = field(default_factory=uuid4)
    error_code: str = ""
    error_message: str = ""
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    service_name: str = ""
    component_name: str = ""
    user_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    is_retryable: bool = False
    retry_count: int = 0
    max_retries: int = 3
    resolved: bool = False