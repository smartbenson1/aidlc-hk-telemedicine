"""
Helper utilities for the User Management Service.
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from uuid import UUID, uuid4


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing."""
    return str(uuid4())


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password with salt (simplified implementation)."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use SHA-256 for demo (in production, use bcrypt or similar)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify a password against its hash."""
    computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return secrets.compare_digest(password_hash, computed_hash)


def sanitize_string(input_string: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input by removing potentially harmful characters."""
    if not input_string:
        return ""
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in input_string if ord(char) >= 32)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def format_phone_number(phone: str) -> str:
    """Format phone number to a standard format."""
    # Remove all non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Format based on length (simplified US format)
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    else:
        return phone  # Return original if can't format


def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date."""
    today = datetime.now().date()
    birth_date = birth_date.date() if isinstance(birth_date, datetime) else birth_date
    
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age


def is_business_hours(dt: datetime, start_hour: int = 6, end_hour: int = 23) -> bool:
    """Check if datetime falls within business hours."""
    return start_hour <= dt.hour <= end_hour


def get_week_start(dt: datetime) -> datetime:
    """Get the start of the week (Monday) for a given datetime."""
    days_since_monday = dt.weekday()
    week_start = dt - timedelta(days=days_since_monday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)


def get_date_range_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate the number of days between two dates."""
    return (end_date.date() - start_date.date()).days


def chunk_list(input_list: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def extract_domain_from_email(email: str) -> Optional[str]:
    """Extract domain from email address."""
    if '@' in email:
        return email.split('@')[1].lower()
    return None


def mask_sensitive_data(data: str, mask_char: str = '*', 
                       visible_start: int = 2, visible_end: int = 2) -> str:
    """Mask sensitive data showing only start and end characters."""
    if len(data) <= visible_start + visible_end:
        return mask_char * len(data)
    
    start = data[:visible_start]
    end = data[-visible_end:] if visible_end > 0 else ""
    middle = mask_char * (len(data) - visible_start - visible_end)
    
    return start + middle + end


def convert_to_utc(dt: datetime, timezone_offset_hours: int = 0) -> datetime:
    """Convert datetime to UTC (simplified implementation)."""
    return dt - timedelta(hours=timezone_offset_hours)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def validate_uuid_string(uuid_string: str) -> bool:
    """Validate if string is a valid UUID."""
    try:
        UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """Safely convert value to integer with default fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with default fallback."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def normalize_string(text: str) -> str:
    """Normalize string by converting to lowercase and removing extra spaces."""
    return ' '.join(text.lower().split())


def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate URL-friendly slug from text."""
    import re
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().replace(' ', '-')
    
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug


def calculate_percentage(part: Union[int, float], total: Union[int, float], 
                        decimal_places: int = 1) -> float:
    """Calculate percentage with specified decimal places."""
    if total == 0:
        return 0.0
    
    percentage = (part / total) * 100
    return round(percentage, decimal_places)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return filename.split('.')[-1].lower() if '.' in filename else ""


def is_valid_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file has an allowed extension."""
    extension = get_file_extension(filename)
    return extension in [ext.lower() for ext in allowed_extensions]


def create_pagination_info(page: int, page_size: int, total_count: int) -> Dict[str, Any]:
    """Create pagination information dictionary."""
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "start_index": (page - 1) * page_size + 1 if total_count > 0 else 0,
        "end_index": min(page * page_size, total_count)
    }


def retry_with_backoff(func, max_attempts: int = 3, base_delay: float = 1.0, 
                      exponential_base: float = 2.0, max_delay: float = 60.0):
    """Retry function with exponential backoff."""
    import time
    
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts:
                raise e
            
            delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
            time.sleep(delay)


class Timer:
    """Simple timer context manager for measuring execution time."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.utcnow()
        self.duration = (self.end_time - self.start_time).total_seconds()
    
    def get_duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return self.duration * 1000 if self.duration else 0.0