"""Enumeration definitions for notification service components."""

from enum import Enum


class NotificationType(Enum):
    """Types of notifications that can be sent."""
    REGISTRATION_CONFIRMATION = "registration_confirmation"
    APPOINTMENT_BOOKING = "appointment_booking"
    APPOINTMENT_REMINDER = "appointment_reminder"
    RESCHEDULE_REQUEST = "reschedule_request"
    RESCHEDULE_CONFIRMATION = "reschedule_confirmation"
    SYSTEM_ALERT = "system_alert"


class RecipientType(Enum):
    """Types of notification recipients."""
    DOCTOR = "doctor"
    PATIENT = "patient"
    ADMIN = "admin"


class Priority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Status of notification delivery."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class TemplateFormat(Enum):
    """Format types for email templates."""
    HTML = "html"
    TEXT = "text"
    MIXED = "mixed"


class TemplateStatus(Enum):
    """Status of email templates."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class QueueType(Enum):
    """Types of notification queues."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


class QueueStatus(Enum):
    """Status of items in notification queue."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class DeliveryStatusEnum(Enum):
    """Delivery status for notifications."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    REJECTED = "rejected"


class BounceType(Enum):
    """Types of email bounces."""
    HARD = "hard"
    SOFT = "soft"
    COMPLAINT = "complaint"
    NULL = "null"


class RequestStatus(Enum):
    """Status of notification requests."""
    RECEIVED = "received"
    VALIDATED = "validated"
    QUEUED = "queued"
    PROCESSED = "processed"
    FAILED = "failed"


class ProviderType(Enum):
    """Types of email service providers."""
    AWS_SES = "aws_ses"
    SENDGRID = "sendgrid"
    SMTP = "smtp"
    MAILGUN = "mailgun"


class IntegrationStatus(Enum):
    """Status of email service integrations."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


class HealthStatus(Enum):
    """Health status of services."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class WebhookType(Enum):
    """Types of webhooks."""
    DELIVERY_STATUS = "delivery_status"
    BOUNCE = "bounce"
    COMPLAINT = "complaint"
    UNSUBSCRIBE = "unsubscribe"


class HttpMethod(Enum):
    """HTTP methods for webhooks."""
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"


class AuthenticationType(Enum):
    """Authentication types for webhooks."""
    NONE = "none"
    API_KEY = "api_key"
    SIGNATURE = "signature"
    OAUTH = "oauth"


class WebhookStatus(Enum):
    """Status of webhook processing."""
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"


class EventStatus(Enum):
    """Status of notification events."""
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"


class SchedulerType(Enum):
    """Types of reminder schedulers."""
    APPOINTMENT_REMINDER = "appointment_reminder"
    SYSTEM_MAINTENANCE = "system_maintenance"
    CUSTOM = "custom"


class SchedulerStatus(Enum):
    """Status of reminder schedulers."""
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    DISABLED = "disabled"


class RendererStatus(Enum):
    """Status of template rendering."""
    PENDING = "pending"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class OutputFormat(Enum):
    """Output format for template rendering."""
    HTML = "html"
    TEXT = "text"
    MIXED = "mixed"


class RetryType(Enum):
    """Types of retry operations."""
    NOTIFICATION_DELIVERY = "notification_delivery"
    TEMPLATE_RENDERING = "template_rendering"
    WEBHOOK_PROCESSING = "webhook_processing"


class BackoffStrategy(Enum):
    """Backoff strategies for retries."""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


class RetryStatus(Enum):
    """Status of retry operations."""
    PENDING = "pending"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXHAUSTED = "exhausted"


class ProcessorType(Enum):
    """Types of notification processors."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"


class ProcessorStatus(Enum):
    """Status of notification processors."""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"


class AggregationLevel(Enum):
    """Aggregation levels for analytics."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportType(Enum):
    """Types of delivery reports."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE = "performance"


class ReportStatus(Enum):
    """Status of report generation."""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ApprovalStatus(Enum):
    """Approval status for template management."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ManagementStatus(Enum):
    """Status of template management operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperationType(Enum):
    """Types of template management operations."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    VERSION = "version"


class AccessLevel(Enum):
    """Access levels for reports."""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"


class DigestFrequency(Enum):
    """Frequency for digest notifications."""
    DAILY = "daily"
    WEEKLY = "weekly"
    NEVER = "never"


class EmailFormat(Enum):
    """Email format preferences."""
    HTML = "html"
    TEXT = "text"
    MIXED = "mixed"