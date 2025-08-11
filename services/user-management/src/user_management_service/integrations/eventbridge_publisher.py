"""
AWS EventBridge integration for publishing user management events
"""

import boto3
import json
from datetime import datetime
from typing import Dict, Any, Optional

from ..utils.logging_utils import get_logger
from ..models.doctor import Doctor
from ..models.patient import Patient

logger = get_logger(__name__)


class EventBridgePublisher:
    """Publisher for AWS EventBridge events"""
    
    def __init__(self, event_bus_name: str = "healmatch-events"):
        self.eventbridge = boto3.client('events')
        self.event_bus_name = event_bus_name
        self.source = "user-management-service"
        
    def publish_doctor_registered_event(self, doctor: Doctor) -> bool:
        """Publish doctor registration event to EventBridge"""
        try:
            event_detail = {
                "doctor_id": str(doctor.id),
                "name": doctor.name,
                "email": doctor.email,
                "phone": doctor.phone,
                "location": doctor.location,
                "specialties": [str(s) for s in doctor.specialties],
                "experience": doctor.experience,
                "rating": float(doctor.rating),
                "status": doctor.status.value if hasattr(doctor.status, 'value') else str(doctor.status),
                "created_at": doctor.created_at.isoformat() if doctor.created_at else datetime.utcnow().isoformat(),
                "event_timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.eventbridge.put_events(
                Entries=[
                    {
                        'Source': self.source,
                        'DetailType': 'Doctor Registered',
                        'Detail': json.dumps(event_detail),
                        'EventBusName': self.event_bus_name,
                        'Resources': [
                            f"arn:aws:dynamodb:*:*:table/user-management-users"
                        ]
                    }
                ]
            )
            
            if response['FailedEntryCount'] == 0:
                logger.info(f"Successfully published doctor registration event for {doctor.id}")
                return True
            else:
                logger.error(f"Failed to publish doctor registration event: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing doctor registration event: {e}")
            return False
    
    def publish_doctor_updated_event(self, doctor: Doctor) -> bool:
        """Publish doctor update event to EventBridge"""
        try:
            event_detail = {
                "doctor_id": str(doctor.id),
                "name": doctor.name,
                "email": doctor.email,
                "phone": doctor.phone,
                "location": doctor.location,
                "specialties": [str(s) for s in doctor.specialties],
                "experience": doctor.experience,
                "rating": float(doctor.rating),
                "status": doctor.status.value if hasattr(doctor.status, 'value') else str(doctor.status),
                "updated_at": doctor.updated_at.isoformat() if doctor.updated_at else datetime.utcnow().isoformat(),
                "event_timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.eventbridge.put_events(
                Entries=[
                    {
                        'Source': self.source,
                        'DetailType': 'Doctor Updated',
                        'Detail': json.dumps(event_detail),
                        'EventBusName': self.event_bus_name
                    }
                ]
            )
            
            if response['FailedEntryCount'] == 0:
                logger.info(f"Successfully published doctor update event for {doctor.id}")
                return True
            else:
                logger.error(f"Failed to publish doctor update event: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing doctor update event: {e}")
            return False
    
    def publish_patient_registered_event(self, patient: Patient) -> bool:
        """Publish patient registration event to EventBridge"""
        try:
            event_detail = {
                "patient_id": str(patient.id),
                "name": patient.name,
                "email": patient.email,
                "phone": patient.phone,
                "medical_history": patient.medical_history,
                "emergency_contact": {
                    "name": patient.emergency_contact_name,
                    "phone": patient.emergency_contact_phone,
                    "relationship": patient.emergency_contact_relationship
                },
                "status": patient.status.value if hasattr(patient.status, 'value') else str(patient.status),
                "created_at": patient.created_at.isoformat() if patient.created_at else datetime.utcnow().isoformat(),
                "event_timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.eventbridge.put_events(
                Entries=[
                    {
                        'Source': self.source,
                        'DetailType': 'Patient Registered',
                        'Detail': json.dumps(event_detail),
                        'EventBusName': self.event_bus_name
                    }
                ]
            )
            
            if response['FailedEntryCount'] == 0:
                logger.info(f"Successfully published patient registration event for {patient.id}")
                return True
            else:
                logger.error(f"Failed to publish patient registration event: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing patient registration event: {e}")
            return False