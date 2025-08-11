"""
Appointment API endpoints.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from flask import Blueprint, request, jsonify

from ...services.appointment_service import AppointmentBookingService
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

# Create blueprint
appointments_bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')

# Initialize service
appointment_service = AppointmentBookingService()


@appointments_bp.route('', methods=['POST'])
def book_appointment():
    """Book a new appointment."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        result = appointment_service.book_appointment(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in book_appointment: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@appointments_bp.route('', methods=['GET'])
def get_appointments():
    """Get appointments for a user."""
    try:
        user_id = request.args.get('user_id')
        user_type = request.args.get('user_type', 'patient')
        
        if not user_id:
            return jsonify({
                "success": False,
                "message": "user_id parameter is required"
            }), 400
        
        appointments = appointment_service.get_appointments(user_id, user_type)
        
        return jsonify({
            "success": True,
            "appointments": appointments
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_appointments: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@appointments_bp.route('/availability/<doctor_id>', methods=['GET'])
def get_doctor_availability(doctor_id: str):
    """Get available time slots for a doctor."""
    try:
        date = request.args.get('date')
        
        if not date:
            return jsonify({
                "success": False,
                "message": "date parameter is required"
            }), 400
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid date format. Use YYYY-MM-DD"
            }), 400
        
        available_slots = appointment_service.get_doctor_availability(doctor_id, date)
        
        return jsonify({
            "success": True,
            "available_slots": available_slots,
            "date": date,
            "doctor_id": doctor_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_doctor_availability: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@appointments_bp.route('/<appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id: str):
    """Cancel an appointment."""
    try:
        result = appointment_service.cancel_appointment(appointment_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in cancel_appointment: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@appointments_bp.route('/<appointment_id>', methods=['GET'])
def get_appointment(appointment_id: str):
    """Get a specific appointment."""
    try:
        # Get appointment from DynamoDB
        response = appointment_service.appointments_client.table.get_item(
            Key={'appointment_id': appointment_id}
        )
        
        appointment = response.get('Item')
        
        if not appointment:
            return jsonify({
                "success": False,
                "message": "Appointment not found"
            }), 404
        
        return jsonify({
            "success": True,
            "appointment": appointment
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_appointment: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500