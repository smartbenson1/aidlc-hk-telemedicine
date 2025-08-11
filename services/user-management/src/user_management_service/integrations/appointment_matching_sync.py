"""
Direct HTTP integration with Appointment Matching Service for doctor sync
"""

import requests
import json
from typing import Dict, Any, Optional

from ..utils.logging_utils import get_logger
from ..models.doctor import Doctor

logger = get_logger(__name__)


class AppointmentMatchingSyncClient:
    """Client for syncing doctor data to Appointment Matching Service"""
    
    def __init__(self, appointment_matching_api_url: str = None):
        # Use the deployed API Gateway URL
        self.api_url = appointment_matching_api_url or "https://7ljuyzkjsd.execute-api.us-east-1.amazonaws.com/prod"
        self.timeout = 30
        
    def sync_doctor_registration(self, doctor: Doctor) -> bool:
        """Sync newly registered doctor to appointment matching service"""
        try:
            doctor_data = {
                "id": str(doctor.id),
                "name": doctor.name,
                "email": doctor.email,
                "phone": doctor.phone,
                "location": doctor.location,
                "specialties": [str(s) for s in doctor.specialties],
                "experience": doctor.experience,
                "rating": float(doctor.rating),
                "status": "active" if doctor.status.value == "ACTIVE" else "inactive"
            }
            
            # Call appointment matching service to sync doctor
            response = requests.post(
                f"{self.api_url}/doctors/sync",
                json=doctor_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Source": "user-management-service"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully synced doctor {doctor.id} to appointment matching service")
                return True
            else:
                logger.error(f"Failed to sync doctor {doctor.id}: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error syncing doctor {doctor.id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error syncing doctor {doctor.id}: {e}")
            return False
    
    def sync_doctor_update(self, doctor: Doctor) -> bool:
        """Sync doctor profile updates to appointment matching service"""
        try:
            doctor_data = {
                "id": str(doctor.id),
                "name": doctor.name,
                "email": doctor.email,
                "phone": doctor.phone,
                "location": doctor.location,
                "specialties": [str(s) for s in doctor.specialties],
                "experience": doctor.experience,
                "rating": float(doctor.rating),
                "status": "active" if doctor.status.value == "ACTIVE" else "inactive"
            }
            
            # Call appointment matching service to update doctor
            response = requests.put(
                f"{self.api_url}/doctors/{doctor.id}/sync",
                json=doctor_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Source": "user-management-service"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully updated doctor {doctor.id} in appointment matching service")
                return True
            else:
                logger.error(f"Failed to update doctor {doctor.id}: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error updating doctor {doctor.id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating doctor {doctor.id}: {e}")
            return False