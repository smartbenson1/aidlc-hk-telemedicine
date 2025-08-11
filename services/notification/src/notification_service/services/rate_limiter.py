"""Rate limiting service for email delivery."""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter for email delivery."""
    
    def __init__(self, 
                 max_requests_per_second: int = 10,
                 max_requests_per_minute: int = 600,
                 max_requests_per_hour: int = 10000):
        """Initialize rate limiter with different time windows."""
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour
        
        # Token buckets for different time windows
        self.second_bucket = TokenBucket(max_requests_per_second, max_requests_per_second)
        self.minute_bucket = TokenBucket(max_requests_per_minute, max_requests_per_minute / 60)
        self.hour_bucket = TokenBucket(max_requests_per_hour, max_requests_per_hour / 3600)
        
        # Request tracking
        self.request_history = deque()
        self.last_cleanup = datetime.now()
    
    def can_send(self, provider: str = "default") -> bool:
        """Check if a request can be sent without exceeding rate limits."""
        current_time = time.time()
        
        # Clean up old requests
        self._cleanup_history()
        
        # Check all rate limit buckets
        if not self.second_bucket.can_consume():
            logger.warning(f"Rate limit exceeded: {self.max_requests_per_second} requests per second")
            return False
        
        if not self.minute_bucket.can_consume():
            logger.warning(f"Rate limit exceeded: {self.max_requests_per_minute} requests per minute")
            return False
        
        if not self.hour_bucket.can_consume():
            logger.warning(f"Rate limit exceeded: {self.max_requests_per_hour} requests per hour")
            return False
        
        return True
    
    def consume(self, provider: str = "default") -> bool:
        """Consume a token from all rate limit buckets."""
        if not self.can_send(provider):
            return False
        
        # Consume tokens from all buckets
        self.second_bucket.consume()
        self.minute_bucket.consume()
        self.hour_bucket.consume()
        
        # Record the request
        self.request_history.append(datetime.now())
        
        return True
    
    def get_wait_time(self, provider: str = "default") -> float:
        """Get the time to wait before the next request can be sent."""
        wait_times = []
        
        # Check wait time for each bucket
        second_wait = self.second_bucket.get_wait_time()
        if second_wait > 0:
            wait_times.append(second_wait)
        
        minute_wait = self.minute_bucket.get_wait_time()
        if minute_wait > 0:
            wait_times.append(minute_wait)
        
        hour_wait = self.hour_bucket.get_wait_time()
        if hour_wait > 0:
            wait_times.append(hour_wait)
        
        return max(wait_times) if wait_times else 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        now = datetime.now()
        
        # Count requests in different time windows
        requests_last_second = sum(1 for req_time in self.request_history 
                                 if now - req_time <= timedelta(seconds=1))
        requests_last_minute = sum(1 for req_time in self.request_history 
                                 if now - req_time <= timedelta(minutes=1))
        requests_last_hour = sum(1 for req_time in self.request_history 
                               if now - req_time <= timedelta(hours=1))
        
        return {
            'requests_last_second': requests_last_second,
            'requests_last_minute': requests_last_minute,
            'requests_last_hour': requests_last_hour,
            'max_requests_per_second': self.max_requests_per_second,
            'max_requests_per_minute': self.max_requests_per_minute,
            'max_requests_per_hour': self.max_requests_per_hour,
            'second_bucket_tokens': self.second_bucket.tokens,
            'minute_bucket_tokens': self.minute_bucket.tokens,
            'hour_bucket_tokens': self.hour_bucket.tokens,
            'can_send_now': self.can_send()
        }
    
    def _cleanup_history(self) -> None:
        """Clean up old request history to prevent memory growth."""
        now = datetime.now()
        
        # Only cleanup every minute to avoid excessive processing
        if now - self.last_cleanup < timedelta(minutes=1):
            return
        
        # Remove requests older than 1 hour
        cutoff_time = now - timedelta(hours=1)
        while self.request_history and self.request_history[0] < cutoff_time:
            self.request_history.popleft()
        
        self.last_cleanup = now

class TokenBucket:
    """Token bucket implementation for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens in the bucket
            refill_rate: Number of tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def can_consume(self, tokens: int = 1) -> bool:
        """Check if tokens can be consumed without actually consuming them."""
        self._refill()
        return self.tokens >= tokens
    
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from the bucket."""
        if not self.can_consume(tokens):
            return False
        
        self.tokens -= tokens
        return True
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait until enough tokens are available."""
        self._refill()
        
        if self.tokens >= tokens:
            return 0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        
        self.last_refill = now

class ProviderRateLimiter:
    """Rate limiter that manages limits per email provider."""
    
    def __init__(self):
        """Initialize provider-specific rate limiter."""
        self.provider_limiters: Dict[str, RateLimiter] = {}
        self.default_limits = {
            'aws_ses': {'per_second': 14, 'per_minute': 840, 'per_hour': 50400},
            'sendgrid': {'per_second': 10, 'per_minute': 600, 'per_hour': 36000},
            'smtp': {'per_second': 5, 'per_minute': 300, 'per_hour': 18000},
            'mailgun': {'per_second': 10, 'per_minute': 600, 'per_hour': 36000}
        }
    
    def get_limiter(self, provider: str) -> RateLimiter:
        """Get or create rate limiter for a provider."""
        if provider not in self.provider_limiters:
            limits = self.default_limits.get(provider, {
                'per_second': 10,
                'per_minute': 600,
                'per_hour': 36000
            })
            
            self.provider_limiters[provider] = RateLimiter(
                max_requests_per_second=limits['per_second'],
                max_requests_per_minute=limits['per_minute'],
                max_requests_per_hour=limits['per_hour']
            )
            
            logger.info(f"Created rate limiter for provider {provider} with limits: {limits}")
        
        return self.provider_limiters[provider]
    
    def can_send(self, provider: str) -> bool:
        """Check if provider can send a request."""
        limiter = self.get_limiter(provider)
        return limiter.can_send(provider)
    
    def consume(self, provider: str) -> bool:
        """Consume a token for the provider."""
        limiter = self.get_limiter(provider)
        return limiter.consume(provider)
    
    def get_wait_time(self, provider: str) -> float:
        """Get wait time for the provider."""
        limiter = self.get_limiter(provider)
        return limiter.get_wait_time(provider)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all providers."""
        stats = {}
        for provider, limiter in self.provider_limiters.items():
            stats[provider] = limiter.get_stats()
        return stats
    
    def update_provider_limits(self, provider: str, 
                             per_second: int, 
                             per_minute: int, 
                             per_hour: int) -> None:
        """Update rate limits for a specific provider."""
        self.provider_limiters[provider] = RateLimiter(
            max_requests_per_second=per_second,
            max_requests_per_minute=per_minute,
            max_requests_per_hour=per_hour
        )
        
        logger.info(f"Updated rate limits for provider {provider}: {per_second}/s, {per_minute}/m, {per_hour}/h")

# Global rate limiter instance
_global_rate_limiter = ProviderRateLimiter()

def get_rate_limiter() -> ProviderRateLimiter:
    """Get the global rate limiter instance."""
    return _global_rate_limiter