"""Multi-provider email service with failover capabilities."""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from ..models.notification import Notification
from ..models.delivery_status import DeliveryStatus
from ..enums import DeliveryStatusEnum, ProviderType
from ..exceptions import NotificationError
from .email_service import SESEmailService
from .rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)

class EmailProviderPriority(Enum):
    """Email provider priority levels."""
    PRIMARY = 1
    SECONDARY = 2
    TERTIARY = 3

class EmailProvider:
    """Email provider configuration."""
    
    def __init__(self, 
                 provider_type: ProviderType,
                 service_instance: Any,
                 priority: EmailProviderPriority,
                 is_active: bool = True,
                 rate_limit_per_second: int = 10):
        self.provider_type = provider_type
        self.service_instance = service_instance
        self.priority = priority
        self.is_active = is_active
        self.rate_limit_per_second = rate_limit_per_second
        self.consecutive_failures = 0
        self.last_failure_time = None

class MultiProviderEmailService:
    """Multi-provider email service with automatic failover."""
    
    def __init__(self):
        """Initialize multi-provider email service."""
        self.providers: List[EmailProvider] = []
        self.max_consecutive_failures = 3
        self.failover_cooldown_minutes = 15
        self.rate_limiter = get_rate_limiter()
        
    def add_provider(self, provider: EmailProvider) -> None:
        """Add email provider to the service."""
        self.providers.append(provider)
        # Sort by priority
        self.providers.sort(key=lambda p: p.priority.value)
        logger.info(f"Added email provider: {provider.provider_type.value} with priority {provider.priority.value}")
    
    def send_email(self, notification: Notification) -> DeliveryStatus:
        """Send email using the first available provider."""
        if not self.providers:
            raise NotificationError("No email providers configured")
        
        last_error = None
        
        for provider in self._get_available_providers():
            try:
                # Check rate limits before sending
                provider_name = provider.provider_type.value
                if not self.rate_limiter.can_send(provider_name):
                    wait_time = self.rate_limiter.get_wait_time(provider_name)
                    logger.warning(f"Rate limit exceeded for {provider_name}, would need to wait {wait_time:.2f} seconds")
                    continue
                
                logger.info(f"Attempting to send email via {provider_name}")
                
                # Consume rate limit token
                if not self.rate_limiter.consume(provider_name):
                    logger.warning(f"Failed to consume rate limit token for {provider_name}")
                    continue
                
                # Send email using the provider
                delivery_status = provider.service_instance.send_email(notification)
                
                # If successful, reset failure count and return
                if delivery_status.status == DeliveryStatusEnum.SENT:
                    provider.consecutive_failures = 0
                    provider.last_failure_time = None
                    logger.info(f"Email sent successfully via {provider.provider_type.value}")
                    return delivery_status
                else:
                    # Provider returned failure status
                    self._handle_provider_failure(provider, delivery_status.response_message)
                    last_error = delivery_status.response_message
                    continue
                    
            except Exception as e:
                # Provider threw exception
                error_message = str(e)
                logger.error(f"Provider {provider.provider_type.value} failed: {error_message}")
                self._handle_provider_failure(provider, error_message)
                last_error = error_message
                continue
        
        # All providers failed
        logger.error(f"All email providers failed for notification {notification.id}")
        return DeliveryStatus(
            notification_id=notification.id,
            delivery_provider="multi_provider",
            recipient_email=notification.recipient_email,
            delivery_attempt=1,
            status=DeliveryStatusEnum.FAILED,
            response_message=f"All providers failed. Last error: {last_error}"
        )
    
    def send_html_email(self, notification: Notification, html_body: str) -> DeliveryStatus:
        """Send HTML email using the first available provider."""
        if not self.providers:
            raise NotificationError("No email providers configured")
        
        last_error = None
        
        for provider in self._get_available_providers():
            try:
                logger.info(f"Attempting to send HTML email via {provider.provider_type.value}")
                
                # Check if provider supports HTML email
                if hasattr(provider.service_instance, 'send_html_email'):
                    delivery_status = provider.service_instance.send_html_email(notification, html_body)
                else:
                    # Fallback to text email
                    delivery_status = provider.service_instance.send_email(notification)
                
                # If successful, reset failure count and return
                if delivery_status.status == DeliveryStatusEnum.SENT:
                    provider.consecutive_failures = 0
                    provider.last_failure_time = None
                    logger.info(f"HTML email sent successfully via {provider.provider_type.value}")
                    return delivery_status
                else:
                    # Provider returned failure status
                    self._handle_provider_failure(provider, delivery_status.response_message)
                    last_error = delivery_status.response_message
                    continue
                    
            except Exception as e:
                # Provider threw exception
                error_message = str(e)
                logger.error(f"Provider {provider.provider_type.value} failed: {error_message}")
                self._handle_provider_failure(provider, error_message)
                last_error = error_message
                continue
        
        # All providers failed
        logger.error(f"All email providers failed for HTML notification {notification.id}")
        return DeliveryStatus(
            notification_id=notification.id,
            delivery_provider="multi_provider",
            recipient_email=notification.recipient_email,
            delivery_attempt=1,
            status=DeliveryStatusEnum.FAILED,
            response_message=f"All providers failed. Last error: {last_error}"
        )
    
    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Get status of all configured providers."""
        status_list = []
        
        for provider in self.providers:
            status_list.append({
                'provider_type': provider.provider_type.value,
                'priority': provider.priority.value,
                'is_active': provider.is_active,
                'consecutive_failures': provider.consecutive_failures,
                'last_failure_time': provider.last_failure_time.isoformat() if provider.last_failure_time else None,
                'is_available': self._is_provider_available(provider)
            })
        
        return status_list
    
    def reset_provider_failures(self, provider_type: ProviderType) -> bool:
        """Reset failure count for a specific provider."""
        for provider in self.providers:
            if provider.provider_type == provider_type:
                provider.consecutive_failures = 0
                provider.last_failure_time = None
                logger.info(f"Reset failures for provider {provider_type.value}")
                return True
        
        return False
    
    def _get_available_providers(self) -> List[EmailProvider]:
        """Get list of available providers sorted by priority."""
        available_providers = []
        
        for provider in self.providers:
            if self._is_provider_available(provider):
                available_providers.append(provider)
        
        return available_providers
    
    def _is_provider_available(self, provider: EmailProvider) -> bool:
        """Check if provider is available for use."""
        if not provider.is_active:
            return False
        
        # Check if provider has exceeded failure threshold
        if provider.consecutive_failures >= self.max_consecutive_failures:
            # Check if cooldown period has passed
            if provider.last_failure_time:
                from datetime import datetime, timedelta
                cooldown_period = timedelta(minutes=self.failover_cooldown_minutes)
                if datetime.now() - provider.last_failure_time < cooldown_period:
                    return False
                else:
                    # Cooldown period passed, reset failures
                    provider.consecutive_failures = 0
                    provider.last_failure_time = None
        
        return True
    
    def _handle_provider_failure(self, provider: EmailProvider, error_message: str) -> None:
        """Handle provider failure by updating failure count."""
        from datetime import datetime
        
        provider.consecutive_failures += 1
        provider.last_failure_time = datetime.now()
        
        logger.warning(f"Provider {provider.provider_type.value} failure #{provider.consecutive_failures}: {error_message}")
        
        if provider.consecutive_failures >= self.max_consecutive_failures:
            logger.error(f"Provider {provider.provider_type.value} marked as unavailable after {self.max_consecutive_failures} consecutive failures")

# Factory function to create configured multi-provider service
def create_multi_provider_email_service() -> MultiProviderEmailService:
    """Create and configure multi-provider email service."""
    service = MultiProviderEmailService()
    
    # Add AWS SES as primary provider
    ses_service = SESEmailService()
    ses_provider = EmailProvider(
        provider_type=ProviderType.AWS_SES,
        service_instance=ses_service,
        priority=EmailProviderPriority.PRIMARY,
        rate_limit_per_second=14  # AWS SES default limit
    )
    service.add_provider(ses_provider)
    
    # TODO: Add additional providers as needed
    # Example: SendGrid as secondary
    # sendgrid_service = SendGridEmailService()
    # sendgrid_provider = EmailProvider(
    #     provider_type=ProviderType.SENDGRID,
    #     service_instance=sendgrid_service,
    #     priority=EmailProviderPriority.SECONDARY
    # )
    # service.add_provider(sendgrid_provider)
    
    return service