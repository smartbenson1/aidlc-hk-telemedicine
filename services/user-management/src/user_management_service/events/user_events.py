"""
Event models for the User Management Service.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from ..utils.base_models import BaseEntity
from ..utils.enums import UserType, EventStatus, ChangeType


@dataclass
class UserRegistrationEvent(BaseEntity):
    """Event for user registration."""
    
    # Event Identity
    event_type: str = "user_registered"
    
    # User Information
    user_id: UUID = None
    user_type: UserType = UserType.PATIENT
    email: str = ""
    name: str = ""
    
    # Event Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_service: str = "user-management"
    correlation_id: UUID = field(default_factory=uuid4)
    
    # Processing Status
    status: EventStatus = EventStatus.PENDING
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"UserRegistrationEvent(user_id={self.user_id}, user_type={self.user_type.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the event."""
        return (f"UserRegistrationEvent(id={self.id}, user_id={self.user_id}, "
                f"user_type={self.user_type.value}, status={self.status.value})")
    
    def mark_processed(self) -> None:
        """Mark the event as processed."""
        self.status = EventStatus.PROCESSED
        self.processed_at = datetime.utcnow()
        self.update_timestamp()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark the event as failed."""
        self.status = EventStatus.FAILED
        self.error_message = error_message
        self.update_timestamp()
    
    def is_pending(self) -> bool:
        """Check if the event is pending."""
        return self.status == EventStatus.PENDING
    
    def is_processed(self) -> bool:
        """Check if the event is processed."""
        return self.status == EventStatus.PROCESSED
    
    def is_failed(self) -> bool:
        """Check if the event failed."""
        return self.status == EventStatus.FAILED
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'user_id': str(self.user_id),
            'user_type': self.user_type.value,
            'email': self.email,
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'source_service': self.source_service,
            'correlation_id': str(self.correlation_id),
            'status': self.status.value,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserRegistrationEvent':
        """Create event from dictionary representation."""
        event = cls()
        event.id = UUID(data['id'])
        event.event_type = data['event_type']
        event.user_id = UUID(data['user_id'])
        event.user_type = UserType(data['user_type'])
        event.email = data['email']
        event.name = data['name']
        event.timestamp = datetime.fromisoformat(data['timestamp'])
        event.source_service = data['source_service']
        event.correlation_id = UUID(data['correlation_id'])
        event.status = EventStatus(data['status'])
        event.processed_at = datetime.fromisoformat(data['processed_at']) if data['processed_at'] else None
        event.error_message = data['error_message']
        event.created_at = datetime.fromisoformat(data['created_at'])
        event.updated_at = datetime.fromisoformat(data['updated_at'])
        event.created_by = UUID(data['created_by']) if data['created_by'] else None
        event.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        return event


@dataclass
class ProfileUpdateEvent(BaseEntity):
    """Event for profile updates."""
    
    # Event Identity
    event_type: str = "profile_updated"
    
    # User Information
    user_id: UUID = None
    user_type: UserType = UserType.PATIENT
    
    # Change Information
    changed_fields: List[str] = field(default_factory=list)
    previous_values: str = ""  # JSON string
    new_values: str = ""  # JSON string
    
    # Event Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_service: str = "user-management"
    correlation_id: UUID = field(default_factory=uuid4)
    updated_by: UUID = None
    
    # Processing Status
    status: EventStatus = EventStatus.PENDING
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"ProfileUpdateEvent(user_id={self.user_id}, fields={len(self.changed_fields)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the event."""
        return (f"ProfileUpdateEvent(id={self.id}, user_id={self.user_id}, "
                f"changed_fields={self.changed_fields}, status={self.status.value})")
    
    def set_changes(self, previous_values: Dict[str, Any], new_values: Dict[str, Any]) -> None:
        """Set the change information."""
        self.changed_fields = list(new_values.keys())
        self.previous_values = json.dumps(previous_values, default=str)
        self.new_values = json.dumps(new_values, default=str)
        self.update_timestamp()
    
    def get_previous_values(self) -> Dict[str, Any]:
        """Get previous values as dictionary."""
        try:
            return json.loads(self.previous_values) if self.previous_values else {}
        except json.JSONDecodeError:
            return {}
    
    def get_new_values(self) -> Dict[str, Any]:
        """Get new values as dictionary."""
        try:
            return json.loads(self.new_values) if self.new_values else {}
        except json.JSONDecodeError:
            return {}
    
    def mark_processed(self) -> None:
        """Mark the event as processed."""
        self.status = EventStatus.PROCESSED
        self.processed_at = datetime.utcnow()
        self.update_timestamp()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark the event as failed."""
        self.status = EventStatus.FAILED
        self.error_message = error_message
        self.update_timestamp()
    
    def is_pending(self) -> bool:
        """Check if the event is pending."""
        return self.status == EventStatus.PENDING
    
    def is_processed(self) -> bool:
        """Check if the event is processed."""
        return self.status == EventStatus.PROCESSED
    
    def is_failed(self) -> bool:
        """Check if the event failed."""
        return self.status == EventStatus.FAILED
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'user_id': str(self.user_id),
            'user_type': self.user_type.value,
            'changed_fields': self.changed_fields,
            'previous_values': self.previous_values,
            'new_values': self.new_values,
            'timestamp': self.timestamp.isoformat(),
            'source_service': self.source_service,
            'correlation_id': str(self.correlation_id),
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'status': self.status.value,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by_system': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProfileUpdateEvent':
        """Create event from dictionary representation."""
        event = cls()
        event.id = UUID(data['id'])
        event.event_type = data['event_type']
        event.user_id = UUID(data['user_id'])
        event.user_type = UserType(data['user_type'])
        event.changed_fields = data['changed_fields']
        event.previous_values = data['previous_values']
        event.new_values = data['new_values']
        event.timestamp = datetime.fromisoformat(data['timestamp'])
        event.source_service = data['source_service']
        event.correlation_id = UUID(data['correlation_id'])
        event.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        event.status = EventStatus(data['status'])
        event.processed_at = datetime.fromisoformat(data['processed_at']) if data['processed_at'] else None
        event.error_message = data['error_message']
        event.created_at = datetime.fromisoformat(data['created_at'])
        event.updated_at = datetime.fromisoformat(data['updated_at'])
        event.created_by = UUID(data['created_by']) if data['created_by'] else None
        return event


@dataclass
class AvailabilityUpdateEvent(BaseEntity):
    """Event for availability updates."""
    
    # Event Identity
    event_type: str = "availability_updated"
    
    # Doctor and Availability Information
    doctor_id: UUID = None
    availability_id: UUID = None
    
    # Change Information
    change_type: ChangeType = ChangeType.MODIFIED
    previous_availability: str = ""  # JSON string
    new_availability: str = ""  # JSON string
    
    # Event Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_service: str = "user-management"
    correlation_id: UUID = field(default_factory=uuid4)
    updated_by: UUID = None
    
    # Processing Status
    status: EventStatus = EventStatus.PENDING
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"AvailabilityUpdateEvent(doctor_id={self.doctor_id}, change_type={self.change_type.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the event."""
        return (f"AvailabilityUpdateEvent(id={self.id}, doctor_id={self.doctor_id}, "
                f"availability_id={self.availability_id}, change_type={self.change_type.value})")
    
    def set_availability_data(self, previous_data: Optional[Dict[str, Any]], 
                            new_data: Optional[Dict[str, Any]]) -> None:
        """Set the availability change data."""
        self.previous_availability = json.dumps(previous_data, default=str) if previous_data else ""
        self.new_availability = json.dumps(new_data, default=str) if new_data else ""
        self.update_timestamp()
    
    def get_previous_availability(self) -> Optional[Dict[str, Any]]:
        """Get previous availability data as dictionary."""
        try:
            return json.loads(self.previous_availability) if self.previous_availability else None
        except json.JSONDecodeError:
            return None
    
    def get_new_availability(self) -> Optional[Dict[str, Any]]:
        """Get new availability data as dictionary."""
        try:
            return json.loads(self.new_availability) if self.new_availability else None
        except json.JSONDecodeError:
            return None
    
    def mark_processed(self) -> None:
        """Mark the event as processed."""
        self.status = EventStatus.PROCESSED
        self.processed_at = datetime.utcnow()
        self.update_timestamp()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark the event as failed."""
        self.status = EventStatus.FAILED
        self.error_message = error_message
        self.update_timestamp()
    
    def is_pending(self) -> bool:
        """Check if the event is pending."""
        return self.status == EventStatus.PENDING
    
    def is_processed(self) -> bool:
        """Check if the event is processed."""
        return self.status == EventStatus.PROCESSED
    
    def is_failed(self) -> bool:
        """Check if the event failed."""
        return self.status == EventStatus.FAILED
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'doctor_id': str(self.doctor_id),
            'availability_id': str(self.availability_id),
            'change_type': self.change_type.value,
            'previous_availability': self.previous_availability,
            'new_availability': self.new_availability,
            'timestamp': self.timestamp.isoformat(),
            'source_service': self.source_service,
            'correlation_id': str(self.correlation_id),
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'status': self.status.value,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by_system': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AvailabilityUpdateEvent':
        """Create event from dictionary representation."""
        event = cls()
        event.id = UUID(data['id'])
        event.event_type = data['event_type']
        event.doctor_id = UUID(data['doctor_id'])
        event.availability_id = UUID(data['availability_id'])
        event.change_type = ChangeType(data['change_type'])
        event.previous_availability = data['previous_availability']
        event.new_availability = data['new_availability']
        event.timestamp = datetime.fromisoformat(data['timestamp'])
        event.source_service = data['source_service']
        event.correlation_id = UUID(data['correlation_id'])
        event.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        event.status = EventStatus(data['status'])
        event.processed_at = datetime.fromisoformat(data['processed_at']) if data['processed_at'] else None
        event.error_message = data['error_message']
        event.created_at = datetime.fromisoformat(data['created_at'])
        event.updated_at = datetime.fromisoformat(data['updated_at'])
        event.created_by = UUID(data['created_by']) if data['created_by'] else None
        return event