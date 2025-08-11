"""SQS queue service for notification processing."""

import boto3
import json
import logging
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

from ..models.notification import Notification
from ..models.notification_queue import NotificationQueue
from ..enums import QueueType, QueueStatus, Priority
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class SQSQueueService:
    """SQS service for notification queue management."""
    
    def __init__(self, queue_url: str, dlq_url: Optional[str] = None):
        """Initialize SQS queue service."""
        self.sqs_client = boto3.client('sqs')
        self.queue_url = queue_url
        self.dlq_url = dlq_url
        
    def enqueue_notification(self, notification: Notification, delay_seconds: int = 0) -> str:
        """Enqueue notification for processing."""
        try:
            # Prepare message body
            message_body = {
                'notification_id': notification.id,
                'recipient_email': notification.recipient_email,
                'notification_type': notification.notification_type.value,
                'priority': notification.priority.value,
                'template_name': notification.template_name,
                'template_variables': notification.template_variables,
                'retry_count': notification.retry_count
            }
            
            # Set message attributes for priority handling
            message_attributes = {
                'Priority': {
                    'StringValue': notification.priority.value,
                    'DataType': 'String'
                },
                'NotificationType': {
                    'StringValue': notification.notification_type.value,
                    'DataType': 'String'
                }
            }
            
            # Send message to SQS
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes=message_attributes,
                DelaySeconds=delay_seconds
            )
            
            message_id = response['MessageId']
            logger.info(f"Enqueued notification {notification.id} with message ID {message_id}")
            
            return message_id
            
        except ClientError as e:
            logger.error(f"Failed to enqueue notification {notification.id}: {e}")
            raise NotificationError(f"Failed to enqueue notification: {e}")
    
    def enqueue_batch(self, notifications: List[Notification]) -> Dict[str, str]:
        """Enqueue multiple notifications in batch."""
        try:
            entries = []
            
            for i, notification in enumerate(notifications[:10]):  # SQS batch limit is 10
                message_body = {
                    'notification_id': notification.id,
                    'recipient_email': notification.recipient_email,
                    'notification_type': notification.notification_type.value,
                    'priority': notification.priority.value,
                    'template_name': notification.template_name,
                    'template_variables': notification.template_variables,
                    'retry_count': notification.retry_count
                }
                
                entries.append({
                    'Id': str(i),
                    'MessageBody': json.dumps(message_body),
                    'MessageAttributes': {
                        'Priority': {
                            'StringValue': notification.priority.value,
                            'DataType': 'String'
                        },
                        'NotificationType': {
                            'StringValue': notification.notification_type.value,
                            'DataType': 'String'
                        }
                    }
                })
            
            # Send batch to SQS
            response = self.sqs_client.send_message_batch(
                QueueUrl=self.queue_url,
                Entries=entries
            )
            
            # Map successful messages
            message_mapping = {}
            for successful in response.get('Successful', []):
                idx = int(successful['Id'])
                notification_id = notifications[idx].id
                message_mapping[notification_id] = successful['MessageId']
            
            # Log failed messages
            for failed in response.get('Failed', []):
                idx = int(failed['Id'])
                notification_id = notifications[idx].id
                logger.error(f"Failed to enqueue notification {notification_id}: {failed['Message']}")
            
            logger.info(f"Enqueued {len(message_mapping)} notifications in batch")
            return message_mapping
            
        except ClientError as e:
            logger.error(f"Failed to enqueue batch notifications: {e}")
            raise NotificationError(f"Failed to enqueue batch notifications: {e}")
    
    def receive_messages(self, max_messages: int = 10, wait_time: int = 20) -> List[Dict[str, Any]]:
        """Receive messages from queue."""
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            logger.info(f"Received {len(messages)} messages from queue")
            
            return messages
            
        except ClientError as e:
            logger.error(f"Failed to receive messages: {e}")
            raise NotificationError(f"Failed to receive messages: {e}")
    
    def delete_message(self, receipt_handle: str) -> None:
        """Delete processed message from queue."""
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            
            logger.debug(f"Deleted message with receipt handle {receipt_handle}")
            
        except ClientError as e:
            logger.error(f"Failed to delete message: {e}")
            raise NotificationError(f"Failed to delete message: {e}")
    
    def delete_message_batch(self, receipt_handles: List[str]) -> None:
        """Delete multiple processed messages from queue."""
        try:
            entries = []
            for i, receipt_handle in enumerate(receipt_handles[:10]):  # SQS batch limit is 10
                entries.append({
                    'Id': str(i),
                    'ReceiptHandle': receipt_handle
                })
            
            response = self.sqs_client.delete_message_batch(
                QueueUrl=self.queue_url,
                Entries=entries
            )
            
            # Log failed deletions
            for failed in response.get('Failed', []):
                logger.error(f"Failed to delete message: {failed['Message']}")
            
            successful_count = len(response.get('Successful', []))
            logger.info(f"Deleted {successful_count} messages in batch")
            
        except ClientError as e:
            logger.error(f"Failed to delete message batch: {e}")
            raise NotificationError(f"Failed to delete message batch: {e}")
    
    def move_to_dlq(self, message_body: str, reason: str) -> None:
        """Move failed message to dead letter queue."""
        if not self.dlq_url:
            logger.warning("No DLQ configured, cannot move failed message")
            return
        
        try:
            # Add failure reason to message
            dlq_message = {
                'original_message': json.loads(message_body),
                'failure_reason': reason,
                'failed_at': json.dumps(datetime.utcnow().isoformat())
            }
            
            self.sqs_client.send_message(
                QueueUrl=self.dlq_url,
                MessageBody=json.dumps(dlq_message)
            )
            
            logger.info(f"Moved failed message to DLQ: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to move message to DLQ: {e}")
    
    def get_queue_attributes(self) -> Dict[str, Any]:
        """Get queue attributes and statistics."""
        try:
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['All']
            )
            
            return response['Attributes']
            
        except ClientError as e:
            logger.error(f"Failed to get queue attributes: {e}")
            raise NotificationError(f"Failed to get queue attributes: {e}")
    
    def purge_queue(self) -> None:
        """Purge all messages from queue (use with caution)."""
        try:
            self.sqs_client.purge_queue(QueueUrl=self.queue_url)
            logger.warning("Queue purged - all messages deleted")
            
        except ClientError as e:
            logger.error(f"Failed to purge queue: {e}")
            raise NotificationError(f"Failed to purge queue: {e}")