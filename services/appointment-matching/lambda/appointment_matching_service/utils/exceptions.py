"""
Custom exception classes for the Appointment Matching Service.
"""


class AppointmentMatchingServiceError(Exception):
    """Base exception for all service errors."""
    pass


class ValidationError(AppointmentMatchingServiceError):
    """Raised when validation fails."""
    pass


class NotFoundError(AppointmentMatchingServiceError):
    """Raised when a requested resource is not found."""
    pass


class BusinessRuleError(AppointmentMatchingServiceError):
    """Raised when business rules are violated."""
    pass


class IntegrationError(AppointmentMatchingServiceError):
    """Raised when external service integration fails."""
    pass


class CircuitBreakerOpenError(IntegrationError):
    """Raised when circuit breaker is open."""
    pass


class BookingError(BusinessRuleError):
    """Raised when appointment booking fails."""
    pass


class RescheduleError(BusinessRuleError):
    """Raised when appointment rescheduling fails."""
    pass


class AnalysisError(AppointmentMatchingServiceError):
    """Raised when symptom analysis fails."""
    pass


class MatchingError(AppointmentMatchingServiceError):
    """Raised when doctor matching fails."""
    pass