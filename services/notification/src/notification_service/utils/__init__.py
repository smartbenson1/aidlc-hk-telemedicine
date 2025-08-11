"""Utility classes and helper functions for the notification service."""

from .helpers import (
    generate_uuid,
    get_current_datetime,
    format_datetime,
    parse_datetime,
    validate_email,
    validate_phone,
    validate_url,
    sanitize_string,
    truncate_string,
    calculate_retry_delay
)

from .validation import (
    ValidationResult,
    validate_notification_data,
    validate_template_data,
    validate_queue_data,
    validate_delivery_data,
    validate_request_data,
    validate_integration_data,
    validate_webhook_data,
    validate_event_data,
    validate_scheduler_data,
    validate_renderer_data,
    validate_retry_data,
    validate_processor_data,
    validate_analytics_data,
    validate_report_data,
    validate_preference_data
)

__all__ = [
    'generate_uuid',
    'get_current_datetime',
    'format_datetime',
    'parse_datetime',
    'validate_email',
    'validate_phone',
    'validate_url',
    'sanitize_string',
    'truncate_string',
    'calculate_retry_delay',
    'ValidationResult',
    'validate_notification_data',
    'validate_template_data',
    'validate_queue_data',
    'validate_delivery_data',
    'validate_request_data',
    'validate_integration_data',
    'validate_webhook_data',
    'validate_event_data',
    'validate_scheduler_data',
    'validate_renderer_data',
    'validate_retry_data',
    'validate_processor_data',
    'validate_analytics_data',
    'validate_report_data',
    'validate_preference_data'
]