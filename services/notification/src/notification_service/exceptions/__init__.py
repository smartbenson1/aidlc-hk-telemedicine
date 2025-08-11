"""Custom exception classes for the notification service."""

from .notification_exceptions import (
    NotificationServiceError,
    ValidationError,
    NotificationNotFoundError,
    TemplateNotFoundError,
    TemplateRenderingError,
    DeliveryError,
    QueueError,
    RetryExhaustedError,
    WebhookProcessingError,
    SchedulerError,
    IntegrationError,
    AnalyticsError,
    ReportGenerationError,
    UserPreferenceError
)

__all__ = [
    'NotificationServiceError',
    'ValidationError',
    'NotificationNotFoundError',
    'TemplateNotFoundError',
    'TemplateRenderingError',
    'DeliveryError',
    'QueueError',
    'RetryExhaustedError',
    'WebhookProcessingError',
    'SchedulerError',
    'IntegrationError',
    'AnalyticsError',
    'ReportGenerationError',
    'UserPreferenceError'
]