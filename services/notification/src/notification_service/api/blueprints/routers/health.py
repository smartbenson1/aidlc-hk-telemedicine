"""Health check blueprint."""

from flask import Blueprint, jsonify
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
bp = Blueprint('health', __name__)

@bp.route('/')
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@bp.route('/detailed')
def detailed_health_check():
    """Detailed health check with dependency status."""
    health_status = {
        "success": True,
        "status": "healthy",
        "service": "notification-service",
        "dependencies": {}
    }
    
    # Check DynamoDB connectivity
    try:
        dynamodb = boto3.client('dynamodb')
        # Simple operation to test connectivity
        dynamodb.list_tables()
        health_status["dependencies"]["dynamodb"] = "healthy"
    except Exception as e:
        logger.error(f"DynamoDB health check failed: {e}")
        health_status["dependencies"]["dynamodb"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check SES connectivity
    try:
        ses = boto3.client('ses')
        # Simple operation to test connectivity
        ses.get_send_quota()
        health_status["dependencies"]["ses"] = "healthy"
    except Exception as e:
        logger.error(f"SES health check failed: {e}")
        health_status["dependencies"]["ses"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check SQS connectivity
    try:
        sqs = boto3.client('sqs')
        # Simple operation to test connectivity
        sqs.list_queues()
        health_status["dependencies"]["sqs"] = "healthy"
    except Exception as e:
        logger.error(f"SQS health check failed: {e}")
        health_status["dependencies"]["sqs"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return jsonify(health_status)