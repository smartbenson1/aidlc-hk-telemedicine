#!/usr/bin/env python3
"""
Simplified AWS Lambda Handler without Pydantic dependencies
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
    from mangum import Mangum
    from user_management_service.api.simple_main import app
    from user_management_service.utils.logging_utils import get_logger
    
    logger = get_logger(__name__)
    
    # Create Mangum handler for API Gateway integration
    handler = Mangum(app, lifespan="off")
    
    def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Simplified AWS Lambda handler function.
        
        Args:
            event: API Gateway event
            context: Lambda context
            
        Returns:
            API Gateway response
        """
        try:
            # Log request information
            logger.info(
                f"Processing request",
                extra={
                    "request_id": context.aws_request_id,
                    "function_name": context.function_name,
                    "function_version": context.function_version,
                    "remaining_time": context.get_remaining_time_in_millis(),
                    "http_method": event.get("httpMethod"),
                    "path": event.get("path"),
                    "resource": event.get("resource")
                }
            )
            
            # Process request through Mangum
            response = handler(event, context)
            
            # Log response information
            logger.info(
                f"Request processed successfully",
                extra={
                    "request_id": context.aws_request_id,
                    "status_code": response.get("statusCode"),
                    "response_size": len(json.dumps(response)) if response else 0
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Lambda handler error: {e}",
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
    logger.error(f"Failed to import dependencies: {e}")
    
    def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Fallback handler when dependencies are not available."""
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "message": "Service dependencies not available",
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
                "service": "user-management-service-simplified",
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
                "service": "user-management-service-simplified",
                "error": str(e),
                "request_id": context.aws_request_id
            })
        }