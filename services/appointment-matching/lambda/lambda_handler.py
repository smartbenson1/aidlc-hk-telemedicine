"""
AWS Lambda handler for Appointment Matching Service
"""

import json
import os
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the service (will be packaged with Lambda)
try:
    from appointment_matching_service.services.appointment_matching_service import AppointmentMatchingService
    from appointment_matching_service.utils.exceptions import (
        AppointmentMatchingServiceError, ValidationError, NotFoundError, 
        BusinessRuleError, BookingError
    )
except ImportError as e:
    logger.error(f"Failed to import appointment matching service: {e}")
    # For development/testing
    AppointmentMatchingService = None


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for Appointment Matching Service API
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Extract request information
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        path_params = event.get('pathParameters') or {}
        body = event.get('body')
        
        # Parse request body if present
        request_data = {}
        if body:
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError:
                return create_error_response(400, "Invalid JSON in request body")
        
        # Initialize service (with DynamoDB repositories)
        if AppointmentMatchingService is None:
            return create_error_response(500, "Service not available")
            
        service = AppointmentMatchingService()
        
        # Route the request
        response = route_request(service, http_method, path, path_params, query_params, request_data)
        
        logger.info(f"Response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return create_error_response(500, f"Internal server error: {str(e)}")


def route_request(service: Any, method: str, path: str, path_params: Dict, 
                 query_params: Dict, request_data: Dict) -> Dict[str, Any]:
    """Route the request to appropriate service method"""
    
    try:
        # Health check
        if path == '/health' and method == 'GET':
            return create_success_response({
                'status': 'healthy',
                'service': 'appointment-matching-service',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            })
        
        # Symptoms endpoints
        elif path == '/symptoms' and method == 'POST':
            return handle_describe_symptoms(service, request_data)
        
        elif path.startswith('/symptoms/') and method == 'GET':
            symptom_id = path_params.get('symptom_id')
            return handle_get_symptom(service, symptom_id)
        
        # Recommendations endpoints
        elif path == '/recommendations' and method == 'POST':
            return handle_get_recommendations(service, request_data)
        
        elif path.startswith('/recommendations/') and method == 'GET':
            recommendation_id = path_params.get('recommendation_id')
            return handle_get_recommendation(service, recommendation_id)
        
        # Appointments endpoints
        elif path == '/appointments' and method == 'POST':
            return handle_book_appointment(service, request_data)
        
        elif path == '/appointments' and method == 'GET':
            patient_id = query_params.get('patient_id')
            doctor_id = query_params.get('doctor_id')
            if patient_id:
                return handle_get_patient_appointments(service, patient_id)
            elif doctor_id:
                return handle_get_doctor_appointments(service, doctor_id)
            else:
                return create_error_response(400, "patient_id or doctor_id required")
        
        elif path.startswith('/appointments/') and path.endswith('/reschedule') and method == 'POST':
            appointment_id = path_params.get('appointment_id')
            return handle_reschedule_appointment(service, appointment_id, request_data)
        
        # Patient appointments
        elif path.startswith('/patients/') and path.endswith('/appointments') and method == 'GET':
            patient_id = path_params.get('patient_id')
            return handle_get_patient_appointments(service, patient_id)
        
        # Doctor appointments
        elif path.startswith('/doctors/') and path.endswith('/appointments') and method == 'GET':
            doctor_id = path_params.get('doctor_id')
            return handle_get_doctor_appointments(service, doctor_id)
        
        # Doctor sync endpoints (for cross-service integration)
        elif path == '/doctors/sync' and method == 'POST':
            return handle_sync_doctor(service, request_data)
        
        elif path.startswith('/doctors/') and path.endswith('/sync') and method == 'PUT':
            doctor_id = path_params.get('doctor_id')
            return handle_update_doctor_sync(service, doctor_id, request_data)
        
        # Doctor appointments  
        elif path.startswith('/doctors/') and path.endswith('/appointments') and method == 'GET':
            doctor_id = path_params.get('doctor_id')
            return handle_get_doctor_appointments(service, doctor_id)
        
        else:
            return create_error_response(404, f"Endpoint not found: {method} {path}")
            
    except ValidationError as e:
        return create_error_response(400, str(e))
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except BusinessRuleError as e:
        return create_error_response(422, str(e))
    except BookingError as e:
        return create_error_response(422, str(e))
    except AppointmentMatchingServiceError as e:
        return create_error_response(500, str(e))


def handle_describe_symptoms(service: Any, request_data: Dict) -> Dict[str, Any]:
    """Handle symptom description request"""
    patient_id = request_data.get('patient_id')
    symptoms_text = request_data.get('symptoms_text')
    
    if not patient_id or not symptoms_text:
        return create_error_response(400, "patient_id and symptoms_text are required")
    
    symptom_desc = service.describe_symptoms(patient_id, symptoms_text)
    
    return create_success_response({
        'id': symptom_desc.id,
        'patient_id': symptom_desc.patient_id,
        'symptoms_text': symptom_desc.symptoms_text,
        'parsed_keywords': symptom_desc.parsed_keywords,
        'confidence_score': float(symptom_desc.confidence_score),
        'matched_specialties': symptom_desc.matched_specialties,
        'analysis_timestamp': symptom_desc.analysis_timestamp.isoformat() if symptom_desc.analysis_timestamp else None,
        'created_at': symptom_desc.created_at.isoformat() if symptom_desc.created_at else None
    })


def handle_get_symptom(service: Any, symptom_id: str) -> Dict[str, Any]:
    """Handle get symptom request"""
    if not symptom_id:
        return create_error_response(400, "symptom_id is required")
    
    symptom_desc = service.symptom_repository.find_by_id(symptom_id)
    if not symptom_desc:
        return create_error_response(404, "Symptom description not found")
    
    return create_success_response({
        'id': symptom_desc.id,
        'patient_id': symptom_desc.patient_id,
        'symptoms_text': symptom_desc.symptoms_text,
        'parsed_keywords': symptom_desc.parsed_keywords,
        'confidence_score': float(symptom_desc.confidence_score),
        'matched_specialties': symptom_desc.matched_specialties,
        'analysis_timestamp': symptom_desc.analysis_timestamp.isoformat() if symptom_desc.analysis_timestamp else None,
        'created_at': symptom_desc.created_at.isoformat() if symptom_desc.created_at else None
    })


def handle_get_recommendations(service: Any, request_data: Dict) -> Dict[str, Any]:
    """Handle get doctor recommendations request"""
    symptom_description_id = request_data.get('symptom_description_id')
    
    if not symptom_description_id:
        return create_error_response(400, "symptom_description_id is required")
    
    recommendations = service.get_doctor_recommendations(symptom_description_id)
    
    return create_success_response({
        'id': recommendations.id,
        'symptom_description_id': recommendations.symptom_description_id,
        'patient_id': recommendations.patient_id,
        'recommended_doctors': recommendations.recommended_doctors,
        'match_scores': [float(score) for score in recommendations.match_scores],
        'available_slots': [slot.isoformat() for slot in recommendations.available_slots],
        'algorithm_version': recommendations.algorithm_version,
        'created_at': recommendations.created_at.isoformat() if recommendations.created_at else None
    })


def handle_get_recommendation(service: Any, recommendation_id: str) -> Dict[str, Any]:
    """Handle get specific recommendation request"""
    # Implementation would retrieve from recommendations repository
    return create_error_response(501, "Not implemented yet")


def handle_book_appointment(service: Any, request_data: Dict) -> Dict[str, Any]:
    """Handle appointment booking request"""
    patient_id = request_data.get('patient_id')
    doctor_id = request_data.get('doctor_id')
    appointment_datetime = request_data.get('appointment_datetime')
    symptoms = request_data.get('symptoms')
    appointment_type = request_data.get('appointment_type', 'in_person')
    
    if not all([patient_id, doctor_id, appointment_datetime, symptoms]):
        return create_error_response(400, "patient_id, doctor_id, appointment_datetime, and symptoms are required")
    
    # Parse datetime
    try:
        appointment_dt = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
    except ValueError:
        return create_error_response(400, "Invalid datetime format. Use ISO format.")
    
    appointment = service.book_appointment(patient_id, doctor_id, appointment_dt, symptoms, appointment_type)
    
    return create_success_response({
        'id': appointment.id,
        'patient_id': appointment.patient_id,
        'doctor_id': appointment.doctor_id,
        'datetime': appointment.datetime.isoformat() if appointment.datetime else None,
        'appointment_type': appointment.appointment_type.value,
        'symptoms': appointment.symptoms,
        'status': appointment.status.value,
        'reschedule_count': appointment.reschedule_count,
        'created_at': appointment.created_at.isoformat() if appointment.created_at else None
    })


def handle_get_patient_appointments(service: Any, patient_id: str) -> Dict[str, Any]:
    """Handle get patient appointments request"""
    if not patient_id:
        return create_error_response(400, "patient_id is required")
    
    appointments = service.get_patient_appointments(patient_id)
    
    return create_success_response({
        'appointments': [
            {
                'id': apt.id,
                'patient_id': apt.patient_id,
                'doctor_id': apt.doctor_id,
                'datetime': apt.datetime.isoformat() if apt.datetime else None,
                'appointment_type': apt.appointment_type.value,
                'symptoms': apt.symptoms,
                'status': apt.status.value,
                'reschedule_count': apt.reschedule_count,
                'reschedule_reason': apt.reschedule_reason,
                'created_at': apt.created_at.isoformat() if apt.created_at else None
            }
            for apt in appointments
        ]
    })


def handle_get_doctor_appointments(service: Any, doctor_id: str) -> Dict[str, Any]:
    """Handle get doctor appointments request"""
    if not doctor_id:
        return create_error_response(400, "doctor_id is required")
    
    appointments = service.get_doctor_appointments(doctor_id)
    
    return create_success_response({
        'appointments': [
            {
                'id': apt.id,
                'patient_id': apt.patient_id,
                'doctor_id': apt.doctor_id,
                'datetime': apt.datetime.isoformat() if apt.datetime else None,
                'appointment_type': apt.appointment_type.value,
                'symptoms': apt.symptoms,
                'status': apt.status.value,
                'reschedule_count': apt.reschedule_count,
                'reschedule_reason': apt.reschedule_reason,
                'created_at': apt.created_at.isoformat() if apt.created_at else None
            }
            for apt in appointments
        ]
    })


def handle_reschedule_appointment(service: Any, appointment_id: str, request_data: Dict) -> Dict[str, Any]:
    """Handle appointment rescheduling request"""
    if not appointment_id:
        return create_error_response(400, "appointment_id is required")
    
    new_datetime = request_data.get('new_datetime')
    reason = request_data.get('reason')
    
    if not new_datetime or not reason:
        return create_error_response(400, "new_datetime and reason are required")
    
    # Parse datetime
    try:
        new_dt = datetime.fromisoformat(new_datetime.replace('Z', '+00:00'))
    except ValueError:
        return create_error_response(400, "Invalid datetime format. Use ISO format.")
    
    appointment = service.reschedule_appointment(appointment_id, new_dt, reason)
    
    return create_success_response({
        'id': appointment.id,
        'patient_id': appointment.patient_id,
        'doctor_id': appointment.doctor_id,
        'datetime': appointment.datetime.isoformat() if appointment.datetime else None,
        'appointment_type': appointment.appointment_type.value,
        'symptoms': appointment.symptoms,
        'status': appointment.status.value,
        'reschedule_count': appointment.reschedule_count,
        'reschedule_reason': appointment.reschedule_reason,
        'updated_at': appointment.updated_at.isoformat() if appointment.updated_at else None
    })


def create_success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create a successful API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key'
        },
        'body': json.dumps({
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }, default=str)
    }


