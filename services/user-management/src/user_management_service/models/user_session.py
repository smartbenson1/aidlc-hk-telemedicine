"""
User Session model for the User Management Service.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from ..utils.base_models import BaseEntity, SessionData
from ..utils.enums import UserType, SessionStatus, SESSION_TIMEOUT_HOURS


@dataclass
class UserSession(BaseEntity):
    """User Session entity model."""
    
    # Identity
    user_id: UUID = None
    user_type: UserType = UserType.PATIENT
    
    # Session Information
    last_accessed: datetime = None
    expires_at: datetime = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Session Status
    status: SessionStatus = SessionStatus.ACTIVE
    
    # Session Data (encrypted JSON)
    session_data: str = ""
    
    def __post_init__(self):
        """Initialize session after creation."""
        if self.last_accessed is None:
            self.last_accessed = self.created_at
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=SESSION_TIMEOUT_HOURS)
    
    def __str__(self) -> str:
        """String representation of the user session."""
        return f"Session for {self.user_id} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the user session."""
        return (f"UserSession(id={self.id}, user_id={self.user_id}, "
                f"user_type={self.user_type.value}, status={self.status.value})")
    
    def is_active(self) -> bool:
        """Check if the session is active."""
        return self.status == SessionStatus.ACTIVE and not self.is_expired()
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_terminated(self) -> bool:
        """Check if the session is terminated."""
        return self.status == SessionStatus.TERMINATED
    
    def update_access(self, ip_address: Optional[str] = None, 
                     user_agent: Optional[str] = None) -> None:
        """Update session access information."""
        self.last_accessed = datetime.utcnow()
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent
        self.update_timestamp()
    
    def refresh(self) -> None:
        """Refresh the session expiration time."""
        if self.is_active():
            self.expires_at = datetime.utcnow() + timedelta(hours=SESSION_TIMEOUT_HOURS)
            self.update_timestamp()
    
    def terminate(self) -> None:
        """Terminate the session."""
        self.status = SessionStatus.TERMINATED
        self.update_timestamp()
    
    def expire(self) -> None:
        """Mark the session as expired."""
        self.status = SessionStatus.EXPIRED
        self.update_timestamp()
    
    def set_session_data(self, data: SessionData) -> None:
        """Set session data (simplified - no encryption for demo)."""
        # In a real implementation, this would be encrypted
        session_dict = {
            'user_name': data.user_name,
            'user_email': data.user_email,
            'permissions': data.permissions,
            'preferences': data.preferences
        }
        self.session_data = json.dumps(session_dict)
        self.update_timestamp()
    
    def get_session_data(self) -> Optional[SessionData]:
        """Get session data (simplified - no decryption for demo)."""
        if not self.session_data:
            return None
        
        try:
            # In a real implementation, this would be decrypted first
            session_dict = json.loads(self.session_data)
            return SessionData(
                user_name=session_dict.get('user_name', ''),
                user_email=session_dict.get('user_email', ''),
                permissions=session_dict.get('permissions', []),
                preferences=session_dict.get('preferences', {})
            )
        except (json.JSONDecodeError, KeyError):
            return None
    
    def get_remaining_time(self) -> timedelta:
        """Get remaining time before session expires."""
        if self.is_expired():
            return timedelta(0)
        return self.expires_at - datetime.utcnow()
    
    def validate_access(self, ip_address: Optional[str] = None, 
                       user_agent: Optional[str] = None) -> bool:
        """Validate session access (simplified validation)."""
        if not self.is_active():
            return False
        
        # In a real implementation, you might want to validate IP/user agent
        # For demo purposes, we'll just update access and return True
        self.update_access(ip_address, user_agent)
        return True
    
    def to_dict(self) -> dict:
        """Convert user session to dictionary representation."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'user_type': self.user_type.value,
            'last_accessed': self.last_accessed.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status.value,
            'session_data': self.session_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserSession':
        """Create user session from dictionary representation."""
        from uuid import UUID
        from datetime import datetime
        
        session = cls()
        session.id = UUID(data['id'])
        session.user_id = UUID(data['user_id'])
        session.user_type = UserType(data['user_type'])
        session.last_accessed = datetime.fromisoformat(data['last_accessed'])
        session.expires_at = datetime.fromisoformat(data['expires_at'])
        session.ip_address = data['ip_address']
        session.user_agent = data['user_agent']
        session.status = SessionStatus(data['status'])
        session.session_data = data['session_data']
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.updated_at = datetime.fromisoformat(data['updated_at'])
        session.created_by = UUID(data['created_by']) if data['created_by'] else None
        session.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        
        return session