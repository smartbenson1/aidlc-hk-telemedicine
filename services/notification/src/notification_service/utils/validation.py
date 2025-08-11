"""Validation utilities for notification service data."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .helpers import validate_email, validate_phone, validate_url, sanitize_string
from ..enums import (
    NotificationType, RecipientType, Priority, NotificationStatus,
    TemplateFormat, TemplateStatus, QueueType, QueueStatus,
    DeliveryStatusEnum, BounceType, RequestStatus, ProviderType,
    IntegrationStatus, HealthStatus, WebhookType, HttpMethod,
    AuthenticationType, WebhookStatus, EventStatus, SchedulerType,
    SchedulerStatus, RendererStatus, OutputFormat, RetryType,
    BackoffStrategy, RetryStatus, ProcessorType, ProcessorStatus,
    AggregationLevel, ReportType, ReportStatus, ApprovalStatus,
    ManagementStatus, OperationType, AccessLevel, DigestFrequency,
    EmailFormat
)


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


def validate_string_length(value: str, field_name: str, max_length: int, required: bool = True) -> List[str]:
    """Validate string length constraints."""
    errors = []
    
    if required and not value:
        errors.append(f"{field_name} is required")
    elif value and len(value) > max_length:
        errors.append(f"{field_name} exceeds maximum length of {max_length} characters")
    
    return errors


def validate_enum_value(value: Any, enum_class: type, field_name: str, required: bool = True) -> List[str]:
    """Validate enum value."""
    errors = []
    
    if required and value is None:
        errors.append(f"{field_name} is required")
    elif value is not None:
        try:
            if isinstance(value, str):
                enum_class(value)
            elif not isinstance(value, enum_class):
                errors.append(f"{field_name} must be a valid {enum_class.__name__} value")
        except ValueError:
            errors.append(f"{field_name} must be a valid {enum_class.__name__} value")
    
    return errors


def validate_json_data(value: Any, field_name: str, required: bool = True) -> List[str]:
    """Validate JSON data."""
    errors = []
    
    if required and value is None:
        errors.append(f"{field_name} is required")
    elif value is not None:
        try:
            if isinstance(value, str):
                json.loads(value)
            elif not isinstance(value, (dict, list)):
                errors.append(f"{field_name} must be valid JSON data")
        except json.JSONDecodeError:
            errors.append(f"{field_name} must be valid JSON")
    
    return errors


def validate_notification_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate notification data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('recipient_email'), 'recipient_email', 255))
    errors.extend(validate_string_length(data.get('recipient_name'), 'recipient_name', 100))
    errors.extend(validate_string_length(data.get('subject'), 'subject', 200))
    errors.extend(validate_string_length(data.get('body'), 'body', 5000))
    errors.extend(validate_string_length(data.get('template_name'), 'template_name', 100))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('recipient_type'), RecipientType, 'recipient_type'))
    errors.extend(validate_enum_value(data.get('notification_type'), NotificationType, 'notification_type'))
    errors.extend(validate_enum_value(data.get('priority'), Priority, 'priority'))
    errors.extend(validate_enum_value(data.get('status'), NotificationStatus, 'status', required=False))
    
    # Email validation
    if data.get('recipient_email') and not validate_email(data['recipient_email']):
        errors.append('recipient_email must be a valid email address')
    
    # JSON validation
    errors.extend(validate_json_data(data.get('template_variables'), 'template_variables'))
    
    # Retry count validation
    retry_count = data.get('retry_count', 0)
    if not isinstance(retry_count, int) or retry_count < 0 or retry_count > 3:
        errors.append('retry_count must be an integer between 0 and 3')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_template_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate email template data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('template_name'), 'template_name', 100))
    errors.extend(validate_string_length(data.get('subject_template'), 'subject_template', 200))
    errors.extend(validate_string_length(data.get('body_template'), 'body_template', 10000))
    errors.extend(validate_string_length(data.get('version'), 'version', 20))
    
    # Optional fields
    errors.extend(validate_string_length(data.get('description'), 'description', 500, required=False))
    errors.extend(validate_string_length(data.get('css_styles'), 'css_styles', 5000, required=False))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('template_type'), NotificationType, 'template_type'))
    errors.extend(validate_enum_value(data.get('template_format'), TemplateFormat, 'template_format'))
    errors.extend(validate_enum_value(data.get('status'), TemplateStatus, 'status', required=False))
    
    # List validations
    required_vars = data.get('required_variables', [])
    optional_vars = data.get('optional_variables', [])
    
    if not isinstance(required_vars, list):
        errors.append('required_variables must be a list')
    if not isinstance(optional_vars, list):
        errors.append('optional_variables must be a list')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_queue_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate notification queue data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('queue_name'), 'queue_name', 50))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('queue_type'), QueueType, 'queue_type'))
    errors.extend(validate_enum_value(data.get('priority'), Priority, 'priority'))
    errors.extend(validate_enum_value(data.get('status'), QueueStatus, 'status', required=False))
    
    # Integer validations
    processing_attempts = data.get('processing_attempts', 0)
    max_attempts = data.get('max_attempts', 3)
    
    if not isinstance(processing_attempts, int) or processing_attempts < 0:
        errors.append('processing_attempts must be a non-negative integer')
    
    if not isinstance(max_attempts, int) or max_attempts < 1 or max_attempts > 10:
        errors.append('max_attempts must be an integer between 1 and 10')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_delivery_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate delivery status data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('delivery_provider'), 'delivery_provider', 50))
    errors.extend(validate_string_length(data.get('recipient_email'), 'recipient_email', 255))
    
    # Optional fields
    errors.extend(validate_string_length(data.get('provider_message_id'), 'provider_message_id', 100, required=False))
    errors.extend(validate_string_length(data.get('response_code'), 'response_code', 10, required=False))
    errors.extend(validate_string_length(data.get('response_message'), 'response_message', 500, required=False))
    errors.extend(validate_string_length(data.get('bounce_reason'), 'bounce_reason', 500, required=False))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('status'), DeliveryStatusEnum, 'status'))
    errors.extend(validate_enum_value(data.get('bounce_type'), BounceType, 'bounce_type', required=False))
    
    # Email validation
    if data.get('recipient_email') and not validate_email(data['recipient_email']):
        errors.append('recipient_email must be a valid email address')
    
    # Integer validation
    delivery_attempt = data.get('delivery_attempt', 1)
    if not isinstance(delivery_attempt, int) or delivery_attempt < 1:
        errors.append('delivery_attempt must be a positive integer')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_request_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate notification request data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('request_id'), 'request_id', 100))
    errors.extend(validate_string_length(data.get('source_service'), 'source_service', 50))
    errors.extend(validate_string_length(data.get('recipient_email'), 'recipient_email', 255))
    errors.extend(validate_string_length(data.get('recipient_name'), 'recipient_name', 100))
    errors.extend(validate_string_length(data.get('template_name'), 'template_name', 100))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('notification_type'), NotificationType, 'notification_type'))
    errors.extend(validate_enum_value(data.get('recipient_type'), RecipientType, 'recipient_type'))
    errors.extend(validate_enum_value(data.get('priority'), Priority, 'priority'))
    errors.extend(validate_enum_value(data.get('status'), RequestStatus, 'status', required=False))
    
    # Email validation
    if data.get('recipient_email') and not validate_email(data['recipient_email']):
        errors.append('recipient_email must be a valid email address')
    
    # JSON validation
    errors.extend(validate_json_data(data.get('template_variables'), 'template_variables'))
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_integration_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate email service integration data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('provider_name'), 'provider_name', 50))
    errors.extend(validate_string_length(data.get('from_email'), 'from_email', 255))
    errors.extend(validate_string_length(data.get('from_name'), 'from_name', 100))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('provider_type'), ProviderType, 'provider_type'))
    errors.extend(validate_enum_value(data.get('status'), IntegrationStatus, 'status', required=False))
    errors.extend(validate_enum_value(data.get('health_check_status'), HealthStatus, 'health_check_status', required=False))
    
    # Email validations
    if data.get('from_email') and not validate_email(data['from_email']):
        errors.append('from_email must be a valid email address')
    
    if data.get('reply_to_email') and not validate_email(data['reply_to_email']):
        errors.append('reply_to_email must be a valid email address')
    
    # URL validation
    if data.get('api_endpoint') and not validate_url(data['api_endpoint']):
        errors.append('api_endpoint must be a valid URL')
    
    # Rate limit validations
    rate_limits = ['rate_limit_per_second', 'rate_limit_per_hour', 'rate_limit_per_day']
    for limit_field in rate_limits:
        limit_value = data.get(limit_field)
        if limit_value is not None and (not isinstance(limit_value, int) or limit_value < 1):
            errors.append(f'{limit_field} must be a positive integer')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_webhook_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate webhook handler data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('request_id'), 'request_id', 100))
    errors.extend(validate_string_length(data.get('provider_name'), 'provider_name', 50))
    errors.extend(validate_string_length(data.get('webhook_url'), 'webhook_url', 500))
    errors.extend(validate_string_length(data.get('content_type'), 'content_type', 100))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('webhook_type'), WebhookType, 'webhook_type'))
    errors.extend(validate_enum_value(data.get('http_method'), HttpMethod, 'http_method'))
    errors.extend(validate_enum_value(data.get('authentication_type'), AuthenticationType, 'authentication_type'))
    errors.extend(validate_enum_value(data.get('status'), WebhookStatus, 'status', required=False))
    
    # URL validation
    if data.get('webhook_url') and not validate_url(data['webhook_url']):
        errors.append('webhook_url must be a valid URL')
    
    # JSON validations
    errors.extend(validate_json_data(data.get('request_body'), 'request_body'))
    errors.extend(validate_json_data(data.get('request_headers'), 'request_headers', required=False))
    errors.extend(validate_json_data(data.get('authentication_config'), 'authentication_config', required=False))
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_event_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate notification event data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('event_type'), 'event_type', 100))
    errors.extend(validate_string_length(data.get('source_service'), 'source_service', 50))
    errors.extend(validate_string_length(data.get('source_entity_type'), 'source_entity_type', 50))
    errors.extend(validate_string_length(data.get('template_name'), 'template_name', 100))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('notification_type'), NotificationType, 'notification_type'))
    errors.extend(validate_enum_value(data.get('status'), EventStatus, 'status', required=False))
    
    # JSON validation
    errors.extend(validate_json_data(data.get('event_data'), 'event_data'))
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_scheduler_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate reminder scheduler data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('scheduler_name'), 'scheduler_name', 100))
    errors.extend(validate_string_length(data.get('cron_expression'), 'cron_expression', 100))
    errors.extend(validate_string_length(data.get('timezone'), 'timezone', 50))
    errors.extend(validate_string_length(data.get('reminder_template'), 'reminder_template', 100))
    errors.extend(validate_string_length(data.get('target_entity_type'), 'target_entity_type', 50))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('scheduler_type'), SchedulerType, 'scheduler_type'))
    errors.extend(validate_enum_value(data.get('status'), SchedulerStatus, 'status', required=False))
    
    # Integer validations
    reminder_offset = data.get('reminder_offset_hours')
    batch_size = data.get('batch_size', 100)
    
    if not isinstance(reminder_offset, int) or reminder_offset < 1:
        errors.append('reminder_offset_hours must be a positive integer')
    
    if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 1000:
        errors.append('batch_size must be an integer between 1 and 1000')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_renderer_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate template renderer data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('request_id'), 'request_id', 100))
    errors.extend(validate_string_length(data.get('template_name'), 'template_name', 100))
    
    # Optional fields
    errors.extend(validate_string_length(data.get('locale'), 'locale', 10, required=False))
    errors.extend(validate_string_length(data.get('timezone'), 'timezone', 50, required=False))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('output_format'), OutputFormat, 'output_format'))
    errors.extend(validate_enum_value(data.get('status'), RendererStatus, 'status', required=False))
    
    # JSON validation
    errors.extend(validate_json_data(data.get('template_variables'), 'template_variables'))
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_retry_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate retry handler data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('entity_type'), 'entity_type', 50))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('retry_type'), RetryType, 'retry_type'))
    errors.extend(validate_enum_value(data.get('backoff_strategy'), BackoffStrategy, 'backoff_strategy'))
    errors.extend(validate_enum_value(data.get('status'), RetryStatus, 'status', required=False))
    
    # Integer validations
    max_attempts = data.get('max_attempts')
    base_delay = data.get('base_delay_seconds')
    max_delay = data.get('max_delay_seconds')
    
    if not isinstance(max_attempts, int) or max_attempts < 1 or max_attempts > 10:
        errors.append('max_attempts must be an integer between 1 and 10')
    
    if not isinstance(base_delay, int) or base_delay < 1:
        errors.append('base_delay_seconds must be a positive integer')
    
    if not isinstance(max_delay, int) or max_delay < base_delay:
        errors.append('max_delay_seconds must be greater than or equal to base_delay_seconds')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_processor_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate notification processor data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('processor_name'), 'processor_name', 100))
    errors.extend(validate_string_length(data.get('source_queue'), 'source_queue', 100))
    errors.extend(validate_string_length(data.get('dead_letter_queue'), 'dead_letter_queue', 100))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('processor_type'), ProcessorType, 'processor_type'))
    errors.extend(validate_enum_value(data.get('status'), ProcessorStatus, 'status', required=False))
    
    # Integer validations
    batch_size = data.get('batch_size', 50)
    processing_interval = data.get('processing_interval_seconds', 30)
    max_concurrent = data.get('max_concurrent_jobs', 5)
    
    if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 500:
        errors.append('batch_size must be an integer between 1 and 500')
    
    if not isinstance(processing_interval, int) or processing_interval < 1:
        errors.append('processing_interval_seconds must be a positive integer')
    
    if not isinstance(max_concurrent, int) or max_concurrent < 1:
        errors.append('max_concurrent_jobs must be a positive integer')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_analytics_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate notification analytics data."""
    errors = []
    
    # Enum validation
    errors.extend(validate_enum_value(data.get('aggregation_level'), AggregationLevel, 'aggregation_level'))
    
    # Integer validations
    integer_fields = [
        'total_notifications', 'successful_deliveries', 'failed_deliveries',
        'bounced_emails', 'average_delivery_time_seconds', 'average_processing_time_ms'
    ]
    
    for field in integer_fields:
        value = data.get(field, 0)
        if not isinstance(value, int) or value < 0:
            errors.append(f'{field} must be a non-negative integer')
    
    # Decimal validation
    complaint_rate = data.get('complaint_rate', 0.0)
    if not isinstance(complaint_rate, (int, float)) or complaint_rate < 0.0 or complaint_rate > 1.0:
        errors.append('complaint_rate must be a decimal between 0.0 and 1.0')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_report_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate delivery report data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('report_name'), 'report_name', 100))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('report_type'), ReportType, 'report_type'))
    errors.extend(validate_enum_value(data.get('output_format'), OutputFormat, 'output_format'))
    errors.extend(validate_enum_value(data.get('access_level'), AccessLevel, 'access_level'))
    errors.extend(validate_enum_value(data.get('status'), ReportStatus, 'status', required=False))
    
    # JSON validations
    errors.extend(validate_json_data(data.get('filters'), 'filters', required=False))
    errors.extend(validate_json_data(data.get('report_data'), 'report_data', required=False))
    
    # List validation
    metrics = data.get('metrics', [])
    if not isinstance(metrics, list) or len(metrics) == 0:
        errors.append('metrics must be a non-empty list')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_preference_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate user preference data."""
    errors = []
    
    # Required fields
    errors.extend(validate_string_length(data.get('user_email'), 'user_email', 255))
    errors.extend(validate_string_length(data.get('timezone'), 'timezone', 50))
    
    # Enum validations
    errors.extend(validate_enum_value(data.get('user_type'), RecipientType, 'user_type'))
    errors.extend(validate_enum_value(data.get('digest_frequency'), DigestFrequency, 'digest_frequency', required=False))
    errors.extend(validate_enum_value(data.get('email_format'), EmailFormat, 'email_format', required=False))
    
    # Email validation
    if data.get('user_email') and not validate_email(data['user_email']):
        errors.append('user_email must be a valid email address')
    
    # Integer validations
    reminder_hours = data.get('reminder_hours_before', 24)
    max_emails = data.get('max_emails_per_day', 10)
    
    if not isinstance(reminder_hours, int) or reminder_hours < 1 or reminder_hours > 168:
        errors.append('reminder_hours_before must be an integer between 1 and 168')
    
    if not isinstance(max_emails, int) or max_emails < 1 or max_emails > 50:
        errors.append('max_emails_per_day must be an integer between 1 and 50')
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)