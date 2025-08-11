"""Custom exception classes for notification service operations."""


class NotificationServiceError(Exception):
    """Base exception for all notification service errors."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationError(NotificationServiceError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, value=None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class NotificationNotFoundError(NotificationServiceError):
    """Raised when a notification is not found."""
    
    def __init__(self, notification_id: str):
        super().__init__(f"Notification not found: {notification_id}", "NOTIFICATION_NOT_FOUND")
        self.notification_id = notification_id


class TemplateNotFoundError(NotificationServiceError):
    """Raised when an email template is not found."""
    
    def __init__(self, template_name: str):
        super().__init__(f"Template not found: {template_name}", "TEMPLATE_NOT_FOUND")
        self.template_name = template_name


class TemplateRenderingError(NotificationServiceError):
    """Raised when template rendering fails."""
    
    def __init__(self, template_name: str, error_details: str):
        super().__init__(f"Template rendering failed for {template_name}: {error_details}", "TEMPLATE_RENDERING_ERROR")
        self.template_name = template_name
        self.error_details = error_details


class DeliveryError(NotificationServiceError):
    """Raised when notification delivery fails."""
    
    def __init__(self, notification_id: str, provider: str, error_details: str):
        super().__init__(f"Delivery failed for notification {notification_id} via {provider}: {error_details}", "DELIVERY_ERROR")
        self.notification_id = notification_id
        self.provider = provider
        self.error_details = error_details


class QueueError(NotificationServiceError):
    """Raised when queue operations fail."""
    
    def __init__(self, queue_name: str, operation: str, error_details: str):
        super().__init__(f"Queue operation '{operation}' failed for queue '{queue_name}': {error_details}", "QUEUE_ERROR")
        self.queue_name = queue_name
        self.operation = operation
        self.error_details = error_details


class RetryExhaustedError(NotificationServiceError):
    """Raised when retry attempts are exhausted."""
    
    def __init__(self, entity_id: str, entity_type: str, max_attempts: int):
        super().__init__(f"Retry attempts exhausted for {entity_type} {entity_id} after {max_attempts} attempts", "RETRY_EXHAUSTED")
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.max_attempts = max_attempts


class WebhookProcessingError(NotificationServiceError):
    """Raised when webhook processing fails."""
    
    def __init__(self, webhook_id: str, provider: str, error_details: str):
        super().__init__(f"Webhook processing failed for {webhook_id} from {provider}: {error_details}", "WEBHOOK_PROCESSING_ERROR")
        self.webhook_id = webhook_id
        self.provider = provider
        self.error_details = error_details


class SchedulerError(NotificationServiceError):
    """Raised when scheduler operations fail."""
    
    def __init__(self, scheduler_name: str, operation: str, error_details: str):
        super().__init__(f"Scheduler operation '{operation}' failed for '{scheduler_name}': {error_details}", "SCHEDULER_ERROR")
        self.scheduler_name = scheduler_name
        self.operation = operation
        self.error_details = error_details


class IntegrationError(NotificationServiceError):
    """Raised when external service integration fails."""
    
    def __init__(self, provider: str, operation: str, error_details: str):
        super().__init__(f"Integration error with {provider} during {operation}: {error_details}", "INTEGRATION_ERROR")
        self.provider = provider
        self.operation = operation
        self.error_details = error_details


class AnalyticsError(NotificationServiceError):
    """Raised when analytics operations fail."""
    
    def __init__(self, operation: str, error_details: str):
        super().__init__(f"Analytics operation '{operation}' failed: {error_details}", "ANALYTICS_ERROR")
        self.operation = operation
        self.error_details = error_details


class ReportGenerationError(NotificationServiceError):
    """Raised when report generation fails."""
    
    def __init__(self, report_type: str, error_details: str):
        super().__init__(f"Report generation failed for {report_type}: {error_details}", "REPORT_GENERATION_ERROR")
        self.report_type = report_type
        self.error_details = error_details


class UserPreferenceError(NotificationServiceError):
    """Raised when user preference operations fail."""
    
    def __init__(self, user_id: str, operation: str, error_details: str):
        super().__init__(f"User preference operation '{operation}' failed for user {user_id}: {error_details}", "USER_PREFERENCE_ERROR")
        self.user_id = user_id
        self.operation = operation
        self.error_details = error_details