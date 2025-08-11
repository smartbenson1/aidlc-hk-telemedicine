"""Delivery status domain model."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from ..enums import DeliveryStatusEnum, BounceType
from ..utils.helpers import generate_uuid, get_current_datetime
from ..utils.validation import validate_delivery_data, ValidationResult
from ..exceptions import ValidationError


@dataclass
class DeliveryStatus:
    """Tracks delivery status of notifications."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Notification Reference
    notification_id: str = ""
    
    # Delivery Information
    delivery_provider: str = ""
    provider_message_id: Optional[str] = None
    
    # Status Tracking
    status: DeliveryStatusEnum = DeliveryStatusEnum.PENDING
    status_timestamp: datetime = field(default_factory=get_current_datetime)
    
    # Delivery Details
    delivery_attempt: int = 1
    response_code: Optional[str] = None
    response_message: Optional[str] = None
    
    # Recipient Information
    recipient_email: str = ""
    bounce_type: Optional[BounceType] = None
    bounce_reason: Optional[str] = None
    
    # System Fields
    created_at: datetime = field(default_factory=get_current_datetime)
    updated_at: datetime = field(default_factory=get_current_datetime)
    
    def __post_init__(self):
        """Validate data after initialization."""
        self.validate()
    
    def validate(self) -> ValidationResult:
        """Validate delivery status data."""
        data = self.to_dict()
        result = validate_delivery_data(data)
        
        if not result.is_valid:
            raise ValidationError(f"Invalid delivery status data: {', '.join(result.errors)}")
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'delivery_provider': self.delivery_provider,
            'provider_message_id': self.provider_message_id,
            'status': self.status.value if isinstance(self.status, DeliveryStatusEnum) else self.status,
            'status_timestamp': self.status_timestamp.isoformat() if self.status_timestamp else None,
            'delivery_attempt': self.delivery_attempt,
            'response_code': self.response_code,
            'response_message': self.response_message,
            'recipient_email': self.recipient_email,
            'bounce_type': self.bounce_type.value if isinstance(self.bounce_type, BounceType) else self.bounce_type,
            'bounce_reason': self.bounce_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DeliveryStatus':
        """Create from dictionary."""
        # Convert enums
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = DeliveryStatusEnum(data['status'])
        if 'bounce_type' in data and isinstance(data['bounce_type'], str):
            data['bounce_type'] = BounceType(data['bounce_type'])
        
        # Convert datetime strings
        datetime_fields = ['status_timestamp', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    data[field_name] = None
        
        return cls(**data)
    
    def update_status(self, new_status: DeliveryStatusEnum, 
                     response_code: str = None, response_message: str = None) -> None:
        """Update delivery status."""
        self.status = new_status
        self.status_timestamp = get_current_datetime()
        self.updated_at = get_current_datetime()
        
        if response_code:
            self.response_code = response_code
        if response_message:
            self.response_message = response_message
    
    def record_bounce(self, bounce_type: BounceType, bounce_reason: str) -> None:
        """Record bounce information."""
        self.status = DeliveryStatusEnum.BOUNCED
        self.bounce_type = bounce_type
        self.bounce_reason = bounce_reason
        self.status_timestamp = get_current_datetime()
        self.updated_at = get_current_datetime()
    
    def is_successful(self) -> bool:
        """Check if delivery was successful."""
        return self.status == DeliveryStatusEnum.DELIVERED
    
    def is_failed(self) -> bool:
        """Check if delivery failed."""
        return self.status in [DeliveryStatusEnum.FAILED, DeliveryStatusEnum.BOUNCED, DeliveryStatusEnum.REJECTED]