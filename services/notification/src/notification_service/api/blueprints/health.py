"""Health check blueprint."""

from flask import Blueprint, jsonify
import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os

from ...services.rate_limiter import get_rate_limiter
from ...repositories.dynamodb_notification_repository import DynamoDBNotificationRepository
from ...repositories.dynamodb_template_repository import DynamoDBTemplateRepository

logger = logging.getLogger(__name__)
bp = Blueprint('health', __name__)

@bp.route('/', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        "success": True,
        "service": "Notification Service",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    })

@bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with dependency status."""
    try:
        health_status = {
            "service": "Notification Service",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "dependencies": {}
        }
        
        # Check DynamoDB connectivity
        try:
            # Check notifications table
            notifications_table = os.getenv('NOTIFICATIONS_TABLE', 'notifications')
            notification_repo = DynamoDBNotificationRepository(table_name=notifications_table)
            
            # Try to describe table
            dynamodb = boto3.client('dynamodb')
            dynamodb.describe_table(TableName=notifications_table)
            
            health_status["dependencies"]["dynamodb_notifications"] = {
                "status": "healthy",
                "table_name": notifications_table
            }
            
        except ClientError as e:
            health_status["dependencies"]["dynamodb_notifications"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check templates table
        try:
            templates_table = os.getenv('TEMPLATES_TABLE', 'email_templates')
            
            dynamodb.describe_table(TableName=templates_table)
            
            health_status["dependencies"]["dynamodb_templates"] = {
                "status": "healthy",
                "table_name": templates_table
            }
            
        except ClientError as e:
            health_status["dependencies"]["dynamodb_templates"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check SES connectivity
        try:
            ses_client = boto3.client('ses')
            quota_response = ses_client.get_send_quota()
            
            health_status["dependencies"]["aws_ses"] = {
                "status": "healthy",
                "send_quota": {
                    "max_24_hour_send": quota_response['Max24HourSend'],
                    "max_send_rate": quota_response['MaxSendRate'],
                    "sent_last_24_hours": quota_response['SentLast24Hours']
                }
            }
            
        except ClientError as e:
            health_status["dependencies"]["aws_ses"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check SQS connectivity
        try:
            queue_url = os.getenv('NOTIFICATION_QUEUE_URL', '')
            if queue_url:
                sqs_client = boto3.client('sqs')
                queue_attributes = sqs_client.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
                )
                
                health_status["dependencies"]["aws_sqs"] = {
                    "status": "healthy",
                    "queue_url": queue_url,
                    "messages_available": queue_attributes['Attributes']['ApproximateNumberOfMessages'],
                    "messages_in_flight": queue_attributes['Attributes']['ApproximateNumberOfMessagesNotVisible']
                }
            else:
                health_status["dependencies"]["aws_sqs"] = {
                    "status": "not_configured",
                    "message": "Queue URL not configured"
                }
                
        except ClientError as e:
            health_status["dependencies"]["aws_sqs"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Add rate limiter stats
        try:
            rate_limiter = get_rate_limiter()
            rate_stats = rate_limiter.get_all_stats()
            
            health_status["rate_limiter"] = {
                "status": "healthy",
                "provider_stats": rate_stats
            }
            
        except Exception as e:
            health_status["rate_limiter"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return jsonify({
            "success": True,
            **health_status
        })
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {e}")
        return jsonify({
            "success": False,
            "service": "Notification Service",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 500

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get service metrics."""
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "Notification Service"
        }
        
        # Get rate limiter metrics
        try:
            rate_limiter = get_rate_limiter()
            metrics["rate_limiter"] = rate_limiter.get_all_stats()
        except Exception as e:
            logger.error(f"Failed to get rate limiter metrics: {e}")
            metrics["rate_limiter"] = {"error": str(e)}
        
        # Get SES metrics
        try:
            ses_client = boto3.client('ses')
            
            # Get send quota
            quota_response = ses_client.get_send_quota()
            
            # Get send statistics
            stats_response = ses_client.get_send_statistics()
            
            metrics["aws_ses"] = {
                "send_quota": quota_response,
                "send_statistics": stats_response['SendDataPoints'][-5:] if stats_response['SendDataPoints'] else []  # Last 5 data points
            }
            
        except Exception as e:
            logger.error(f"Failed to get SES metrics: {e}")
            metrics["aws_ses"] = {"error": str(e)}
        
        # Get SQS metrics
        try:
            queue_url = os.getenv('NOTIFICATION_QUEUE_URL', '')
            if queue_url:
                sqs_client = boto3.client('sqs')
                queue_attributes = sqs_client.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=['All']
                )
                
                metrics["aws_sqs"] = {
                    "queue_url": queue_url,
                    "attributes": queue_attributes['Attributes']
                }
            else:
                metrics["aws_sqs"] = {"message": "Queue URL not configured"}
                
        except Exception as e:
            logger.error(f"Failed to get SQS metrics: {e}")
            metrics["aws_sqs"] = {"error": str(e)}
        
        return jsonify({
            "success": True,
            "metrics": metrics
        })
        
    except Exception as e:
        logger.error(f"Error in get_metrics: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 500