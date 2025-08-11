"""
Automatic sync utility for syncing doctors to appointment matching service
"""

import boto3
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def sync_doctor_to_appointment_matching(doctor_data: Dict[str, Any]) -> bool:
    """
    Automatically sync a doctor to the appointment matching service.
    
    Args:
        doctor_data: Doctor data from user management service
        
    Returns:
        bool: True if sync successful, False otherwise
    """
    try:
        # Initialize DynamoDB resource
        dynamodb = boto3.resource('dynamodb')
        appointment_table = dynamodb.Table('appointment-matching-doctors')
        
        # Transform doctor data for appointment matching table
        appointment_doctor = {
            'id': doctor_data['id'],
            'name': doctor_data['name'],
            'email': doctor_data['email'],
            'phone': doctor_data.get('phone', ''),
            'location': doctor_data.get('location', ''),
            'specialties': doctor_data.get('specialties', []),
            'experience': doctor_data.get('experience', ''),
            'rating': Decimal(str(doctor_data.get('rating', 4.5))),
            'status': 'active',  # Set as active for appointment matching
            'created_at': doctor_data.get('created_at', datetime.utcnow().isoformat()),
            'updated_at': datetime.utcnow().isoformat(),
            'user_type': 'doctor'
        }
        
        # Save to appointment matching table
        appointment_table.put_item(Item=appointment_doctor)
        
        logger.info(f"Successfully synced doctor {doctor_data['id']} to appointment matching service")
        return True
        
    except Exception as e:
        logger.error(f"Failed to sync doctor {doctor_data.get('id', 'unknown')} to appointment matching: {e}")
        return False


def sync_doctor_from_registration(doctor_id: str, name: str, email: str, phone: str, 
                                location: str, specialties: list, experience: str, 
                                rating: Decimal = Decimal('4.5')) -> bool:
    """
    Sync a doctor to appointment matching service directly from registration data.
    
    Args:
        doctor_id: Doctor ID
        name: Doctor name
        email: Doctor email
        phone: Doctor phone
        location: Doctor location
        specialties: List of specialties
        experience: Doctor experience
        rating: Doctor rating (default 4.5)
        
    Returns:
        bool: True if sync successful, False otherwise
    """
    doctor_data = {
        'id': doctor_id,
        'name': name,
        'email': email,
        'phone': phone,
        'location': location,
        'specialties': specialties,
        'experience': experience,
        'rating': rating,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    return sync_doctor_to_appointment_matching(doctor_data)