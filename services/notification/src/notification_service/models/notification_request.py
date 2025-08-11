"""Notification request domain model."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..enums import NotificationType, RecipientType, Priority, RequestStatus
from ..utils.helpers import generate_uuid, get_current_datetime, generate_correlation_id
from ..utils.validation import validate_request_data, ValidationResult
from ..exceptions import ValidationError


@dataclass
class NotificationRequest:
    """Request for creating notifications from external services."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Request Information
    request_id: str = field(default_factory=lambda: f"req_{generate_uuid()[:12]}")
    source_service: str = ""
    correlation_id: str = field(default_factory=generate_correlation_id)
    
    # Notification Details
    notification_type: NotificationType = NotificationType.APPOINTMENT_REMINDER
    recipient_email: str = ""
    recipient_name: str = ""
    recipient_type: RecipientType = RecipientType.PATIENT
    
    # Template and Content
    template_name: str = ""
    template_variables: Dict[str, Any] = field(default_factory=dict)
    
    # Scheduling
    priority: Priority = Priority.NORMAL
    scheduled_time: Optional[datetime] = None
    
    # Processing Status
    status: RequestStatus = RequestStatus.RECEIVED
    processed_at: Optional[datetime] = None
    notification_id: Optional[str] = None
    
    # Error Handling
    validation_errors: List[str] = field(default_factory=list)
    processing_error: Optional[str] = None
    
    # System Fields
    created_at: datetime = field(default_factory=get_current_datetime)
    updated_at: datetime = field(default_factory=get_current_datetime)
    
    def __post_init__(self):
        """Validate data after initialization."""
        self.validate()
    
    def validate(self) -> ValidationResult:
        """Validate request data."""
        data = self.to_dict()
        result = validate_request_data(data)
        
        if not result.is_valid:
            self.validation_errors = result.errors
            raise ValidationError(f"Invalid request data: {', '.join(result.errors)}")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'source_service': self.source_service,
            'correlation_id': self.correlation_id,
            'notification_type': self.notification_type.value if isinstance(self.notification_type, NotificationType) else self.notification_type,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'recipient_type': self.recipient_type.value if isinstance(self.recipient_type, RecipientType) else self.recipient_type,
            'template_name': self.template_name,
            'template_variables': self.template_variables,
            'priority': self.priority.value if isinstance(self.priority, Priority) else self.priority,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'status': self.status.value if isinstance(self.status, RequestStatus) else self.status,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'notification_id': self.notification_id,
            'validation_errors': self.validation_errors,
            'processing_error': self.processing_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationRequest':
        """Create from dictionary."""
        # Convert enums
        if 'notification_type' in data and isinstance(data['notification_type'], str):
            data['notification_type'] = NotificationType(data['notification_type'])
        if 'recipient_type' in data and isinstance(data['recipient_type'], str):
            data['recipient_type'] = RecipientType(data['recipient_type'])
        if 'priority' in data and isinstance(data['priority'], str):
            data['priority'] = Priority(data['priority'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = RequestStatus(data['status'])
        
        # Convert datetime strings
        datetime_fields = ['scheduled_time', 'processed_at', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    data[field_name] = None
        
        return cls(**data)
    
    def update_status(self, new_status: RequestStatus, error: str = None) -> None:
        """Update request status."""
        self.status = new_status
        self.updated_at = get_current_datetime()
        
        if new_status == RequestStatus.PROCESSED:
            self.processed_at = get_current_datetime()
        elif new_status == RequestStatus.FAILED and error:
            self.processing_error = error
    
    def link_notification(self, notification_id: str) -> None:
        """Link to created notification."""
        self.notification_id = notification_id
        self.updated_at = get_current_datetime()
    
    def is_processed(self) -> bool:
        """Check if request has been processed."""
        return self.status == RequestStatus.PROCESSED
    
    def is_failed(self) -> bool:
        """Check if request failed."""
        return self.status == RequestStatus.FAILED
    
    def is_immediate(self) -> bool:
        """Check if request is for immediate delivery."""
        return self.scheduled_time is None
    
    def is_scheduled(self) -> bool:
        """Check if request is scheduled for future delivery."""
        return self.scheduled_time is not None and self.scheduled_time > get_current_datetime()