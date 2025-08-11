"""
Validation utilities for the User Management Service.
"""

import re
from typing import List, Optional, Any
from dataclasses import dataclass
from uuid import UUID

from .enums import VALID_EMERGENCY_CONTACT_RELATIONSHIPS


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    field: Optional[str] = None
    
    def add_error(self, error: str, field: Optional[str] = None) -> None:
        """Add an error to the validation result."""
        self.is_valid = False
        self.errors.append(error)
        if field and not self.field:
            self.field = field


def validate_email(email: str) -> ValidationResult:
    """Validate email format using simplified logic."""
    result = ValidationResult(is_valid=True, errors=[])
    
    if not email:
        result.add_error("Email is required", "email")
        return result
    
    if len(email) > 255:
        result.add_error("Email must not exceed 255 characters", "email")
    
    # Simplified email validation
    if "@" not in email or "." not in email.split("@")[-1]:
        result.add_error("Invalid email format", "email")
    
    return result


def validate_phone(phone: str) -> ValidationResult:
    """Validate phone number using simplified logic."""
    result = ValidationResult(is_valid=True, errors=[])
    
    if not phone:
        result.add_error("Phone number is required", "phone")
        return result
    
    # Remove common phone number characters
    cleaned_phone = re.sub(r'[^\d]', '', phone)
    
    if len(cleaned_phone) < 10:
        result.add_error("Phone number must have at least 10 digits", "phone")
    elif len(cleaned_phone) > 15:
        result.add_error("Phone number must not exceed 15 digits", "phone")
    
    return result


def validate_name(name: str, field_name: str = "name") -> ValidationResult:
    """Validate name field."""
    result = ValidationResult(is_valid=True, errors=[])
    
    if not name:
        result.add_error(f"{field_name.capitalize()} is required", field_name)
        return result
    
    if len(name) < 2:
        result.add_error(f"{field_name.capitalize()} must be at least 2 characters", field_name)
    elif len(name) > 100:
        result.add_error(f"{field_name.capitalize()} must not exceed 100 characters", field_name)
    
    # Allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        result.add_error(f"{field_name.capitalize()} contains invalid characters", field_name)
    
    return result


def validate_text_length(text: str, field_name: str, min_length: int = 0, 
                        max_length: int = 1000, required: bool = True) -> ValidationResult:
    """Validate text field length."""
    result = ValidationResult(is_valid=True, errors=[])
    
    if not text:
        if required:
            result.add_error(f"{field_name.capitalize()} is required", field_name)
        return result
    
    if len(text) < min_length:
        result.add_error(f"{field_name.capitalize()} must be at least {min_length} characters", field_name)
    elif len(text) > max_length:
        result.add_error(f"{field_name.capitalize()} must not exceed {max_length} characters", field_name)
    
    return result


def validate_uuid_list(uuid_list: List[UUID], field_name: str, 
                      min_count: int = 0, max_count: int = 10) -> ValidationResult:
    """Validate list of UUIDs."""
    result = ValidationResult(is_valid=True, errors=[])
    
    if not uuid_list:
        if min_count > 0:
            result.add_error(f"{field_name.capitalize()} must contain at least {min_count} items", field_name)
        return result
    
    if len(uuid_list) < min_count:
        result.add_error(f"{field_name.capitalize()} must contain at least {min_count} items", field_name)
    elif len(uuid_list) > max_count:
        result.add_error(f"{field_name.capitalize()} must not exceed {max_count} items", field_name)
    
    # Check for duplicates
    if len(uuid_list) != len(set(uuid_list)):
        result.add_error(f"{field_name.capitalize()} contains duplicate items", field_name)
    
    return result


def validate_emergency_contact_relationship(relationship: str) -> ValidationResult:
    """Validate emergency contact relationship."""
    result = ValidationResult(is_valid=True, errors=[])
    
    if not relationship:
        result.add_error("Emergency contact relationship is required", "emergency_contact_relationship")
        return result
    
    if relationship.lower() not in VALID_EMERGENCY_CONTACT_RELATIONSHIPS:
        valid_options = ", ".join(VALID_EMERGENCY_CONTACT_RELATIONSHIPS)
        result.add_error(f"Invalid relationship. Valid options: {valid_options}", "emergency_contact_relationship")
    
    return result


def validate_rating(rating: float) -> ValidationResult:
    """Validate doctor rating."""
    result = ValidationResult(is_valid=True, errors=[])
    
    if rating < 0.0 or rating > 5.0:
        result.add_error("Rating must be between 0.0 and 5.0", "rating")
    
    return result


def combine_validation_results(*results: ValidationResult) -> ValidationResult:
    """Combine multiple validation results into one."""
    combined = ValidationResult(is_valid=True, errors=[])
    
    for result in results:
        if not result.is_valid:
            combined.is_valid = False
            combined.errors.extend(result.errors)
    
    return combined


def validate_required_fields(data: dict, required_fields: List[str]) -> ValidationResult:
    """Validate that all required fields are present and not empty."""
    result = ValidationResult(is_valid=True, errors=[])
    
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            result.add_error(f"{field.replace('_', ' ').capitalize()} is required", field)
    
    return result


def validate_phone_uniqueness(phone1: str, phone2: str, field1: str, field2: str) -> ValidationResult:
    """Validate that two phone numbers are different."""
    result = ValidationResult(is_valid=True, errors=[])
    
    # Clean both phone numbers for comparison
    clean_phone1 = re.sub(r'[^\d]', '', phone1) if phone1 else ""
    clean_phone2 = re.sub(r'[^\d]', '', phone2) if phone2 else ""
    
    if clean_phone1 and clean_phone2 and clean_phone1 == clean_phone2:
        result.add_error(f"{field1} and {field2} must be different", field2)
    
    return result