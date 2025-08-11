#!/usr/bin/env python3
"""
Flask Lambda handler using serverless-wsgi
"""

import json
import os
import sys
import logging
from typing import Dict, Any

# Configure logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    import serverless_wsgi
    from user_management_service.flask_app import app
    from user_management_service.utils.logging_utils import get_logger
    
    logger = get_logger(__name__)
    
    def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Flask Lambda handler using serverless-wsgi.
        
        Args:
            event: API Gateway event
            context: Lambda context
            
        Returns:
            API Gateway response
        """
        try:
            # Log request information
            logger.info(
                f"Processing Flask request",
                extra={
                    "request_id": context.aws_request_id,
                    "function_name": context.function_name,
                    "http_method": event.get("httpMethod"),
                    "path": event.get("path")
                }
            )
            
            # Process request through serverless-wsgi
            response = serverless_wsgi.handle_request(app, event, context)
            
            # Log response information
            logger.info(
                f"Flask request processed successfully",
                extra={
                    "request_id": context.aws_request_id,
                    "status_code": response.get("statusCode")
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Flask Lambda handler error: {e}",
                extra={
                    "request_id": context.aws_request_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                exc_info=True
            )
            
            # Return error response
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "message": "Internal server error",
                    "error_code": "LAMBDA_ERROR",
                    "request_id": context.aws_request_id
                })
            }

except ImportError as e:
    # Fallback handler if dependencies are not available
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import Flask dependencies: {e}")
    
    def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Fallback handler when Flask dependencies are not available."""
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "message": "Flask dependencies not available",
                "error_code": "DEPENDENCY_ERROR",
                "request_id": getattr(context, 'aws_request_id', 'unknown')
            })
        }


# Health check handler for direct Lambda invocation
def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Simple health check handler for direct Lambda invocation.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Health check response
    """
    try:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "healthy",
                "service": "user-management-service-flask",
                "version": "1.0.0",
                "function_name": context.function_name,
                "function_version": context.function_version,
                "request_id": context.aws_request_id,
                "remaining_time_ms": context.get_remaining_time_in_millis()
            })
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "unhealthy",
                "service": "user-management-service-flask",
                "error": str(e),
                "request_id": context.aws_request_id
            })
        }