"""Admin User model based on shared_model.md specification."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Import utilities from notification service (reuse existing utilities)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from notification_service.utils.helpers import generate_uuid, get_current_datetime, validate_email
from notification_service.exceptions import ValidationError


class AdminRole(Enum):
    """Admin user roles."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPPORT = "support"


class AdminStatus(Enum):
    """Admin user status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


@dataclass
class AdminUser:
    """
    Admin User component for system administration.
    Based on shared_model.md AdminUser specification.
    """
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Basic Information
    username: str = ""
    email: str = ""
    name: str = ""
    
    # Authentication
    password_hash: str = ""
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Authorization
    role: AdminRole = AdminRole.ADMIN
    permissions: List[str] = field(default_factory=list)
    
    # System Fields
    status: AdminStatus = AdminStatus.ACTIVE
    created_at: datetime = field(default_factory=get_current_datetime)
    updated_at: datetime = field(default_factory=get_current_datetime)
    created_by: str = "system"
    updated_by: str = "system"
    
    def __post_init__(self):
        """Validate data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate admin user data."""
        errors = []
        
        # Required fields
        if not self.username or len(self.username) > 50:
            errors.append("Username is required and must be max 50 characters")
        
        if not self.email or not validate_email(self.email):
            errors.append("Valid email is required")
        
        if not self.name or len(self.name) > 100:
            errors.append("Name is required and must be max 100 characters")
        
        if not self.password_hash:
            errors.append("Password hash is required")
        
        # Validation rules
        if self.login_attempts < 0:
            errors.append("Login attempts cannot be negative")
        
        if errors:
            raise ValidationError(f"Invalid admin user data: {', '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'password_hash': self.password_hash,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_attempts': self.login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'role': self.role.value if isinstance(self.role, AdminRole) else self.role,
            'permissions': self.permissions,
            'status': self.status.value if isinstance(self.status, AdminStatus) else self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdminUser':
        """Create from dictionary."""
        # Convert enums
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = AdminRole(data['role'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = AdminStatus(data['status'])
        
        # Convert datetime strings
        datetime_fields = ['last_login', 'locked_until', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    data[field_name] = None
        
        return cls(**data)
    
    def update_password(self, password_hash: str) -> None:
        """Update password hash."""
        self.password_hash = password_hash
        self.updated_at = get_current_datetime()
    
    def record_login(self) -> None:
        """Record successful login."""
        self.last_login = get_current_datetime()
        self.login_attempts = 0
        self.locked_until = None
        self.updated_at = get_current_datetime()
    
    def record_failed_login(self, max_attempts: int = 5, lockout_minutes: int = 30) -> None:
        """Record failed login attempt."""
        self.login_attempts += 1
        self.updated_at = get_current_datetime()
        
        if self.login_attempts >= max_attempts:
            from datetime import timedelta
            self.locked_until = get_current_datetime() + timedelta(minutes=lockout_minutes)
            self.status = AdminStatus.LOCKED
    
    def is_locked(self) -> bool:
        """Check if account is locked."""
        if self.status == AdminStatus.LOCKED:
            if self.locked_until and self.locked_until > get_current_datetime():
                return True
            else:
                # Auto-unlock if lockout period expired
                self.status = AdminStatus.ACTIVE
                self.locked_until = None
                self.login_attempts = 0
                return False
        return False
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        if self.role == AdminRole.SUPER_ADMIN:
            return True
        return permission in self.permissions
    
    def add_permission(self, permission: str) -> None:
        """Add permission to user."""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = get_current_datetime()
    
    def remove_permission(self, permission: str) -> None:
        """Remove permission from user."""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.updated_at = get_current_datetime()
    
    def __str__(self) -> str:
        """String representation."""
        return f"AdminUser(id={self.id}, username={self.username}, role={self.role.value})"