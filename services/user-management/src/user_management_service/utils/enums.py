"""
Common enums and constants for the User Management Service.
"""

from enum import Enum


class UserStatus(Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserType(Enum):
    """User type enumeration."""
    DOCTOR = "doctor"
    PATIENT = "patient"
    ADMIN = "admin"


class AppointmentType(Enum):
    """Appointment type enumeration."""
    TELEMEDICINE = "telemedicine"
    IN_PERSON = "in_person"


class AvailabilityStatus(Enum):
    """Doctor availability status enumeration."""
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"


class SessionStatus(Enum):
    """User session status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class EventStatus(Enum):
    """Event processing status enumeration."""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class ChangeType(Enum):
    """Change type for availability updates."""
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Constants
MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 255
MAX_PHONE_LENGTH = 15
MIN_PHONE_LENGTH = 10
MAX_LOCATION_LENGTH = 200
MAX_EXPERIENCE_LENGTH = 1000
MIN_EXPERIENCE_LENGTH = 10
MAX_MEDICAL_HISTORY_LENGTH = 2000
MAX_EMERGENCY_CONTACT_NAME_LENGTH = 100
MAX_EMERGENCY_CONTACT_RELATIONSHIP_LENGTH = 50

# Business Rules Constants
MAX_SPECIALTIES_PER_DOCTOR = 10
MIN_SPECIALTIES_PER_DOCTOR = 1
MAX_BOOKING_WINDOW_DAYS = 30
SLOT_DURATION_HOURS = 1
MAX_DAILY_SLOTS = 12
MAX_WEEKLY_SLOTS = 60
MAX_PROFILE_UPDATES_PER_DAY = 5
MAX_REGISTRATION_ATTEMPTS = 3
SESSION_TIMEOUT_HOURS = 24

# Validation Constants
VALID_EMERGENCY_CONTACT_RELATIONSHIPS = [
    "spouse", "parent", "child", "sibling", "friend", "other"
]

# Email Templates
EMAIL_TEMPLATES = {
    "doctor_registration": "doctor_registration_confirmation.html",
    "patient_registration": "patient_registration_confirmation.html",
    "profile_update": "profile_update_notification.html"
}

# Service Configuration
SERVICE_TIMEOUTS = {
    "email_service": 30,
    "admin_service": 30,
    "appointment_service": 30
}