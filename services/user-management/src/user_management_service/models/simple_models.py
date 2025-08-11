"""
Simple models without Pydantic dependencies for Lambda compatibility
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import re


def validate_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Simple phone validation - allow various formats including test numbers"""
    # Allow various phone formats including test numbers with letters
    if not phone or len(phone.strip()) < 5:
        return False
    
    # Allow test phone numbers (containing letters) or real phone numbers
    cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # If it contains letters, assume it's a test number and allow it
    if any(c.isalpha() for c in cleaned):
        return len(cleaned) >= 5
    
    # For numeric phone numbers, do basic validation
    pattern = r'^[\+]?[1-9][\d]{7,15}$'
    return bool(re.match(pattern, cleaned))


@dataclass
class DoctorRegistrationData:
    """Simple doctor registration data"""
    name: str
    email: str
    phone: str
    location: str
    specialties: List[str]
    experience: str
    
    def validate(self) -> List[str]:
        """Validate the data and return list of errors"""
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not self.email or not validate_email(self.email):
            errors.append("Invalid email address")
        
        if not self.phone or not validate_phone(self.phone):
            errors.append("Invalid phone number")
        
        if not self.location or len(self.location.strip()) < 5:
            errors.append("Location must be at least 5 characters")
        
        if not self.specialties or len(self.specialties) == 0:
            errors.append("At least one specialty is required")
        
        if not self.experience or len(self.experience.strip()) < 10:
            errors.append("Experience description must be at least 10 characters")
        
        return errors
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DoctorRegistrationData':
        """Create from dictionary"""
        return cls(
            name=data.get('name', '').strip(),
            email=data.get('email', '').strip().lower(),
            phone=data.get('phone', '').strip(),
            location=data.get('location', '').strip(),
            specialties=data.get('specialties', []),
            experience=data.get('experience', '').strip()
        )


@dataclass
class PatientRegistrationData:
    """Simple patient registration data"""
    name: str
    email: str
    phone: str
    medical_history: str = ""
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    emergency_contact_relationship: str = ""
    
    def validate(self) -> List[str]:
        """Validate the data and return list of errors"""
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not self.email or not validate_email(self.email):
            errors.append("Invalid email address")
        
        if not self.phone or not validate_phone(self.phone):
            errors.append("Invalid phone number")
        
        # Emergency contact validation (optional but if provided, must be valid)
        if self.emergency_contact_name and len(self.emergency_contact_name.strip()) < 2:
            errors.append("Emergency contact name must be at least 2 characters")
        
        if self.emergency_contact_phone and not validate_phone(self.emergency_contact_phone):
            errors.append("Invalid emergency contact phone number")
        
        if self.emergency_contact_relationship and len(self.emergency_contact_relationship.strip()) < 2:
            errors.append("Emergency contact relationship must be at least 2 characters")
        
        return errors
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientRegistrationData':
        """Create from dictionary"""
        return cls(
            name=data.get('name', '').strip(),
            email=data.get('email', '').strip().lower(),
            phone=data.get('phone', '').strip(),
            medical_history=data.get('medical_history', '').strip(),
            emergency_contact_name=data.get('emergency_contact_name', '').strip(),
            emergency_contact_phone=data.get('emergency_contact_phone', '').strip(),
            emergency_contact_relationship=data.get('emergency_contact_relationship', '').strip()
        )


@dataclass
class ApiResponse:
    """Simple API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'success': self.success
        }
        
        if self.data is not None:
            result['data'] = self.data
        
        if self.message:
            result['message'] = self.message
        
        if self.error_code:
            result['error_code'] = self.error_code
        
        if self.timestamp:
            result['timestamp'] = self.timestamp
        else:
            result['timestamp'] = datetime.utcnow().isoformat()
        
        return result


def create_success_response(data: Dict[str, Any], message: str = None) -> ApiResponse:
    """Create a success response"""
    return ApiResponse(
        success=True,
        data=data,
        message=message
    )


def create_error_response(message: str, error_code: str = None) -> ApiResponse:
    """Create an error response"""
    return ApiResponse(
        success=False,
        message=message,
        error_code=error_code
    )