"""Notification domain model (from shared model)."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from ..enums import NotificationType, RecipientType, Priority, NotificationStatus
from ..utils.helpers import generate_uuid, get_current_datetime, validate_email
from ..utils.validation import validate_notification_data, ValidationResult
from ..exceptions import ValidationError


@dataclass
class Notification:
    """
    Central notification entity for managing email notifications.
    Based on the shared model Notification component.
    """
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Recipient Information
    recipient_email: str = ""
    recipient_name: str = ""
    recipient_type: RecipientType = RecipientType.PATIENT
    
    # Notification Details
    notification_type: NotificationType = NotificationType.APPOINTMENT_REMINDER
    subject: str = ""
    body: str = ""
    
    # Template Information
    template_name: str = ""
    template_variables: Dict[str, Any] = field(default_factory=dict)
    
    # Scheduling and Delivery
    scheduled_time: Optional[datetime] = None
    priority: Priority = Priority.NORMAL
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    
    # System Fields
    created_at: datetime = field(default_factory=get_current_datetime)
    updated_at: datetime = field(default_factory=get_current_datetime)
    created_by: str = "system"
    updated_by: str = "system"
    
    def __post_init__(self):
        """Validate data after initialization."""
        self.validate()
    
    def validate(self) -> ValidationResult:
        """Validate notification data."""
        data = self.to_dict()
        result = validate_notification_data(data)
        
        if not result.is_valid:
            raise ValidationError(f"Invalid notification data: {', '.join(result.errors)}")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'recipient_type': self.recipient_type.value if isinstance(self.recipient_type, RecipientType) else self.recipient_type,
            'notification_type': self.notification_type.value if isinstance(self.notification_type, NotificationType) else self.notification_type,
            'subject': self.subject,
            'body': self.body,
            'template_name': self.template_name,
            'template_variables': self.template_variables,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'priority': self.priority.value if isinstance(self.priority, Priority) else self.priority,
            'status': self.status.value if isinstance(self.status, NotificationStatus) else self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'failure_reason': self.failure_reason,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create notification from dictionary."""
        # Convert enum strings back to enums
        if 'recipient_type' in data and isinstance(data['recipient_type'], str):
            data['recipient_type'] = RecipientType(data['recipient_type'])
        
        if 'notification_type' in data and isinstance(data['notification_type'], str):
            data['notification_type'] = NotificationType(data['notification_type'])
        
        if 'priority' in data and isinstance(data['priority'], str):
            data['priority'] = Priority(data['priority'])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = NotificationStatus(data['status'])
        
        # Convert datetime strings back to datetime objects
        datetime_fields = ['scheduled_time', 'sent_at', 'delivered_at', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    data[field_name] = None
        
        return cls(**data)
    
    def update_status(self, new_status: NotificationStatus, failure_reason: str = None) -> None:
        """Update notification status."""
        self.status = new_status
        self.updated_at = get_current_datetime()
        
        if new_status == NotificationStatus.SENT:
            self.sent_at = get_current_datetime()
        elif new_status == NotificationStatus.DELIVERED:
            self.delivered_at = get_current_datetime()
        elif new_status in [NotificationStatus.FAILED, NotificationStatus.BOUNCED]:
            self.failure_reason = failure_reason
    
    def increment_retry_count(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
        self.updated_at = get_current_datetime()
    
    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if notification can be retried."""
        return (self.retry_count < max_retries and 
                self.status in [NotificationStatus.FAILED, NotificationStatus.PENDING])
    
    def is_scheduled(self) -> bool:
        """Check if notification is scheduled for future delivery."""
        if not self.scheduled_time:
            return False
        
        current_time = get_current_datetime()
        scheduled_time = self.scheduled_time
        
        # Handle timezone-naive datetime comparison
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=current_time.tzinfo)
        
        return scheduled_time > current_time
    
    def is_due_for_delivery(self) -> bool:
        """Check if scheduled notification is due for delivery."""
        if not self.scheduled_time:
            return True  # Immediate delivery
        
        current_time = get_current_datetime()
        scheduled_time = self.scheduled_time
        
        # Handle timezone-naive datetime comparison
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=current_time.tzinfo)
        
        return scheduled_time <= current_time
    
    def get_template_variables_json(self) -> str:
        """Get template variables as JSON string."""
        return json.dumps(self.template_variables, default=str)
    
    def set_template_variables_from_json(self, json_str: str) -> None:
        """Set template variables from JSON string."""
        try:
            self.template_variables = json.loads(json_str)
        except json.JSONDecodeError:
            self.template_variables = {}
    
    def add_template_variable(self, key: str, value: Any) -> None:
        """Add a template variable."""
        self.template_variables[key] = value
        self.updated_at = get_current_datetime()
    
    def get_template_variable(self, key: str, default: Any = None) -> Any:
        """Get a template variable value."""
        return self.template_variables.get(key, default)
    
    def is_high_priority(self) -> bool:
        """Check if notification has high or urgent priority."""
        return self.priority in [Priority.HIGH, Priority.URGENT]
    
    def get_age_in_minutes(self) -> int:
        """Get age of notification in minutes."""
        if not self.created_at:
            return 0
        
        delta = get_current_datetime() - self.created_at
        return int(delta.total_seconds() / 60)
    
    def __str__(self) -> str:
        """String representation of notification."""
        return f"Notification(id={self.id}, type={self.notification_type.value}, recipient={self.recipient_email}, status={self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Notification(id='{self.id}', recipient_email='{self.recipient_email}', "
                f"notification_type={self.notification_type}, status={self.status}, "
                f"priority={self.priority}, retry_count={self.retry_count})")