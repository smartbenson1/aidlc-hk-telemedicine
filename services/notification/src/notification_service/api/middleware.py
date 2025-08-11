"""API middleware for rate limiting, authentication, and logging."""

import time
import logging
from functools import wraps
from flask import request, jsonify, g
from typing import Dict, Any, Optional

from ..services.rate_limiter import get_rate_limiter
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class APIRateLimiter:
    """Rate limiter for API endpoints."""
    
    def __init__(self):
        """Initialize API rate limiter."""
        self.rate_limiter = get_rate_limiter()
        # API-specific rate limits (requests per minute)
        self.endpoint_limits = {
            'send_notification': 100,
            'schedule_notification': 50,
            'create_template': 10,
            'render_template': 200,
            'default': 60
        }
    
    def check_rate_limit(self, endpoint: str, client_id: str = 'default') -> Dict[str, Any]:
        """Check if request is within rate limits."""
        # Use endpoint-specific limits
        limit = self.endpoint_limits.get(endpoint, self.endpoint_limits['default'])
        
        # Create a unique key for this client and endpoint
        rate_key = f"api_{endpoint}_{client_id}"
        
        # For now, use a simple in-memory rate limiter
        # In production, you'd use Redis or similar
        current_time = time.time()
        
        # Get or create rate limit data for this key
        if not hasattr(g, 'rate_limit_data'):
            g.rate_limit_data = {}
        
        if rate_key not in g.rate_limit_data:
            g.rate_limit_data[rate_key] = {
                'requests': [],
                'limit': limit
            }
        
        rate_data = g.rate_limit_data[rate_key]
        
        # Clean up old requests (older than 1 minute)
        cutoff_time = current_time - 60  # 1 minute ago
        rate_data['requests'] = [req_time for req_time in rate_data['requests'] if req_time > cutoff_time]
        
        # Check if limit exceeded
        if len(rate_data['requests']) >= limit:
            return {
                'allowed': False,
                'limit': limit,
                'remaining': 0,
                'reset_time': int(rate_data['requests'][0] + 60)
            }
        
        # Add current request
        rate_data['requests'].append(current_time)
        
        return {
            'allowed': True,
            'limit': limit,
            'remaining': limit - len(rate_data['requests']),
            'reset_time': int(current_time + 60)
        }

# Global rate limiter instance
api_rate_limiter = APIRateLimiter()

def rate_limit(endpoint_name: str = None):
    """Rate limiting decorator for API endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine endpoint name
            endpoint = endpoint_name or f.__name__
            
            # Get client identifier (IP address for now)
            client_id = request.remote_addr or 'unknown'
            
            # Check rate limit
            rate_check = api_rate_limiter.check_rate_limit(endpoint, client_id)
            
            if not rate_check['allowed']:
                logger.warning(f"Rate limit exceeded for {client_id} on endpoint {endpoint}")
                
                response = jsonify({
                    "success": False,
                    "error": "Rate Limit Exceeded",
                    "message": f"Too many requests. Limit: {rate_check['limit']} per minute",
                    "retry_after": rate_check['reset_time'] - int(time.time())
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(rate_check['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_check['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_check['reset_time'])
                
                return response
            
            # Add rate limit headers to response
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(rate_check['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_check['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_check['reset_time'])
            
            return response
        
        return decorated_function
    return decorator

def log_request():
    """Log incoming requests."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Log request
            logger.info(f"API Request: {request.method} {request.path} from {request.remote_addr}")
            
            try:
                # Execute the function
                response = f(*args, **kwargs)
                
                # Log response
                duration = time.time() - start_time
                status_code = getattr(response, 'status_code', 200)
                logger.info(f"API Response: {status_code} in {duration:.3f}s")
                
                return response
                
            except Exception as e:
                # Log error
                duration = time.time() - start_time
                logger.error(f"API Error: {str(e)} in {duration:.3f}s")
                raise
        
        return decorated_function
    return decorator

def validate_json():
    """Validate that request contains valid JSON."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not request.is_json:
                    return jsonify({
                        "success": False,
                        "error": "Invalid Content Type",
                        "message": "Request must contain valid JSON"
                    }), 400
                
                try:
                    request.get_json()
                except Exception as e:
                    return jsonify({
                        "success": False,
                        "error": "Invalid JSON",
                        "message": "Request body contains invalid JSON"
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def handle_errors():
    """Error handling decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except NotificationError as e:
                logger.error(f"Notification error in {f.__name__}: {e}")
                return jsonify({
                    "success": False,
                    "error": "Notification Error",
                    "message": str(e)
                }), 500
            except ValueError as e:
                logger.error(f"Validation error in {f.__name__}: {e}")
                return jsonify({
                    "success": False,
                    "error": "Validation Error",
                    "message": str(e)
                }), 400
            except Exception as e:
                logger.error(f"Unexpected error in {f.__name__}: {e}", exc_info=True)
                return jsonify({
                    "success": False,
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred"
                }), 500
        
        return decorated_function
    return decorator

def api_endpoint(endpoint_name: str = None, require_json: bool = True):
    """Combined decorator for API endpoints."""
    def decorator(f):
        # Apply all middleware decorators
        decorated = f
        decorated = handle_errors()(decorated)
        if require_json:
            decorated = validate_json()(decorated)
        decorated = log_request()(decorated)
        decorated = rate_limit(endpoint_name)(decorated)
        
        return decorated
    return decorator

class RequestValidator:
    """Request validation utilities."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
        """Validate that all required fields are present."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_enum_value(value: str, enum_class) -> bool:
        """Validate that value is valid for enum."""
        try:
            enum_class(value)
            return True
        except ValueError:
            return False