def handle_sync_doctor(service: Any, request_data: Dict) -> Dict[str, Any]:
    """Handle doctor sync from user management service"""
    try:
        from appointment_matching_service.repositories.dynamodb_repository import DoctorDynamoDBRepository
        
        doctor_repo = DoctorDynamoDBRepository()
        
        # Transform and create doctor
        doctor_data = {
            'id': request_data['id'],
            'name': request_data['name'],
            'email': request_data['email'],
            'phone': request_data['phone'],
            'location': request_data['location'],
            'specialties': request_data.get('specialties', []),
            'experience': request_data['experience'],
            'rating': float(request_data.get('rating', 4.5)),
            'status': request_data.get('status', 'active'),
            'created_at': request_data.get('created_at', datetime.utcnow().isoformat()),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Use DynamoDB repository directly
        import boto3
        from decimal import Decimal
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('appointment-matching-doctors')
        
        # Convert rating to Decimal for DynamoDB
        doctor_data['rating'] = Decimal(str(doctor_data['rating']))
        
        table.put_item(Item=doctor_data)
        
        return create_success_response({
            'message': f'Doctor {request_data["id"]} synced successfully',
            'doctor_id': request_data['id']
        })
        
    except Exception as e:
        return create_error_response(500, f"Failed to sync doctor: {str(e)}")

def handle_update_doctor_sync(service: Any, doctor_id: str, request_data: Dict) -> Dict[str, Any]:
    """Handle doctor update sync from user management service"""
    try:
        import boto3
        from decimal import Decimal
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('appointment-matching-doctors')
        
        # Update doctor data
        update_expression = "SET #name = :name, email = :email, phone = :phone, #location = :location, specialties = :specialties, experience = :experience, rating = :rating, #status = :status, updated_at = :updated_at"
        
        table.update_item(
            Key={'id': doctor_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames={
                '#name': 'name',
                '#location': 'location',
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':name': request_data['name'],
                ':email': request_data['email'],
                ':phone': request_data['phone'],
                ':location': request_data['location'],
                ':specialties': request_data.get('specialties', []),
                ':experience': request_data['experience'],
                ':rating': Decimal(str(request_data.get('rating', 4.5))),
                ':status': request_data.get('status', 'active'),
                ':updated_at': datetime.utcnow().isoformat()
            }
        )
        
        return create_success_response({
            'message': f'Doctor {doctor_id} updated successfully',
            'doctor_id': doctor_id
        })
        
    except Exception as e:
        return create_error_response(500, f"Failed to update doctor: {str(e)}")

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create an error API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key'
        },
        'body': json.dumps({
            'success': False,
            'error': {
                'code': status_code,
                'message': message
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    }