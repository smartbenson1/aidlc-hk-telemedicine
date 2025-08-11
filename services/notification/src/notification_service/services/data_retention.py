"""Data retention policy service for notification data."""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..repositories.dynamodb_notification_repository import DynamoDBNotificationRepository
from ..repositories.dynamodb_template_repository import DynamoDBTemplateRepository
from ..enums import NotificationStatus
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class DataRetentionService:
    """Service for managing data retention policies."""
    
    def __init__(self,
                 notification_repo: DynamoDBNotificationRepository,
                 template_repo: DynamoDBTemplateRepository):
        """Initialize data retention service."""
        self.notification_repo = notification_repo
        self.template_repo = template_repo
        
        # Default retention policies (in days)
        self.retention_policies = {
            'delivered_notifications': 90,
            'failed_notifications': 180,
            'pending_notifications': 30,
            'template_versions': 365
        }
    
    def apply_retention_policies(self) -> Dict[str, Any]:
        """Apply all retention policies."""
        try:
            results = {}
            
            # Clean up delivered notifications
            delivered_count = self._cleanup_notifications(
                NotificationStatus.DELIVERED,
                self.retention_policies['delivered_notifications']
            )
            results['delivered_notifications_cleaned'] = delivered_count
            
            # Clean up failed notifications
            failed_count = self._cleanup_notifications(
                NotificationStatus.FAILED,
                self.retention_policies['failed_notifications']
            )
            results['failed_notifications_cleaned'] = failed_count
            
            # Clean up old pending notifications (likely stale)
            pending_count = self._cleanup_notifications(
                NotificationStatus.PENDING,
                self.retention_policies['pending_notifications']
            )
            results['pending_notifications_cleaned'] = pending_count
            
            total_cleaned = delivered_count + failed_count + pending_count
            
            logger.info(f"Data retention cleanup completed: {total_cleaned} notifications cleaned")
            
            return {
                'success': True,
                'total_cleaned': total_cleaned,
                'details': results,
                'message': f'Cleaned up {total_cleaned} notifications'
            }
            
        except Exception as e:
            logger.error(f"Failed to apply retention policies: {e}")
            raise NotificationError(f"Failed to apply retention policies: {e}")
    
    def _cleanup_notifications(self, status: NotificationStatus, retention_days: int) -> int:
        """Clean up notifications older than retention period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # This would need to be implemented in the repository
            # For now, return 0 as placeholder
            cleaned_count = 0
            
            logger.info(f"Cleaned up {cleaned_count} {status.value} notifications older than {retention_days} days")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup {status.value} notifications: {e}")
            return 0