"""Dead Letter Queue handler for failed notifications."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.notification import Notification
from ..repositories.dynamodb_notification_repository import DynamoDBNotificationRepository
from ..services.queue_service import SQSQueueService
from ..enums import NotificationStatus
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class DeadLetterQueueHandler:
    """Handler for processing messages in the dead letter queue."""
    
    def __init__(self,
                 notification_repo: DynamoDBNotificationRepository,
                 dlq_service: SQSQueueService,
                 main_queue_service: SQSQueueService):
        """Initialize DLQ handler."""
        self.notification_repo = notification_repo
        self.dlq_service = dlq_service
        self.main_queue_service = main_queue_service
    
    def process_dlq_messages(self, max_messages: int = 10) -> Dict[str, Any]:
        """Process messages from the dead letter queue."""
        try:
            logger.info("Processing dead letter queue messages...")
            
            # Receive messages from DLQ
            messages = self.dlq_service.receive_messages(max_messages=max_messages)
            
            if not messages:
                logger.info("No messages in dead letter queue")
                return {
                    'success': True,
                    'processed': 0,
                    'message': 'No messages in DLQ'
                }
            
            processed_count = 0
            requeued_count = 0
            permanently_failed_count = 0
            
            for message in messages:
                try:
                    # Parse message body
                    message_data = json.loads(message['Body'])
                    
                    # Check if this is a DLQ message with failure info
                    if 'original_message' in message_data:
                        original_message = message_data['original_message']
                        failure_reason = message_data.get('failure_reason', 'Unknown')
                        failed_at = message_data.get('failed_at')
                    else:
                        # Direct message in DLQ
                        original_message = message_data
                        failure_reason = 'Message sent to DLQ'
                        failed_at = datetime.utcnow().isoformat()
                    
                    notification_id = original_message.get('notification_id')
                    if not notification_id:
                        logger.error("No notification_id in DLQ message")
                        self.dlq_service.delete_message(message['ReceiptHandle'])
                        continue
                    
                    # Get notification from database
                    notification = self.notification_repo.find_by_id(notification_id)
                    if not notification:
                        logger.error(f"Notification {notification_id} not found in database")
                        self.dlq_service.delete_message(message['ReceiptHandle'])
                        continue
                    
                    # Analyze failure and decide action
                    action = self._analyze_failure(notification, failure_reason, failed_at)
                    
                    if action == 'requeue':
                        # Attempt to requeue for retry
                        self._requeue_notification(notification, failure_reason)
                        requeued_count += 1
                        logger.info(f"Requeued notification {notification_id} from DLQ")
                        
                    elif action == 'manual_review':
                        # Mark for manual review
                        self._mark_for_manual_review(notification, failure_reason)
                        logger.info(f"Marked notification {notification_id} for manual review")
                        
                    else:  # permanent_failure
                        # Mark as permanently failed
                        self._mark_permanent_failure(notification, failure_reason)
                        permanently_failed_count += 1
                        logger.info(f"Marked notification {notification_id} as permanently failed")
                    
                    # Delete message from DLQ
                    self.dlq_service.delete_message(message['ReceiptHandle'])
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process DLQ message: {e}")
                    # Leave message in DLQ for later processing
            
            logger.info(f"Processed {processed_count} DLQ messages: {requeued_count} requeued, {permanently_failed_count} permanently failed")
            
            return {
                'success': True,
                'processed': processed_count,
                'requeued': requeued_count,
                'permanently_failed': permanently_failed_count,
                'manual_review': processed_count - requeued_count - permanently_failed_count,
                'message': f'Processed {processed_count} DLQ messages'
            }
            
        except Exception as e:
            logger.error(f"Failed to process DLQ messages: {e}")
            raise NotificationError(f"Failed to process DLQ messages: {e}")
    
    def get_dlq_statistics(self) -> Dict[str, Any]:
        """Get statistics about the dead letter queue."""
        try:
            # Get queue attributes
            attributes = self.dlq_service.get_queue_attributes()
            
            # Parse relevant statistics
            stats = {
                'approximate_number_of_messages': int(attributes.get('ApproximateNumberOfMessages', 0)),
                'approximate_number_of_messages_not_visible': int(attributes.get('ApproximateNumberOfMessagesNotVisible', 0)),
                'created_timestamp': attributes.get('CreatedTimestamp'),
                'last_modified_timestamp': attributes.get('LastModifiedTimestamp'),
                'message_retention_period': int(attributes.get('MessageRetentionPeriod', 0)),
                'visibility_timeout': int(attributes.get('VisibilityTimeout', 0))
            }
            
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get DLQ statistics: {e}")
            raise NotificationError(f"Failed to get DLQ statistics: {e}")
    
    def reprocess_dlq_message(self, notification_id: str, force: bool = False) -> Dict[str, Any]:
        """Manually reprocess a specific notification from DLQ."""
        try:
            # Get notification from database
            notification = self.notification_repo.find_by_id(notification_id)
            if not notification:
                raise NotificationError(f"Notification {notification_id} not found")
            
            # Check if notification can be retried
            if not force and not notification.can_retry():
                raise NotificationError(f"Notification {notification_id} cannot be retried")
            
            # Reset status and requeue
            self.notification_repo.update_status(notification_id, NotificationStatus.PENDING)
            
            # Requeue for processing
            message_id = self.main_queue_service.enqueue_notification(notification)
            
            logger.info(f"Manually reprocessed notification {notification_id} from DLQ")
            
            return {
                'success': True,
                'notification_id': notification_id,
                'message_id': message_id,
                'message': 'Notification requeued for processing'
            }
            
        except Exception as e:
            logger.error(f"Failed to reprocess notification {notification_id}: {e}")
            raise NotificationError(f"Failed to reprocess notification: {e}")
    
    def _analyze_failure(self, notification: Notification, failure_reason: str, failed_at: str) -> str:
        """Analyze failure and determine appropriate action."""
        # Check retry count
        if notification.retry_count >= 3:
            return 'permanent_failure'
        
        # Analyze failure reason
        failure_reason_lower = failure_reason.lower()
        
        # Temporary failures that can be retried
        temporary_failures = [
            'throttling',
            'rate limit',
            'timeout',
            'connection',
            'temporary',
            'service unavailable',
            '503',
            '429'
        ]
        
        # Permanent failures that should not be retried
        permanent_failures = [
            'invalid email',
            'bounce',
            'complaint',
            'suppressed',
            'blacklisted',
            'invalid destination',
            '400',
            '404'
        ]
        
        # Check for temporary failures
        for temp_failure in temporary_failures:
            if temp_failure in failure_reason_lower:
                return 'requeue'
        
        # Check for permanent failures
        for perm_failure in permanent_failures:
            if perm_failure in failure_reason_lower:
                return 'permanent_failure'
        
        # Unknown failure - mark for manual review
        return 'manual_review'
    
    def _requeue_notification(self, notification: Notification, failure_reason: str) -> None:
        """Requeue notification for retry."""
        # Calculate delay based on retry count
        delay_seconds = 300 * (2 ** notification.retry_count)  # Exponential backoff
        
        # Requeue with delay
        self.main_queue_service.enqueue_notification(notification, delay_seconds=delay_seconds)
        
        # Update status and increment retry count
        self.notification_repo.update_status(notification.id, NotificationStatus.PENDING)
        self.notification_repo.increment_retry_count(notification.id)
        
        # Log the requeue
        logger.info(f"Requeued notification {notification.id} with {delay_seconds}s delay due to: {failure_reason}")
    
    def _mark_for_manual_review(self, notification: Notification, failure_reason: str) -> None:
        """Mark notification for manual review."""
        # Update status with failure reason
        self.notification_repo.update_status(
            notification.id,
            NotificationStatus.FAILED,
            f"Manual review required: {failure_reason}"
        )
        
        # TODO: Create alert or ticket for manual review
        logger.warning(f"Notification {notification.id} marked for manual review: {failure_reason}")
    
    def _mark_permanent_failure(self, notification: Notification, failure_reason: str) -> None:
        """Mark notification as permanently failed."""
        # Update status with failure reason
        self.notification_repo.update_status(
            notification.id,
            NotificationStatus.FAILED,
            f"Permanent failure: {failure_reason}"
        )
        
        logger.error(f"Notification {notification.id} permanently failed: {failure_reason}")

class DLQAnalyzer:
    """Analyzer for DLQ patterns and trends."""
    
    def __init__(self, dlq_service: SQSQueueService):
        """Initialize DLQ analyzer."""
        self.dlq_service = dlq_service
    
    def analyze_failure_patterns(self, sample_size: int = 50) -> Dict[str, Any]:
        """Analyze failure patterns in the DLQ."""
        try:
            # Sample messages from DLQ
            messages = self.dlq_service.receive_messages(max_messages=sample_size)
            
            if not messages:
                return {
                    'success': True,
                    'total_messages': 0,
                    'patterns': {},
                    'message': 'No messages in DLQ to analyze'
                }
            
            # Analyze patterns
            failure_reasons = {}
            notification_types = {}
            recipient_domains = {}
            
            for message in messages:
                try:
                    message_data = json.loads(message['Body'])
                    
                    # Extract failure reason
                    if 'failure_reason' in message_data:
                        reason = message_data['failure_reason']
                        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                    
                    # Extract notification type
                    original_message = message_data.get('original_message', message_data)
                    if 'notification_type' in original_message:
                        ntype = original_message['notification_type']
                        notification_types[ntype] = notification_types.get(ntype, 0) + 1
                    
                    # Extract recipient domain
                    if 'recipient_email' in original_message:
                        email = original_message['recipient_email']
                        domain = email.split('@')[-1] if '@' in email else 'unknown'
                        recipient_domains[domain] = recipient_domains.get(domain, 0) + 1
                        
                except Exception as e:
                    logger.error(f"Failed to analyze DLQ message: {e}")
            
            return {
                'success': True,
                'total_messages': len(messages),
                'patterns': {
                    'failure_reasons': failure_reasons,
                    'notification_types': notification_types,
                    'recipient_domains': recipient_domains
                },
                'recommendations': self._generate_recommendations(failure_reasons, notification_types, recipient_domains)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze DLQ patterns: {e}")
            raise NotificationError(f"Failed to analyze DLQ patterns: {e}")
    
    def _generate_recommendations(self, 
                                failure_reasons: Dict[str, int],
                                notification_types: Dict[str, int],
                                recipient_domains: Dict[str, int]) -> List[str]:
        """Generate recommendations based on failure patterns."""
        recommendations = []
        
        # Analyze failure reasons
        if failure_reasons:
            top_failure = max(failure_reasons, key=failure_reasons.get)
            if 'rate limit' in top_failure.lower():
                recommendations.append("Consider implementing better rate limiting or using multiple email providers")
            elif 'bounce' in top_failure.lower():
                recommendations.append("Implement email validation before sending notifications")
            elif 'timeout' in top_failure.lower():
                recommendations.append("Review email service configuration and network connectivity")
        
        # Analyze notification types
        if notification_types:
            total_notifications = sum(notification_types.values())
            for ntype, count in notification_types.items():
                if count / total_notifications > 0.5:
                    recommendations.append(f"High failure rate for {ntype} notifications - review template and content")
        
        # Analyze recipient domains
        if recipient_domains:
            total_recipients = sum(recipient_domains.values())
            for domain, count in recipient_domains.items():
                if count / total_recipients > 0.3:
                    recommendations.append(f"High failure rate for {domain} domain - check domain reputation")
        
        return recommendations if recommendations else ["No specific recommendations based on current patterns"]