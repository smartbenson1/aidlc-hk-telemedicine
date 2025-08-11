"""
Enums for the Appointment Matching Service.
"""

from enum import Enum


class UserStatus(Enum):
    """Status for users (doctors and patients)."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class SpecialtyStatus(Enum):
    """Status for medical specialties."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class AvailabilityStatus(Enum):
    """Status for doctor availability slots."""
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"


class AppointmentType(Enum):
    """Type of appointment."""
    TELEMEDICINE = "telemedicine"
    IN_PERSON = "in_person"


class AppointmentStatus(Enum):
    """Status of appointments."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"


class EventStatus(Enum):
    """Status for events."""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class CircuitBreakerState(Enum):
    """Circuit breaker states for integration components."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"