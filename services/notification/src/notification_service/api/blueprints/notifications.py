"""Notifications blueprint."""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import json
import os

from ...models.notification import Notification
from ...models.notification_request import NotificationRequest
from ...enums import NotificationType, RecipientType, Priority, NotificationStatus
from ...exceptions import ValidationError, NotificationError
from ...utils.helpers import generate_uuid
from ...services.notification_service import NotificationService
from ...repositories.dynamodb_notification_repository import DynamoDBNotificationRepository
from ...repositories.dynamodb_template_repository import DynamoDBTemplateRepository
from ...services.email_service import SESEmailService
from ...services.queue_service import SQSQueueService

logger = logging.getLogger(__name__)
bp = Blueprint('notifications', __name__)

# Initialize services (in production, these would be dependency injected)
def get_notification_service():
    """Get notification service instance."""
    notification_repo = DynamoDBNotificationRepository(
        table_name=os.getenv('NOTIFICATIONS_TABLE', 'notifications')
    )
    template_repo = DynamoDBTemplateRepository(
        table_name=os.getenv('TEMPLATES_TABLE', 'email_templates')
    )
    email_service = SESEmailService(
        from_email=os.getenv('FROM_EMAIL', 'noreply@healmatch.com'),
        from_name=os.getenv('FROM_NAME', 'HealMatch Easy')
    )
    queue_service = SQSQueueService(
        queue_url=os.getenv('NOTIFICATION_QUEUE_URL', ''),
        dlq_url=os.getenv('NOTIFICATION_DLQ_URL', '')
    )
    
    return NotificationService(
        notification_repo=notification_repo,
        template_repo=template_repo,
        email_service=email_service,
        queue_service=queue_service
    )

@bp.route('/send', methods=['POST'])
def send_notification():
    """Send immediate notification."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Use notification service
        notification_service = get_notification_service()
        result = notification_service.send_immediate_notification(data)
        
        return jsonify(result)
        
    except ValidationError as e:
        logger.error(f"Validation error in send_notification: {e}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in send_notification: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to send notification"
        }), 500

@bp.route('/schedule', methods=['POST'])
def schedule_notification():
    """Schedule notification for future delivery."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Use notification service
        notification_service = get_notification_service()
        result = notification_service.schedule_notification(data)
        
        return jsonify(result)
        
    except ValidationError as e:
        logger.error(f"Validation error in schedule_notification: {e}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in schedule_notification: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to schedule notification"
        }), 500

@bp.route('/<notification_id>/status', methods=['GET'])
def get_notification_status(notification_id):
    """Get notification status."""
    try:
        # Use notification service
        notification_service = get_notification_service()
        result = notification_service.get_notification_status(notification_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_notification_status: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to retrieve notification status"
        }), 500

@bp.route('/<notification_id>/retry', methods=['POST'])
def retry_notification(notification_id):
    """Retry failed notification."""
    try:
        # Use notification service
        notification_service = get_notification_service()
        result = notification_service.retry_notification(notification_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in retry_notification: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to retry notification"
        }), 500