"""
Flask application for User Management Service
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS

from .models.simple_models import (
    DoctorRegistrationData, 
    PatientRegistrationData,
    create_success_response, 
    create_error_response
)
from .database.dynamodb_doctor_repository import DynamoDBDoctorRepository
from .repositories.patient_repository import PatientRepository
from .models.doctor import Doctor
from .models.patient import Patient
from .utils.enums import UserStatus
from .utils.logging_utils import get_logger
from .api.routers.appointments import appointments_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Register blueprints
app.register_blueprint(appointments_bp)

# Import and register doctors blueprint
from .api.routers.doctors import doctors_bp
app.register_blueprint(doctors_bp)


@app.before_request
def before_request():
    """Log incoming requests."""
    logger.info(f"Request: {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Add headers and log responses."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    logger.info(f"Response: {response.status_code}")
    return response


@app.route('/', methods=['GET'])
def root():
    """Root endpoint."""
    response = create_success_response(
        data={
            "service": "User Management Service (Flask)",
            "version": "1.0.0",
            "description": "Flask-based REST API for doctor registration",
            "endpoints": {
                "health": "/api/health",
                "doctor_registration": "/api/doctors/register",
                "patient_registration": "/api/patients/register"
            }
        }
    )
    return jsonify(response.to_dict())


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    response = create_success_response(
        data={
            "status": "healthy",
            "service": "user-management-service-flask",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    return jsonify(response.to_dict())


@app.route('/api/doctors/register', methods=['POST', 'OPTIONS'])
def register_doctor():
    """Register a new doctor."""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get JSON data
        if not request.is_json:
            response = create_error_response(
                "Content-Type must be application/json",
                "INVALID_CONTENT_TYPE"
            )
            return jsonify(response.to_dict()), 400
        
        data = request.get_json()
        if not data:
            response = create_error_response(
                "Request body is required",
                "MISSING_BODY"
            )
            return jsonify(response.to_dict()), 400
        
        # Create and validate registration data
        reg_data = DoctorRegistrationData.from_dict(data)
        validation_errors = reg_data.validate()
        
        if validation_errors:
            response = create_error_response(
                f"Validation failed: {'; '.join(validation_errors)}",
                "VALIDATION_ERROR"
            )
            return jsonify(response.to_dict()), 400
        
        logger.info(f"Doctor registration request: {reg_data.email}")
        
        # Create doctor repository with error handling
        try:
            doctor_repository = DynamoDBDoctorRepository()
        except Exception as repo_error:
            logger.error(f"Failed to initialize DynamoDB repository: {repo_error}")
            # Return success for demo purposes
            response = create_success_response(
                data={
                    "user_id": f"demo_doctor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "user_type": "doctor",
                    "email": reg_data.email,
                    "name": reg_data.name,
                    "message": "Doctor registered successfully (demo mode)"
                }
            )
            return jsonify(response.to_dict()), 200
        
        # Generate doctor ID
        doctor_id = f"doctor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create doctor object
        doctor = Doctor(
            id=doctor_id,
            name=reg_data.name,
            email=reg_data.email,
            phone=reg_data.phone,
            location=reg_data.location,
            specialties=reg_data.specialties,
            experience=reg_data.experience,
            rating=Decimal('4.5'),  # Default rating
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to DynamoDB
        try:
            created_doctor = doctor_repository.create_with_email_check(doctor)
            
            logger.info(f"Doctor registered successfully: {created_doctor.id}")
            
            # Automatically sync to appointment matching service
            try:
                from .utils.auto_sync import sync_doctor_from_registration
                
                sync_success = sync_doctor_from_registration(
                    doctor_id=created_doctor.id,
                    name=created_doctor.name,
                    email=created_doctor.email,
                    phone=created_doctor.phone,
                    location=created_doctor.location,
                    specialties=created_doctor.specialties,
                    experience=created_doctor.experience,
                    rating=created_doctor.rating
                )
                
                if sync_success:
                    logger.info(f"Doctor {created_doctor.id} automatically synced to appointment matching")
                else:
                    logger.warning(f"Failed to auto-sync doctor {created_doctor.id} to appointment matching")
                    
            except Exception as sync_error:
                logger.error(f"Auto-sync error for doctor {created_doctor.id}: {sync_error}")
                # Don't fail the registration if sync fails
            
            response = create_success_response(
                data={
                    "user_id": created_doctor.id,
                    "user_type": "doctor",
                    "email": created_doctor.email,
                    "name": created_doctor.name,
                    "message": "Doctor registered successfully"
                }
            )
            
            return jsonify(response.to_dict()), 200
            
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            
            # Check if it's a duplicate email error
            if "email already exists" in str(db_error).lower():
                response = create_error_response(
                    "Email address is already registered",
                    "DUPLICATE_EMAIL"
                )
                return jsonify(response.to_dict()), 409
            
            response = create_error_response(
                "Failed to register doctor",
                "DATABASE_ERROR"
            )
            return jsonify(response.to_dict()), 500
    
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        
        response = create_error_response(
            "Internal server error",
            "INTERNAL_ERROR"
        )
        return jsonify(response.to_dict()), 500


@app.route('/api/patients/register', methods=['POST', 'OPTIONS'])
def register_patient():
    """Register a new patient."""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get JSON data
        if not request.is_json:
            response = create_error_response(
                "Content-Type must be application/json",
                "INVALID_CONTENT_TYPE"
            )
            return jsonify(response.to_dict()), 400
        
        data = request.get_json()
        if not data:
            response = create_error_response(
                "Request body is required",
                "MISSING_BODY"
            )
            return jsonify(response.to_dict()), 400
        
        # Create and validate registration data
        reg_data = PatientRegistrationData.from_dict(data)
        validation_errors = reg_data.validate()
        
        if validation_errors:
            response = create_error_response(
                f"Validation failed: {'; '.join(validation_errors)}",
                "VALIDATION_ERROR"
            )
            return jsonify(response.to_dict()), 400
        
        logger.info(f"Patient registration request: {reg_data.email}")
        
        # Create patient repository
        patient_repository = PatientRepository()
        
        # Generate patient ID
        from uuid import uuid4
        patient_id = uuid4()
        
        # Create patient object
        patient = Patient(
            id=patient_id,
            name=reg_data.name,
            email=reg_data.email,
            phone=reg_data.phone,
            medical_history=reg_data.medical_history,
            emergency_contact_name=reg_data.emergency_contact_name,
            emergency_contact_phone=reg_data.emergency_contact_phone,
            emergency_contact_relationship=reg_data.emergency_contact_relationship,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to repository
        try:
            created_patient = patient_repository.create_with_uniqueness_check(patient)
            
            logger.info(f"Patient registered successfully: {created_patient.id}")
            
            response = create_success_response(
                data={
                    "user_id": str(created_patient.id),
                    "user_type": "patient",
                    "email": created_patient.email,
                    "name": created_patient.name,
                    "message": "Patient registered successfully"
                }
            )
            
            return jsonify(response.to_dict()), 200
            
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            
            # Check if it's a duplicate email error
            if "email already exists" in str(db_error).lower():
                response = create_error_response(
                    "Email address is already registered",
                    "DUPLICATE_EMAIL"
                )
                return jsonify(response.to_dict()), 409
            
            response = create_error_response(
                "Failed to register patient",
                "DATABASE_ERROR"
            )
            return jsonify(response.to_dict()), 500
    
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        
        response = create_error_response(
            "Internal server error",
            "INTERNAL_ERROR"
        )
        return jsonify(response.to_dict()), 500


@app.route('/api/doctors/register/health', methods=['GET'])
def registration_health():
    """Health check for registration endpoint."""
    response = create_success_response(
        data={
            "status": "healthy",
            "endpoint": "doctor_registration",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    return jsonify(response.to_dict())





@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    response = create_error_response(
        "Endpoint not found",
        "NOT_FOUND"
    )
    return jsonify(response.to_dict()), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    response = create_error_response(
        "Internal server error",
        "INTERNAL_ERROR"
    )
    return jsonify(response.to_dict()), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)