"""
Appointment Booking Service

This service handles appointment booking, scheduling, and management.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
import uuid
import json

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class AppointmentBookingService:
    """
    Service for handling appointment booking operations.
    """
    
    def __init__(self):
        """Initialize the appointment booking service."""
        # For now, use a simple mock approach until DynamoDB issue is resolved
        self._appointments_cache = {}
        
        logger.info("AppointmentBookingService initialized (using mock storage)")
    
    def book_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Book a new appointment.
        
        Args:
            appointment_data: Appointment booking data
            
        Returns:
            Dict containing booking result
        """
        try:
            # Validate appointment data
            self._validate_appointment_data(appointment_data)
            
            # Check doctor availability
            if not self._check_doctor_availability(
                appointment_data['doctor_id'], 
                appointment_data['appointment_date'],
                appointment_data['appointment_time']
            ):
                return {
                    "success": False,
                    "message": "Doctor is not available at the requested time"
                }
            
            # Create appointment
            appointment_id = str(uuid.uuid4())
            appointment = {
                'appointment_id': appointment_id,
                'patient_id': appointment_data['patient_id'],
                'doctor_id': appointment_data['doctor_id'],
                'appointment_date': appointment_data['appointment_date'],
                'appointment_time': appointment_data['appointment_time'],
                'duration_minutes': appointment_data.get('duration_minutes', 30),
                'reason': appointment_data.get('reason', ''),
                'notes': appointment_data.get('notes', ''),
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Store in memory cache for now (mock implementation)
            self._appointments_cache[appointment_id] = appointment
            logger.info(f"Appointment stored in cache: {appointment_id}")
            
            logger.info(f"Appointment booked successfully: {appointment_id}")
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "message": "Appointment booked successfully",
                "appointment": appointment
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                "success": False,
                "message": f"Failed to book appointment: {str(e)}"
            }
    
    def get_appointments(self, user_id: str, user_type: str = "patient") -> List[Dict[str, Any]]:
        """
        Get appointments for a user.
        
        Args:
            user_id: User ID
            user_type: Type of user (patient or doctor)
            
        Returns:
            List of appointments
        """
        try:
            # Filter appointments from cache
            appointments = []
            for appointment in self._appointments_cache.values():
                if user_type == "patient" and appointment.get('patient_id') == user_id:
                    appointments.append(appointment)
                elif user_type == "doctor" and appointment.get('doctor_id') == user_id:
                    appointments.append(appointment)
            
            # Sort by appointment date and time
            appointments.sort(key=lambda x: f"{x.get('appointment_date', '')} {x.get('appointment_time', '')}")
            
            return appointments
            
        except Exception as e:
            logger.error(f"Error getting appointments for {user_id}: {e}")
            return []
    
    def get_doctor_availability(self, doctor_id: str, date: str) -> List[str]:
        """
        Get available time slots for a doctor on a specific date.
        
        Args:
            doctor_id: Doctor ID
            date: Date in YYYY-MM-DD format
            
        Returns:
            List of available time slots
        """
        try:
            # Get existing appointments for the doctor on this date
            try:
                response = self.appointments_client.table.scan(
                    FilterExpression="doctor_id = :doctor_id AND appointment_date = :date",
                    ExpressionAttributeValues={
                        ":doctor_id": doctor_id,
                        ":date": date
                    }
                )
                booked_times = [item['appointment_time'] for item in response.get('Items', [])]
            except Exception as scan_error:
                logger.warning(f"Error scanning appointments, using empty booked times: {scan_error}")
                booked_times = []
            
            # Generate available time slots (9 AM to 5 PM, 30-minute slots)
            available_slots = []
            start_hour = 9
            end_hour = 17
            
            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:
                    time_slot = f"{hour:02d}:{minute:02d}"
                    if time_slot not in booked_times:
                        available_slots.append(time_slot)
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting availability for doctor {doctor_id}: {e}")
            return []
    
    def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Dict containing cancellation result
        """
        try:
            # Update appointment status
            self.appointments_client.table.update_item(
                Key={'appointment_id': appointment_id},
                UpdateExpression="SET #status = :status, updated_at = :updated_at",
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'cancelled',
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Appointment cancelled: {appointment_id}")
            
            return {
                "success": True,
                "message": "Appointment cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling appointment {appointment_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to cancel appointment: {str(e)}"
            }
    
    def _validate_appointment_data(self, data: Dict[str, Any]) -> None:
        """Validate appointment booking data."""
        required_fields = ['patient_id', 'doctor_id', 'appointment_date', 'appointment_time']
        
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate date format
        try:
            datetime.strptime(data['appointment_date'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        # Validate time format
        try:
            datetime.strptime(data['appointment_time'], '%H:%M')
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM")
    
    def _check_doctor_availability(self, doctor_id: str, date: str, time: str) -> bool:
        """Check if doctor is available at the specified time."""
        try:
            # Get all appointments for this doctor on this date
            available_slots = self.get_doctor_availability(doctor_id, date)
            return time in available_slots
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return True  # Default to available if check fails