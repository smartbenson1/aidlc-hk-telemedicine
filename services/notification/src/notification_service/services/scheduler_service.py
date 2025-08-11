"""EventBridge scheduler service for scheduled notifications."""

import boto3
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

from ..models.notification import Notification
from ..repositories.dynamodb_notification_repository import DynamoDBNotificationRepository
from ..services.queue_service import SQSQueueService
from ..enums import NotificationStatus
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class EventBridgeSchedulerService:
    """EventBridge service for scheduling notifications."""
    
    def __init__(self, 
                 rule_name: str = "notification-scheduler",
                 target_lambda_arn: str = None):
        """Initialize EventBridge scheduler service."""
        self.events_client = boto3.client('events')
        self.rule_name = rule_name
        self.target_lambda_arn = target_lambda_arn
        
    def create_scheduled_rule(self, 
                            schedule_expression: str = "rate(5 minutes)",
                            description: str = "Process scheduled notifications") -> bool:
        """Create EventBridge rule for scheduled processing."""
        try:
            # Create the rule
            response = self.events_client.put_rule(
                Name=self.rule_name,
                ScheduleExpression=schedule_expression,
                Description=description,
                State='ENABLED'
            )
            
            logger.info(f"Created EventBridge rule: {self.rule_name}")
            
            # Add Lambda target if provided
            if self.target_lambda_arn:
                self.events_client.put_targets(
                    Rule=self.rule_name,
                    Targets=[
                        {
                            'Id': '1',
                            'Arn': self.target_lambda_arn,
                            'Input': json.dumps({
                                'action': 'process_scheduled_notifications',
                                'source': 'eventbridge'
                            })
                        }
                    ]
                )
                logger.info(f"Added Lambda target to rule: {self.target_lambda_arn}")
            
            return True
            
        except ClientError as e:
            logger.error(f"Failed to create EventBridge rule: {e}")
            raise NotificationError(f"Failed to create EventBridge rule: {e}")
    
    def schedule_one_time_notification(self, 
                                     notification_id: str,
                                     scheduled_time: datetime) -> str:
        """Schedule a one-time notification using EventBridge."""
        try:
            # Create unique rule name for this notification
            rule_name = f"notification-{notification_id}"
            
            # Convert datetime to cron expression
            cron_expression = self._datetime_to_cron(scheduled_time)
            
            # Create the rule
            self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=cron_expression,
                Description=f"One-time notification {notification_id}",
                State='ENABLED'
            )
            
            # Add target to process this specific notification
            self.events_client.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        'Id': '1',
                        'Arn': self.target_lambda_arn,
                        'Input': json.dumps({
                            'action': 'process_notification',
                            'notification_id': notification_id,
                            'source': 'eventbridge_scheduled'
                        })
                    }
                ]
            )
            
            logger.info(f"Scheduled one-time notification {notification_id} for {scheduled_time}")
            return rule_name
            
        except ClientError as e:
            logger.error(f"Failed to schedule notification {notification_id}: {e}")
            raise NotificationError(f"Failed to schedule notification: {e}")
    
    def cancel_scheduled_notification(self, rule_name: str) -> bool:
        """Cancel a scheduled notification."""
        try:
            # Remove targets first
            self.events_client.remove_targets(
                Rule=rule_name,
                Ids=['1']
            )
            
            # Delete the rule
            self.events_client.delete_rule(Name=rule_name)
            
            logger.info(f"Cancelled scheduled notification rule: {rule_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to cancel scheduled notification {rule_name}: {e}")
            return False
    
    def _datetime_to_cron(self, dt: datetime) -> str:
        """Convert datetime to EventBridge cron expression."""
        # EventBridge cron format: cron(minutes hours day-of-month month day-of-week year)
        return f"cron({dt.minute} {dt.hour} {dt.day} {dt.month} ? {dt.year})"

