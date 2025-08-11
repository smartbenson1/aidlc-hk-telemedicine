#!/usr/bin/env python3
"""
Security Configuration for User Management Service

This module provides security configurations, validation rules, and security utilities
for the User Management Service API.
"""

import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
from cryptography.fernet import Fernet

from ..utils.logging_utils import get_logger
from ..utils.exceptions import ValidationError, SecurityError

logger = get_logger(__name__)


class SecurityConfig:
    """Security configuration and utilities."""
    
    # Security constants
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
    
    # Input validation
    MAX_INPUT_LENGTH = 10000
    ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
    MAX_FILE_SIZE_MB = 10
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Sensitive data patterns
    SENSITIVE_PATTERNS = [
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email (for logging)
        r'\b\d{10,15}\b'  # Phone numbers
    ]


class InputValidator:
    """Input validation and sanitization utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10 and len(digits_only) <= 15
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        errors = []
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters long")
        
        if len(password) > SecurityConfig.MAX_PASSWORD_LENGTH:
            errors.append(f"Password must be no more than {SecurityConfig.MAX_PASSWORD_LENGTH} characters long")
        
        if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if SecurityConfig.REQUIRE_NUMBERS and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength_score": max(0, 100 - len(errors) * 20)
        }
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: Optional[int] = None) -> str:
        """Sanitize user input."""
        if not isinstance(input_str, str):
            raise ValidationError("Input must be a string")
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_str)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Apply length limit
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format."""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_str.lower()))
    
    @staticmethod
    def detect_sql_injection(input_str: str) -> bool:
        """Detect potential SQL injection attempts."""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(--|#|/\*|\*/)",
            r"(\bxp_cmdshell\b)",
            r"(\bsp_executesql\b)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def detect_xss(input_str: str) -> bool:
        """Detect potential XSS attempts."""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False


class DataEncryption:
    """Data encryption and decryption utilities."""
    
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            # Generate a key for development (should be stored securely in production)
            self.encryption_key = Fernet.generate_key()
        
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()
        
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise SecurityError("Failed to encrypt sensitive data")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise SecurityError("Failed to decrypt sensitive data")
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Hash password with salt."""
        if not salt:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return {
            "hash": password_hash.hex(),
            "salt": salt
        }
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash."""
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return password_hash.hex() == stored_hash


class AuditLogger:
    """Audit logging for security events."""
    
    def __init__(self):
        self.logger = get_logger("security_audit")
    
    def log_authentication_attempt(self, user_id: str, success: bool, ip_address: str, user_agent: str):
        """Log authentication attempts."""
        self.logger.info(
            f"Authentication attempt",
            extra={
                "event_type": "authentication",
                "user_id": user_id,
                "success": success,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_authorization_failure(self, user_id: str, resource: str, action: str, ip_address: str):
        """Log authorization failures."""
        self.logger.warning(
            f"Authorization failure",
            extra={
                "event_type": "authorization_failure",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_data_access(self, user_id: str, resource_type: str, resource_id: str, action: str):
        """Log data access events."""
        self.logger.info(
            f"Data access",
            extra={
                "event_type": "data_access",
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_security_violation(self, violation_type: str, details: str, ip_address: str, user_agent: str):
        """Log security violations."""
        self.logger.error(
            f"Security violation",
            extra={
                "event_type": "security_violation",
                "violation_type": violation_type,
                "details": details,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self):
        self.attempts = {}  # In production, use Redis or DynamoDB
        self.lockouts = {}
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited."""
        now = datetime.utcnow()
        
        # Check if currently locked out
        if identifier in self.lockouts:
            lockout_until = self.lockouts[identifier]
            if now < lockout_until:
                return True
            else:
                # Lockout expired, remove it
                del self.lockouts[identifier]
        
        return False
    
    def record_attempt(self, identifier: str, success: bool) -> Dict[str, Any]:
        """Record an attempt and return rate limit status."""
        now = datetime.utcnow()
        
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        # Clean old attempts (older than 1 hour)
        self.attempts[identifier] = [
            attempt for attempt in self.attempts[identifier]
            if now - attempt['timestamp'] < timedelta(hours=1)
        ]
        
        # Record current attempt
        self.attempts[identifier].append({
            'timestamp': now,
            'success': success
        })
        
        # Count failed attempts in the last hour
        failed_attempts = sum(
            1 for attempt in self.attempts[identifier]
            if not attempt['success'] and now - attempt['timestamp'] < timedelta(hours=1)
        )
        
        # Apply lockout if too many failed attempts
        if failed_attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            lockout_until = now + timedelta(minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES)
            self.lockouts[identifier] = lockout_until
            
            return {
                "rate_limited": True,
                "lockout_until": lockout_until.isoformat(),
                "failed_attempts": failed_attempts
            }
        
        return {
            "rate_limited": False,
            "failed_attempts": failed_attempts,
            "remaining_attempts": SecurityConfig.MAX_LOGIN_ATTEMPTS - failed_attempts
        }


# Global instances
input_validator = InputValidator()
data_encryption = DataEncryption()
audit_logger = AuditLogger()
rate_limiter = RateLimiter()


def sanitize_for_logging(data: Any) -> Any:
    """Sanitize data for logging by removing sensitive information."""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key.lower() in ['password', 'token', 'secret', 'key', 'authorization']:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_for_logging(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]
    elif isinstance(data, str):
        # Check for sensitive patterns
        for pattern in SecurityConfig.SENSITIVE_PATTERNS:
            if re.search(pattern, data):
                return "[SENSITIVE_DATA_REDACTED]"
        return data
    else:
        return data