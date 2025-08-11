"""Notification queue domain model."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from ..enums import QueueType, QueueStatus, Priority
from ..utils.helpers import generate_uuid, get_current_datetime
from ..utils.validation import validate_queue_data, ValidationResult
from ..exceptions import ValidationError


@dataclass
class NotificationQueue:
    """Queue item for notification processing."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Queue Information
    queue_name: str = ""
    queue_type: QueueType = QueueType.IMMEDIATE
    
    # Notification Reference
    notification_id: str = ""
    
    # Processing Information
    priority: Priority = Priority.NORMAL
    scheduled_time: datetime = field(default_factory=get_current_datetime)
    processing_attempts: int = 0
    max_attempts: int = 3
    
    # Status and Timing
    status: QueueStatus = QueueStatus.QUEUED
    queued_at: datetime = field(default_factory=get_current_datetime)
    processing_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error Handling
    last_error: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    
    # System Fields
    created_at: datetime = field(default_factory=get_current_datetime)
    updated_at: datetime = field(default_factory=get_current_datetime)
    
    def __post_init__(self):
        """Validate data after initialization."""
        self.validate()
    
    def validate(self) -> ValidationResult:
        """Validate queue data."""
        data = self.to_dict()
        result = validate_queue_data(data)
        
        if not result.is_valid:
            raise ValidationError(f"Invalid queue data: {', '.join(result.errors)}")
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'queue_name': self.queue_name,
            'queue_type': self.queue_type.value if isinstance(self.queue_type, QueueType) else self.queue_type,
            'notification_id': self.notification_id,
            'priority': self.priority.value if isinstance(self.priority, Priority) else self.priority,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'processing_attempts': self.processing_attempts,
            'max_attempts': self.max_attempts,
            'status': self.status.value if isinstance(self.status, QueueStatus) else self.status,
            'queued_at': self.queued_at.isoformat() if self.queued_at else None,
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_error': self.last_error,
            'next_retry_at': self.next_retry_at.isoformat() if self.next_retry_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NotificationQueue':
        """Create from dictionary."""
        # Convert enums
        if 'queue_type' in data and isinstance(data['queue_type'], str):
            data['queue_type'] = QueueType(data['queue_type'])
        if 'priority' in data and isinstance(data['priority'], str):
            data['priority'] = Priority(data['priority'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = QueueStatus(data['status'])
        
        # Convert datetime strings
        datetime_fields = ['scheduled_time', 'queued_at', 'processing_started_at', 'completed_at', 'next_retry_at', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    data[field_name] = None
        
        return cls(**data)
    
    def start_processing(self) -> None:
        """Mark as processing started."""
        self.status = QueueStatus.PROCESSING
        self.processing_started_at = get_current_datetime()
        self.updated_at = get_current_datetime()
    
    def complete_processing(self) -> None:
        """Mark as completed."""
        self.status = QueueStatus.COMPLETED
        self.completed_at = get_current_datetime()
        self.updated_at = get_current_datetime()
    
    def fail_processing(self, error: str) -> None:
        """Mark as failed."""
        self.status = QueueStatus.FAILED
        self.last_error = error
        self.processing_attempts += 1
        self.updated_at = get_current_datetime()
    
    def can_retry(self) -> bool:
        """Check if can be retried."""
        return self.processing_attempts < self.max_attempts
    
    def is_ready_for_processing(self) -> bool:
        """Check if ready for processing."""
        if self.status != QueueStatus.QUEUED:
            return False
        
        current_time = get_current_datetime()
        scheduled_time = self.scheduled_time
        
        # Handle timezone-naive datetime comparison
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=current_time.tzinfo)
        
        return scheduled_time <= current_time