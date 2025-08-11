"""
AWS Lambda function to consume user management events and sync doctor data
"""

import json
import boto3
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing user management events from EventBridge
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Parse EventBridge event
        if 'Records' in event:
            # SNS/SQS event
            for record in event['Records']:
                process_record(record)
        elif 'detail' in event:
            # Direct EventBridge event
            process_eventbridge_event(event)
        else:
            logger.warning("Unknown event format")
            return create_response(400, "Unknown event format")
        
        return create_response(200, "Events processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        return create_response(500, f"Error processing event: {str(e)}")


def process_eventbridge_event(event: Dict[str, Any]) -> None:
    """Process EventBridge event"""
    detail_type = event.get('detail-type', '')
    detail = event.get('detail', {})
    source = event.get('source', '')
    
    if source != 'user-management-service':
        logger.info(f"Ignoring event from source: {source}")
        return
    
    if detail_type == 'Doctor Registered':
        sync_doctor_to_appointment_matching(detail, 'create')
    elif detail_type == 'Doctor Updated':
        sync_doctor_to_appointment_matching(detail, 'update')
    elif detail_type == 'Patient Registered':
        logger.info(f"Patient registered: {detail.get('patient_id')} - no sync needed")
    else:
        logger.warning(f"Unknown detail type: {detail_type}")


def process_record(record: Dict[str, Any]) -> None:
    """Process individual record from SNS/SQS"""
    if 'Sns' in record:
        # SNS record
        message = json.loads(record['Sns']['Message'])
        process_eventbridge_event(message)
    elif 'body' in record:
        # SQS record
        message = json.loads(record['body'])
        process_eventbridge_event(message)


def sync_doctor_to_appointment_matching(doctor_data: Dict[str, Any], operation: str) -> None:
    """Sync doctor data to appointment-matching-doctors table"""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('appointment-matching-doctors')
        
        # Transform doctor data for appointment matching table
        appointment_doctor = {
            'id': doctor_data['doctor_id'],
            'name': doctor_data['name'],
            'email': doctor_data['email'],
            'phone': doctor_data['phone'],
            'location': doctor_data['location'],
            'specialties': doctor_data.get('specialties', []),
            'experience': doctor_data['experience'],
            'rating': Decimal(str(doctor_data.get('rating', 4.5))),
            'status': doctor_data.get('status', 'active'),
            'created_at': doctor_data.get('created_at', datetime.utcnow().isoformat()),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if operation == 'create':
            # Use put_item for create (will overwrite if exists)
            table.put_item(Item=appointment_doctor)
            logger.info(f"Created doctor in appointment-matching: {doctor_data['doctor_id']}")
            
        elif operation == 'update':
            # Use update_item for updates
            update_expression = "SET #name = :name, email = :email, phone = :phone, #location = :location, specialties = :specialties, experience = :experience, rating = :rating, #status = :status, updated_at = :updated_at"
            
            table.update_item(
                Key={'id': doctor_data['doctor_id']},
                UpdateExpression=update_expression,
                ExpressionAttributeNames={
                    '#name': 'name',
                    '#location': 'location', 
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':name': appointment_doctor['name'],
                    ':email': appointment_doctor['email'],
                    ':phone': appointment_doctor['phone'],
                    ':location': appointment_doctor['location'],
                    ':specialties': appointment_doctor['specialties'],
                    ':experience': appointment_doctor['experience'],
                    ':rating': appointment_doctor['rating'],
                    ':status': appointment_doctor['status'],
                    ':updated_at': appointment_doctor['updated_at']
                }
            )
            logger.info(f"Updated doctor in appointment-matching: {doctor_data['doctor_id']}")
        
    except Exception as e:
        logger.error(f"Failed to sync doctor {doctor_data.get('doctor_id')}: {e}")
        raise


def create_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create Lambda response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    }