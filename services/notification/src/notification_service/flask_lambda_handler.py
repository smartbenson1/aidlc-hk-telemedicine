"""Flask Lambda handler for AWS deployment."""

import json
import logging
from typing import Dict, Any

# Configure logging for Lambda
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for Flask application."""
    try:
        # Import Flask app
        from .api.main import app
        
        # Handle different event types
        if 'httpMethod' in event:
            # API Gateway event
            return handle_api_gateway_event(app, event, context)
        elif 'source' in event and event['source'] == 'aws.events':
            # EventBridge scheduled event
            return handle_eventbridge_event(event, context)
        elif 'Records' in event:
            # SQS event
            return handle_sqs_event(event, context)
        else:
            logger.warning(f"Unknown event type: {event}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Unknown event type'
                })
            }
            
    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

def handle_api_gateway_event(app, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle API Gateway events."""
    try:
        from werkzeug.serving import WSGIRequestHandler
        from werkzeug.wrappers import Request, Response
        from io import StringIO
        import sys
        
        # Create WSGI environment from API Gateway event
        environ = create_wsgi_environ(event)
        
        # Capture response
        response_data = {}
        
        def start_response(status, headers):
            response_data['status'] = status
            response_data['headers'] = dict(headers)
        
        # Call Flask app
        with app.app_context():
            response_iter = app.wsgi_app(environ, start_response)
            response_body = b''.join(response_iter).decode('utf-8')
        
        # Format response for API Gateway
        status_code = int(response_data['status'].split()[0])
        headers = response_data.get('headers', {})
        
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': response_body,
            'isBase64Encoded': False
        }
        
    except Exception as e:
        logger.error(f"API Gateway handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

def create_wsgi_environ(event: Dict[str, Any]) -> Dict[str, Any]:
    """Create WSGI environment from API Gateway event."""
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'SCRIPT_NAME': '',
        'PATH_INFO': event['path'],
        'QUERY_STRING': '',
        'CONTENT_TYPE': '',
        'CONTENT_LENGTH': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': StringIO(),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False
    }
    
    # Add query parameters
    if event.get('queryStringParameters'):
        query_params = []
        for key, value in event['queryStringParameters'].items():
            query_params.append(f"{key}={value}")
        environ['QUERY_STRING'] = '&'.join(query_params)
    
    # Add headers
    if event.get('headers'):
        for key, value in event['headers'].items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = f'HTTP_{key}'
            environ[key] = value
    
    # Add body
    if event.get('body'):
        from io import StringIO
        environ['wsgi.input'] = StringIO(event['body'])
        environ['CONTENT_LENGTH'] = str(len(event['body']))
    
    return environ

def handle_eventbridge_event(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle EventBridge scheduled events."""
    try:
        logger.info(f"Processing EventBridge event: {event}")
        
        # TODO: Process scheduled notifications
        # This would query DynamoDB for notifications due for delivery
        # and queue them in SQS for processing
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'EventBridge event processed'
            })
        }
        
    except Exception as e:
        logger.error(f"EventBridge handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': 'Failed to process EventBridge event'
            })
        }

def handle_sqs_event(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle SQS events for notification processing."""
    try:
        logger.info(f"Processing SQS event with {len(event['Records'])} records")
        
        processed_count = 0
        failed_count = 0
        
        for record in event['Records']:
            try:
                # Parse message body
                message_body = json.loads(record['body'])
                logger.info(f"Processing notification: {message_body}")
                
                # TODO: Process notification (send email via SES)
                # This would:
                # 1. Retrieve notification details from DynamoDB
                # 2. Render email template
                # 3. Send email via SES
                # 4. Update delivery status in DynamoDB
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process SQS record: {e}")
                failed_count += 1
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'processed': processed_count,
                'failed': failed_count
            })
        }
        
    except Exception as e:
        logger.error(f"SQS handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': 'Failed to process SQS event'
            })
        }