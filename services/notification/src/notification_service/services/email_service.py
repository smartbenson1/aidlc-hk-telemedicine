"""AWS SES email service integration."""

import boto3
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

from ..models.notification import Notification
from ..models.delivery_status import DeliveryStatus
from ..enums import DeliveryStatusEnum, BounceType
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class SESEmailService:
    """AWS SES email service for sending notifications."""
    
    def __init__(self, from_email: str = "noreply@healmatch.com", from_name: str = "HealMatch Easy"):
        """Initialize SES email service."""
        self.ses_client = boto3.client('ses')
        self.from_email = from_email
        self.from_name = from_name
        
    def send_email(self, notification: Notification) -> DeliveryStatus:
        """Send email notification via AWS SES."""
        try:
            # Prepare email parameters
            source = f"{self.from_name} <{self.from_email}>"
            destination = {
                'ToAddresses': [notification.recipient_email]
            }
            message = {
                'Subject': {
                    'Data': notification.subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': notification.body,
                        'Charset': 'UTF-8'
                    }
                }
            }
            
            # Send email
            response = self.ses_client.send_email(
                Source=source,
                Destination=destination,
                Message=message
            )
            
            # Create delivery status
            delivery_status = DeliveryStatus(
                notification_id=notification.id,
                delivery_provider="aws_ses",
                provider_message_id=response['MessageId'],
                recipient_email=notification.recipient_email,
                delivery_attempt=1,
                status=DeliveryStatusEnum.SENT,
                response_code="200",
                response_message="Email sent successfully"
            )
            
            logger.info(f"Email sent successfully for notification {notification.id}, MessageId: {response['MessageId']}")
            return delivery_status
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"Failed to send email for notification {notification.id}: {error_code} - {error_message}")
            
            # Create failed delivery status
            delivery_status = DeliveryStatus(
                notification_id=notification.id,
                delivery_provider="aws_ses",
                recipient_email=notification.recipient_email,
                delivery_attempt=1,
                status=DeliveryStatusEnum.FAILED,
                response_code=error_code,
                response_message=error_message,
                bounce_type=self._get_bounce_type(error_code)
            )
            
            return delivery_status
            
        except Exception as e:
            logger.error(f"Unexpected error sending email for notification {notification.id}: {e}")
            
            # Create failed delivery status
            delivery_status = DeliveryStatus(
                notification_id=notification.id,
                delivery_provider="aws_ses",
                recipient_email=notification.recipient_email,
                delivery_attempt=1,
                status=DeliveryStatusEnum.FAILED,
                response_message=str(e)
            )
            
            return delivery_status
    
    def send_html_email(self, notification: Notification, html_body: str) -> DeliveryStatus:
        """Send HTML email notification via AWS SES."""
        try:
            # Prepare email parameters
            source = f"{self.from_name} <{self.from_email}>"
            destination = {
                'ToAddresses': [notification.recipient_email]
            }
            message = {
                'Subject': {
                    'Data': notification.subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': notification.body,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
            
            # Send email
            response = self.ses_client.send_email(
                Source=source,
                Destination=destination,
                Message=message
            )
            
            # Create delivery status
            delivery_status = DeliveryStatus(
                notification_id=notification.id,
                delivery_provider="aws_ses",
                provider_message_id=response['MessageId'],
                recipient_email=notification.recipient_email,
                delivery_attempt=1,
                status=DeliveryStatusEnum.SENT,
                response_code="200",
                response_message="HTML email sent successfully"
            )
            
            logger.info(f"HTML email sent successfully for notification {notification.id}, MessageId: {response['MessageId']}")
            return delivery_status
            
        except Exception as e:
            logger.error(f"Failed to send HTML email for notification {notification.id}: {e}")
            
            # Create failed delivery status
            delivery_status = DeliveryStatus(
                notification_id=notification.id,
                delivery_provider="aws_ses",
                recipient_email=notification.recipient_email,
                delivery_attempt=1,
                status=DeliveryStatusEnum.FAILED,
                response_message=str(e)
            )
            
            return delivery_status
    
    def verify_email_address(self, email: str) -> bool:
        """Verify email address with SES."""
        try:
            self.ses_client.verify_email_identity(EmailAddress=email)
            logger.info(f"Email verification sent to {email}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to verify email {email}: {e}")
            return False
    
    def get_send_quota(self) -> Dict[str, Any]:
        """Get SES send quota information."""
        try:
            response = self.ses_client.get_send_quota()
            return {
                'max_24_hour_send': response['Max24HourSend'],
                'max_send_rate': response['MaxSendRate'],
                'sent_last_24_hours': response['SentLast24Hours']
            }
            
        except ClientError as e:
            logger.error(f"Failed to get send quota: {e}")
            raise NotificationError(f"Failed to get send quota: {e}")
    
    def get_send_statistics(self) -> List[Dict[str, Any]]:
        """Get SES send statistics."""
        try:
            response = self.ses_client.get_send_statistics()
            return response['SendDataPoints']
            
        except ClientError as e:
            logger.error(f"Failed to get send statistics: {e}")
            raise NotificationError(f"Failed to get send statistics: {e}")
    
    def _get_bounce_type(self, error_code: str) -> BounceType:
        """Determine bounce type from SES error code."""
        hard_bounce_codes = [
            'MessageRejected',
            'InvalidParameterValue',
            'InvalidDestination'
        ]
        
        soft_bounce_codes = [
            'Throttling',
            'SendingPausedException',
            'MailFromDomainNotVerifiedException'
        ]
        
        if error_code in hard_bounce_codes:
            return BounceType.HARD
        elif error_code in soft_bounce_codes:
            return BounceType.SOFT
        else:
            return BounceType.NULL