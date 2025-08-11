"""Core notification service for processing notifications."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.notification import Notification
from ..models.email_template import EmailTemplate
from ..models.notification_request import NotificationRequest
from ..repositories.dynamodb_notification_repository import DynamoDBNotificationRepository
from ..repositories.dynamodb_template_repository import DynamoDBTemplateRepository
from ..services.email_service import SESEmailService
from ..services.queue_service import SQSQueueService
from ..enums import NotificationStatus, RequestStatus
from ..exceptions import ValidationError, NotificationError

logger = logging.getLogger(__name__)

class NotificationService:
    """Core service for notification processing."""
    
    def __init__(self, 
                 notification_repo: DynamoDBNotificationRepository,
                 template_repo: DynamoDBTemplateRepository,
                 email_service: SESEmailService,
                 queue_service: SQSQueueService):
        """Initialize notification service with dependencies."""
        self.notification_repo = notification_repo
        self.template_repo = template_repo
        self.email_service = email_service
        self.queue_service = queue_service
    
    def send_immediate_notification(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send immediate notification."""
        try:
            # Create notification request
            notification_request = self._create_notification_request(request_data)
            
            # Render template and create notification
            notification = self._create_notification_from_request(notification_request)
            
            # Save notification to database
            self.notification_repo.save(notification)
            
            # Queue for immediate processing
            message_id = self.queue_service.enqueue_notification(notification)
            
            logger.info(f"Immediate notification {notification.id} queued with message ID {message_id}")
            
            return {
                "success": True,
                "notification_id": notification.id,
                "status": notification.status.value,
                "message": "Notification queued for delivery"
            }
            
        except Exception as e:
            logger.error(f"Failed to send immediate notification: {e}")
            raise NotificationError(f"Failed to send notification: {e}")
    
    def schedule_notification(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule notification for future delivery."""
        try:
            # Create notification request with scheduled time
            notification_request = self._create_notification_request(request_data, scheduled=True)
            
            # Render template and create notification
            notification = self._create_notification_from_request(notification_request)
            
            # Save notification to database
            self.notification_repo.save(notification)
            
            # TODO: Schedule with EventBridge
            # For now, just save to database
            
            logger.info(f"Notification {notification.id} scheduled for {notification.scheduled_time}")
            
            return {
                "success": True,
                "notification_id": notification.id,
                "status": notification.status.value,
                "scheduled_time": notification.scheduled_time.isoformat() if notification.scheduled_time else None,
                "message": "Notification scheduled for delivery"
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule notification: {e}")
            raise NotificationError(f"Failed to schedule notification: {e}")
    
    def process_notification(self, notification_id: str) -> Dict[str, Any]:
        """Process a single notification (send email)."""
        try:
            # Retrieve notification from database
            notification = self.notification_repo.find_by_id(notification_id)
            if not notification:
                raise NotificationError(f"Notification {notification_id} not found")
            
            # Check if notification is ready for processing
            if not notification.is_due_for_delivery():
                logger.info(f"Notification {notification_id} not yet due for delivery")
                return {
                    "success": False,
                    "message": "Notification not yet due for delivery"
                }
            
            # Update status to processing
            self.notification_repo.update_status(notification_id, NotificationStatus.SENT)
            
            # Send email
            delivery_status = self.email_service.send_email(notification)
            
            # Update notification status based on delivery result
            from ..enums import DeliveryStatusEnum
            if delivery_status.status == DeliveryStatusEnum.SENT:
                self.notification_repo.update_status(notification_id, NotificationStatus.SENT)
                logger.info(f"Notification {notification_id} sent successfully")
                
                return {
                    "success": True,
                    "notification_id": notification_id,
                    "status": "sent",
                    "message": "Notification sent successfully"
                }
            else:
                # Handle failure
                self.notification_repo.update_status(
                    notification_id, 
                    NotificationStatus.FAILED, 
                    delivery_status.response_message
                )
                
                # Check if retry is needed
                notification = self.notification_repo.find_by_id(notification_id)
                if notification and notification.can_retry():
                    self.notification_repo.increment_retry_count(notification_id)
                    # Re-queue with delay for retry
                    self.queue_service.enqueue_notification(notification, delay_seconds=300)  # 5 minute delay
                    
                    logger.info(f"Notification {notification_id} failed, queued for retry")
                    return {
                        "success": False,
                        "notification_id": notification_id,
                        "status": "failed",
                        "message": "Notification failed, queued for retry"
                    }
                else:
                    logger.error(f"Notification {notification_id} failed permanently")
                    return {
                        "success": False,
                        "notification_id": notification_id,
                        "status": "failed",
                        "message": "Notification failed permanently"
                    }
            
        except Exception as e:
            logger.error(f"Failed to process notification {notification_id}: {e}")
            # Update status to failed
            try:
                self.notification_repo.update_status(notification_id, NotificationStatus.FAILED, str(e))
            except:
                pass
            
            raise NotificationError(f"Failed to process notification: {e}")
    
    def process_due_notifications(self, limit: int = 10) -> Dict[str, Any]:
        """Process notifications that are due for delivery."""
        try:
            # Find notifications due for delivery
            due_notifications = self.notification_repo.find_due_for_delivery(limit)
            
            if not due_notifications:
                return {
                    "success": True,
                    "processed": 0,
                    "message": "No notifications due for delivery"
                }
            
            # Queue notifications for processing
            message_mapping = self.queue_service.enqueue_batch(due_notifications)
            
            logger.info(f"Queued {len(message_mapping)} due notifications for processing")
            
            return {
                "success": True,
                "processed": len(message_mapping),
                "message": f"Queued {len(message_mapping)} notifications for processing"
            }
            
        except Exception as e:
            logger.error(f"Failed to process due notifications: {e}")
            raise NotificationError(f"Failed to process due notifications: {e}")
    
    def get_notification_status(self, notification_id: str) -> Dict[str, Any]:
        """Get notification status."""
        try:
            notification = self.notification_repo.find_by_id(notification_id)
            if not notification:
                raise NotificationError(f"Notification {notification_id} not found")
            
            return {
                "success": True,
                "notification_id": notification.id,
                "status": notification.status.value,
                "recipient_email": notification.recipient_email,
                "notification_type": notification.notification_type.value,
                "created_at": notification.created_at.isoformat(),
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
                "failure_reason": notification.failure_reason,
                "retry_count": notification.retry_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification status: {e}")
            raise NotificationError(f"Failed to get notification status: {e}")
    
    def retry_notification(self, notification_id: str) -> Dict[str, Any]:
        """Retry failed notification."""
        try:
            notification = self.notification_repo.find_by_id(notification_id)
            if not notification:
                raise NotificationError(f"Notification {notification_id} not found")
            
            if not notification.can_retry():
                raise NotificationError("Notification cannot be retried")
            
            # Reset status and increment retry count
            self.notification_repo.update_status(notification_id, NotificationStatus.PENDING)
            self.notification_repo.increment_retry_count(notification_id)
            
            # Re-queue for processing
            message_id = self.queue_service.enqueue_notification(notification)
            
            logger.info(f"Notification {notification_id} queued for retry with message ID {message_id}")
            
            return {
                "success": True,
                "notification_id": notification_id,
                "status": "pending",
                "message": "Notification queued for retry"
            }
            
        except Exception as e:
            logger.error(f"Failed to retry notification {notification_id}: {e}")
            raise NotificationError(f"Failed to retry notification: {e}")
    
    def _create_notification_request(self, request_data: Dict[str, Any], scheduled: bool = False) -> NotificationRequest:
        """Create notification request from request data."""
        from ..enums import NotificationType, RecipientType, Priority
        
        # Validate required fields
        required_fields = ['recipient_email', 'recipient_name', 'recipient_type', 
                          'notification_type', 'template_name']
        if scheduled:
            required_fields.append('scheduled_time')
        
        for field in required_fields:
            if field not in request_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Parse scheduled time if provided
        scheduled_time = None
        if scheduled and 'scheduled_time' in request_data:
            try:
                scheduled_time = datetime.fromisoformat(request_data['scheduled_time'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Invalid scheduled_time format. Use ISO 8601 format.")
            
            if scheduled_time <= datetime.now(scheduled_time.tzinfo):
                raise ValidationError("Scheduled time must be in the future")
        
        return NotificationRequest(
            source_service="api",
            notification_type=NotificationType(request_data['notification_type']),
            recipient_email=request_data['recipient_email'],
            recipient_name=request_data['recipient_name'],
            recipient_type=RecipientType(request_data['recipient_type']),
            template_name=request_data['template_name'],
            template_variables=request_data.get('template_variables', {}),
            priority=Priority(request_data.get('priority', 'normal')),
            scheduled_time=scheduled_time
        )
    
    def _create_notification_from_request(self, request: NotificationRequest) -> Notification:
        """Create notification from request by rendering template."""
        # Retrieve template
        template = self.template_repo.find_by_name(request.template_name)
        if not template:
            raise ValidationError(f"Template '{request.template_name}' not found")
        
        # Render template
        rendered_content = template.render(request.template_variables)
        
        # Create notification
        return Notification(
            recipient_email=request.recipient_email,
            recipient_name=request.recipient_name,
            recipient_type=request.recipient_type,
            notification_type=request.notification_type,
            subject=rendered_content['subject'],
            body=rendered_content['body'],
            template_name=request.template_name,
            template_variables=request.template_variables,
            priority=request.priority,
            scheduled_time=request.scheduled_time
        )