"""DynamoDB repository for notifications."""

import boto3
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

from ..models.notification import Notification
from ..enums import NotificationStatus
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class DynamoDBNotificationRepository:
    """DynamoDB repository for notification management."""
    
    def __init__(self, table_name: str = "notifications"):
        """Initialize repository with DynamoDB table."""
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        
    def save(self, notification: Notification) -> Notification:
        """Save notification to DynamoDB."""
        try:
            item = self._notification_to_item(notification)
            
            self.table.put_item(Item=item)
            logger.info(f"Saved notification {notification.id} to DynamoDB")
            
            return notification
            
        except ClientError as e:
            logger.error(f"Failed to save notification {notification.id}: {e}")
            raise NotificationError(f"Failed to save notification: {e}")
    
    def find_by_id(self, notification_id: str) -> Optional[Notification]:
        """Find notification by ID."""
        try:
            response = self.table.get_item(
                Key={'id': notification_id}
            )
            
            if 'Item' not in response:
                return None
            
            return self._item_to_notification(response['Item'])
            
        except ClientError as e:
            logger.error(f"Failed to find notification {notification_id}: {e}")
            raise NotificationError(f"Failed to find notification: {e}")
    
    def find_by_status(self, status: NotificationStatus, limit: int = 100) -> List[Notification]:
        """Find notifications by status."""
        try:
            response = self.table.scan(
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status.value},
                Limit=limit
            )
            
            notifications = []
            for item in response.get('Items', []):
                notifications.append(self._item_to_notification(item))
            
            return notifications
            
        except ClientError as e:
            logger.error(f"Failed to find notifications by status {status}: {e}")
            raise NotificationError(f"Failed to find notifications: {e}")
    
    def find_due_for_delivery(self, limit: int = 100) -> List[Notification]:
        """Find notifications due for delivery."""
        try:
            current_time = datetime.utcnow().isoformat()
            
            response = self.table.scan(
                FilterExpression='#status = :status AND (attribute_not_exists(scheduled_time) OR scheduled_time <= :current_time)',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': NotificationStatus.PENDING.value,
                    ':current_time': current_time
                },
                Limit=limit
            )
            
            notifications = []
            for item in response.get('Items', []):
                notifications.append(self._item_to_notification(item))
            
            return notifications
            
        except ClientError as e:
            logger.error(f"Failed to find due notifications: {e}")
            raise NotificationError(f"Failed to find due notifications: {e}")
    
    def update_status(self, notification_id: str, status: NotificationStatus, 
                     failure_reason: Optional[str] = None) -> None:
        """Update notification status."""
        try:
            update_expression = "SET #status = :status, updated_at = :updated_at"
            expression_values = {
                ':status': status.value,
                ':updated_at': datetime.utcnow().isoformat()
            }
            expression_names = {'#status': 'status'}
            
            if status == NotificationStatus.SENT:
                update_expression += ", sent_at = :sent_at"
                expression_values[':sent_at'] = datetime.utcnow().isoformat()
            elif status == NotificationStatus.DELIVERED:
                update_expression += ", delivered_at = :delivered_at"
                expression_values[':delivered_at'] = datetime.utcnow().isoformat()
            elif status in [NotificationStatus.FAILED, NotificationStatus.BOUNCED]:
                if failure_reason:
                    update_expression += ", failure_reason = :failure_reason"
                    expression_values[':failure_reason'] = failure_reason
            
            self.table.update_item(
                Key={'id': notification_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values
            )
            
            logger.info(f"Updated notification {notification_id} status to {status.value}")
            
        except ClientError as e:
            logger.error(f"Failed to update notification {notification_id} status: {e}")
            raise NotificationError(f"Failed to update notification status: {e}")
    
    def increment_retry_count(self, notification_id: str) -> None:
        """Increment retry count for notification."""
        try:
            self.table.update_item(
                Key={'id': notification_id},
                UpdateExpression="ADD retry_count :inc SET updated_at = :updated_at",
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Incremented retry count for notification {notification_id}")
            
        except ClientError as e:
            logger.error(f"Failed to increment retry count for {notification_id}: {e}")
            raise NotificationError(f"Failed to increment retry count: {e}")
    
    def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cutoff_iso = cutoff_date.isoformat()
            
            # Scan for old notifications
            response = self.table.scan(
                FilterExpression='created_at < :cutoff_date',
                ExpressionAttributeValues={':cutoff_date': cutoff_iso},
                ProjectionExpression='id'
            )
            
            deleted_count = 0
            
            # Delete in batches
            with self.table.batch_writer() as batch:
                for item in response.get('Items', []):
                    batch.delete_item(Key={'id': item['id']})
                    deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} old notifications")
            return deleted_count
            
        except ClientError as e:
            logger.error(f"Failed to delete old notifications: {e}")
            raise NotificationError(f"Failed to delete old notifications: {e}")
    
    def _notification_to_item(self, notification: Notification) -> Dict[str, Any]:
        """Convert notification to DynamoDB item."""
        item = {
            'id': notification.id,
            'recipient_email': notification.recipient_email,
            'recipient_name': notification.recipient_name,
            'recipient_type': notification.recipient_type.value,
            'notification_type': notification.notification_type.value,
            'subject': notification.subject,
            'body': notification.body,
            'template_name': notification.template_name,
            'template_variables': json.dumps(notification.template_variables),
            'priority': notification.priority.value,
            'status': notification.status.value,
            'retry_count': notification.retry_count,
            'created_at': notification.created_at.isoformat(),
            'updated_at': notification.updated_at.isoformat(),
            'created_by': notification.created_by,
            'updated_by': notification.updated_by
        }
        
        # Add optional fields
        if notification.scheduled_time:
            item['scheduled_time'] = notification.scheduled_time.isoformat()
        if notification.sent_at:
            item['sent_at'] = notification.sent_at.isoformat()
        if notification.delivered_at:
            item['delivered_at'] = notification.delivered_at.isoformat()
        if notification.failure_reason:
            item['failure_reason'] = notification.failure_reason
        
        return item
    
    def _item_to_notification(self, item: Dict[str, Any]) -> Notification:
        """Convert DynamoDB item to notification."""
        from ..enums import NotificationType, RecipientType, Priority, NotificationStatus
        
        # Parse template variables
        template_variables = {}
        if 'template_variables' in item:
            try:
                template_variables = json.loads(item['template_variables'])
            except json.JSONDecodeError:
                template_variables = {}
        
        # Parse datetime fields
        created_at = datetime.fromisoformat(item['created_at'])
        updated_at = datetime.fromisoformat(item['updated_at'])
        scheduled_time = None
        sent_at = None
        delivered_at = None
        
        if 'scheduled_time' in item:
            scheduled_time = datetime.fromisoformat(item['scheduled_time'])
        if 'sent_at' in item:
            sent_at = datetime.fromisoformat(item['sent_at'])
        if 'delivered_at' in item:
            delivered_at = datetime.fromisoformat(item['delivered_at'])
        
        return Notification(
            id=item['id'],
            recipient_email=item['recipient_email'],
            recipient_name=item['recipient_name'],
            recipient_type=RecipientType(item['recipient_type']),
            notification_type=NotificationType(item['notification_type']),
            subject=item['subject'],
            body=item['body'],
            template_name=item['template_name'],
            template_variables=template_variables,
            scheduled_time=scheduled_time,
            priority=Priority(item['priority']),
            status=NotificationStatus(item['status']),
            sent_at=sent_at,
            delivered_at=delivered_at,
            failure_reason=item.get('failure_reason'),
            retry_count=item.get('retry_count', 0),
            created_at=created_at,
            updated_at=updated_at,
            created_by=item.get('created_by', 'system'),
            updated_by=item.get('updated_by', 'system')
        )