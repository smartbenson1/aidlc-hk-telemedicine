"""Helper utility functions for the notification service."""

import uuid
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def get_current_datetime() -> datetime:
    """Get the current datetime in UTC."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """Format a datetime object to string."""
    if dt is None:
        return ""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> Optional[datetime]:
    """Parse a datetime string to datetime object."""
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, format_str).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def validate_email(email: str) -> bool:
    """Validate email address format using regex."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (basic validation)."""
    if not phone:
        return False
    
    # Remove common separators and spaces
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it contains only digits and is reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_string(text: str, max_length: int = None) -> str:
    """Sanitize string by removing dangerous characters and optionally truncating."""
    if not text:
        return ""
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max_length with optional suffix."""
    if not text or len(text) <= max_length:
        return text
    
    if len(suffix) >= max_length:
        return text[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def calculate_retry_delay(attempt: int, base_delay: int, max_delay: int, strategy: str = "exponential") -> int:
    """Calculate retry delay based on strategy."""
    if strategy == "fixed":
        return min(base_delay, max_delay)
    elif strategy == "linear":
        return min(base_delay * attempt, max_delay)
    elif strategy == "exponential":
        return min(base_delay * (2 ** (attempt - 1)), max_delay)
    else:
        return base_delay


def is_business_hours(dt: datetime, start_hour: int = 9, end_hour: int = 18) -> bool:
    """Check if datetime falls within business hours."""
    if dt is None:
        return False
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if dt.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's within business hours
    return start_hour <= dt.hour < end_hour


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters."""
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    return mask_char * (len(data) - visible_chars) + data[-visible_chars:]


def generate_correlation_id() -> str:
    """Generate a correlation ID for tracing."""
    return f"corr_{generate_uuid()[:8]}"


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return f"req_{generate_uuid()[:12]}"