class ScheduledNotificationProcessor:
    """Processor for handling scheduled notifications."""
    
    def __init__(self,
                 notification_repo: DynamoDBNotificationRepository,
                 queue_service: SQSQueueService):
        """Initialize scheduled notification processor."""
        self.notification_repo = notification_repo
        self.queue_service = queue_service
    
    def process_due_notifications(self, limit: int = 100) -> Dict[str, Any]:
        """Process notifications that are due for delivery."""
        try:
            logger.info("Processing due notifications...")
            
            # Find notifications due for delivery
            due_notifications = self.notification_repo.find_due_for_delivery(limit)
            
            if not due_notifications:
                logger.info("No notifications due for delivery")
                return {
                    'success': True,
                    'processed': 0,
                    'message': 'No notifications due for delivery'
                }
            
            # Separate by priority for processing order
            urgent_notifications = [n for n in due_notifications if n.priority.value == 'urgent']
            high_notifications = [n for n in due_notifications if n.priority.value == 'high']
            normal_notifications = [n for n in due_notifications if n.priority.value == 'normal']
            low_notifications = [n for n in due_notifications if n.priority.value == 'low']
            
            # Process in priority order
            processed_count = 0
            
            for priority_group in [urgent_notifications, high_notifications, normal_notifications, low_notifications]:
                if priority_group:
                    # Queue notifications for processing
                    message_mapping = self.queue_service.enqueue_batch(priority_group)
                    processed_count += len(message_mapping)
                    
                    # Update notification status to queued
                    for notification in priority_group:
                        if notification.id in message_mapping:
                            self.notification_repo.update_status(
                                notification.id, 
                                NotificationStatus.PENDING
                            )
            
            logger.info(f"Processed {processed_count} due notifications")
            
            return {
                'success': True,
                'processed': processed_count,
                'urgent': len(urgent_notifications),
                'high': len(high_notifications),
                'normal': len(normal_notifications),
                'low': len(low_notifications),
                'message': f'Queued {processed_count} notifications for processing'
            }
            
        except Exception as e:
            logger.error(f"Failed to process due notifications: {e}")
            raise NotificationError(f"Failed to process due notifications: {e}")
    
    def process_reminder_notifications(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Process appointment reminder notifications."""
        try:
            logger.info(f"Processing reminder notifications for {hours_ahead} hours ahead...")
            
            # Calculate target time range
            now = datetime.utcnow()
            target_time = now + timedelta(hours=hours_ahead)
            
            # This would typically query the appointment service for upcoming appointments
            # For now, we'll process any scheduled notifications in the target time range
            
            # Find scheduled notifications in the target time range
            scheduled_notifications = self.notification_repo.find_scheduled_in_range(
                start_time=target_time - timedelta(minutes=30),
                end_time=target_time + timedelta(minutes=30)
            )
            
            if not scheduled_notifications:
                logger.info(f"No reminder notifications found for {hours_ahead} hours ahead")
                return {
                    'success': True,
                    'processed': 0,
                    'message': f'No reminders due in {hours_ahead} hours'
                }
            
            # Queue reminder notifications
            message_mapping = self.queue_service.enqueue_batch(scheduled_notifications)
            
            # Update notification status
            for notification in scheduled_notifications:
                if notification.id in message_mapping:
                    self.notification_repo.update_status(
                        notification.id,
                        NotificationStatus.PENDING
                    )
            
            logger.info(f"Processed {len(message_mapping)} reminder notifications")
            
            return {
                'success': True,
                'processed': len(message_mapping),
                'target_time': target_time.isoformat(),
                'message': f'Queued {len(message_mapping)} reminder notifications'
            }
            
        except Exception as e:
            logger.error(f"Failed to process reminder notifications: {e}")
            raise NotificationError(f"Failed to process reminder notifications: {e}")
    
    def cleanup_old_notifications(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old processed notifications."""
        try:
            logger.info(f"Cleaning up notifications older than {days_old} days...")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Find old notifications that are completed or failed
            old_notifications = self.notification_repo.find_old_notifications(
                cutoff_date=cutoff_date,
                statuses=[NotificationStatus.DELIVERED, NotificationStatus.FAILED]
            )
            
            if not old_notifications:
                logger.info("No old notifications to clean up")
                return {
                    'success': True,
                    'cleaned': 0,
                    'message': 'No old notifications to clean up'
                }
            
            # Archive or delete old notifications
            cleaned_count = 0
            for notification in old_notifications:
                try:
                    # For now, just mark as archived
                    # In production, you might move to cold storage or delete
                    self.notification_repo.archive_notification(notification.id)
                    cleaned_count += 1
                except Exception as e:
                    logger.error(f"Failed to archive notification {notification.id}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} old notifications")
            
            return {
                'success': True,
                'cleaned': cleaned_count,
                'cutoff_date': cutoff_date.isoformat(),
                'message': f'Archived {cleaned_count} old notifications'
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old notifications: {e}")
            raise NotificationError(f"Failed to cleanup old notifications: {e}")

class RetryProcessor:
    """Processor for handling notification retries with exponential backoff."""
    
    def __init__(self,
                 notification_repo: DynamoDBNotificationRepository,
                 queue_service: SQSQueueService):
        """Initialize retry processor."""
        self.notification_repo = notification_repo
        self.queue_service = queue_service
        self.max_retries = 3
        self.base_delay_seconds = 300  # 5 minutes
    
    def process_failed_notifications(self) -> Dict[str, Any]:
        """Process failed notifications for retry."""
        try:
            logger.info("Processing failed notifications for retry...")
            
            # Find failed notifications that can be retried
            failed_notifications = self.notification_repo.find_failed_notifications(
                max_retry_count=self.max_retries
            )
            
            if not failed_notifications:
                logger.info("No failed notifications to retry")
                return {
                    'success': True,
                    'retried': 0,
                    'message': 'No failed notifications to retry'
                }
            
            retried_count = 0
            
            for notification in failed_notifications:
                try:
                    # Calculate delay based on retry count (exponential backoff)
                    delay_seconds = self.base_delay_seconds * (2 ** notification.retry_count)
                    
                    # Re-queue with delay
                    message_id = self.queue_service.enqueue_notification(
                        notification, 
                        delay_seconds=delay_seconds
                    )
                    
                    # Update retry count and status
                    self.notification_repo.increment_retry_count(notification.id)
                    self.notification_repo.update_status(
                        notification.id,
                        NotificationStatus.PENDING
                    )
                    
                    retried_count += 1
                    logger.info(f"Retried notification {notification.id} with {delay_seconds}s delay")
                    
                except Exception as e:
                    logger.error(f"Failed to retry notification {notification.id}: {e}")
            
            logger.info(f"Retried {retried_count} failed notifications")
            
            return {
                'success': True,
                'retried': retried_count,
                'message': f'Retried {retried_count} failed notifications'
            }
            
        except Exception as e:
            logger.error(f"Failed to process failed notifications: {e}")
            raise NotificationError(f"Failed to process failed notifications: {e}")