"""
Utility helper functions for the Appointment Matching Service.
"""

import re
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal

from .exceptions import ValidationError


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def get_current_utc_datetime() -> datetime:
    """Get current UTC datetime."""
    return datetime.utcnow()


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone or not isinstance(phone, str):
        return False
    
    # Simple phone validation - digits, spaces, hyphens, parentheses, plus
    pattern = r'^[\+]?[\d\s\-\(\)]{10,15}$'
    return bool(re.match(pattern, phone))


def validate_string_length(value: str, max_length: int, min_length: int = 0) -> bool:
    """Validate string length."""
    if not isinstance(value, str):
        return False
    return min_length <= len(value) <= max_length


def validate_decimal_range(value: Decimal, min_val: Decimal, max_val: Decimal) -> bool:
    """Validate decimal is within range."""
    if not isinstance(value, Decimal):
        return False
    return min_val <= value <= max_val


def validate_future_datetime(dt: datetime) -> bool:
    """Validate that datetime is in the future."""
    if not isinstance(dt, datetime):
        return False
    return dt > get_current_utc_datetime()


def validate_booking_window(dt: datetime, max_days: int = 30) -> bool:
    """Validate that datetime is within booking window."""
    if not validate_future_datetime(dt):
        return False
    
    max_future = get_current_utc_datetime() + timedelta(days=max_days)
    return dt <= max_future


def calculate_hours_difference(dt1: datetime, dt2: datetime) -> float:
    """Calculate hours difference between two datetimes."""
    diff = abs(dt2 - dt1)
    return diff.total_seconds() / 3600


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup logging for a component."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def sanitize_text(text: str) -> str:
    """Sanitize text input by removing extra whitespace."""
    if not text:
        return ""
    return " ".join(text.strip().split())


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
    """Extract keywords from text (simple implementation)."""
    if not text:
        return []
    
    # Simple keyword extraction - split by whitespace and punctuation
    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + ',}\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
        'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
        'who', 'whom', 'whose', 'this', 'that', 'these', 'those', 'am', 'is',
        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'having', 'do', 'does', 'did', 'doing', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'shall'
    }
    
    keywords = [word for word in words if word not in stop_words]
    
    # Return unique keywords, limited by max_keywords
    return list(dict.fromkeys(keywords))[:max_keywords]