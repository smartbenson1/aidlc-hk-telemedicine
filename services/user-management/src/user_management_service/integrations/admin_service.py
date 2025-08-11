"""
Administration Service Integration for the User Management Service.
"""

import logging
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from ..models.medical_specialty import MedicalSpecialty
from ..utils.base_models import ServiceResult, RetryConfig, CircuitBreakerState
from ..utils.exceptions import IntegrationError
from ..utils.enums import SERVICE_TIMEOUTS

logger = logging.getLogger(__name__)


class AdministrationServiceIntegration:
    """Integration service for communicating with the Administration Service."""
    
    def __init__(self, base_url: str = "http://localhost:8080",
                 api_key: Optional[str] = None,
                 timeout_seconds: int = SERVICE_TIMEOUTS["admin_service"]):
        """Initialize the administration service integration."""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.retry_config = RetryConfig()
        self.circuit_breaker = CircuitBreakerState()
        
        # Default headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "UserManagementService/1.0"
        }
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def fetch_active_specialties(self) -> ServiceResult:
        """Fetch active medical specialties from Administration Service."""
        try:
            logger.info("Fetching active specialties from Administration Service")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                return ServiceResult.error_result(
                    "Administration Service is currently unavailable (circuit breaker open)",
                    "SERVICE_UNAVAILABLE"
                )
            
            # Make HTTP request with retry logic
            for attempt in range(1, self.retry_config.max_attempts + 1):
                try:
                    response = self._make_request(
                        "GET",
                        f"{self.base_url}/api/v1/specialties",
                        params={"status": "active"}
                    )
                    
                    if response['status_code'] == 200:
                        specialties_data = response['json']()
                        
                        # Convert to MedicalSpecialty objects
                        specialties = []
                        for specialty_data in specialties_data.get("specialties", []):
                            specialty = MedicalSpecialty(
                                name=specialty_data["name"],
                                description=specialty_data.get("description", ""),
                                status=specialty_data.get("status", "active")
                            )
                            # Set ID if provided
                            if "id" in specialty_data:
                                specialty.id = UUID(specialty_data["id"])
                            
                            specialties.append(specialty)
                        
                        self.circuit_breaker.record_success()
                        logger.info(f"Successfully fetched {len(specialties)} specialties")
                        
                        return ServiceResult.success_result({
                            "specialties": [s.to_dict() for s in specialties],
                            "total_count": len(specialties),
                            "fetched_at": datetime.utcnow().isoformat()
                        })
                    
                    elif response['status_code'] == 404:
                        # Service endpoint not found
                        return ServiceResult.error_result(
                            "Specialties endpoint not found in Administration Service",
                            "ENDPOINT_NOT_FOUND"
                        )
                    
                    else:
                        # Server error, retry if possible
                        if attempt < self.retry_config.max_attempts:
                            delay = self.retry_config.get_delay(attempt)
                            logger.warning(f"Request failed (attempt {attempt}), retrying in {delay}s")
                            import time
                            time.sleep(delay)
                            continue
                        else:
                            self.circuit_breaker.record_failure()
                            return ServiceResult.error_result(
                                f"Administration Service returned error: {response['status_code']}",
                                "SERVICE_ERROR",
                                {"status_code": response['status_code'], "response": response['text']}
                            )
                
                except (urllib.error.URLError, ConnectionError) as e:
                    if attempt < self.retry_config.max_attempts:
                        delay = self.retry_config.get_delay(attempt)
                        logger.warning(f"Request failed (attempt {attempt}): {str(e)}, retrying in {delay}s")
                        import time
                        time.sleep(delay)
                        continue
                    else:
                        self.circuit_breaker.record_failure()
                        raise
            
        except (urllib.error.URLError, TimeoutError):
            self.circuit_breaker.record_failure()
            return ServiceResult.error_result(
                "Administration Service request timed out",
                "TIMEOUT_ERROR"
            )
        
        except ConnectionError:
            self.circuit_breaker.record_failure()
            return ServiceResult.error_result(
                "Could not connect to Administration Service",
                "CONNECTION_ERROR"
            )
        
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to fetch specialties: {str(e)}")
            return ServiceResult.error_result(
                "Failed to fetch specialties from Administration Service",
                "INTEGRATION_ERROR",
                {"error": str(e)}
            )
    
    def validate_specialty_exists(self, specialty_id: UUID) -> ServiceResult:
        """Validate that a specialty exists and is active."""
        try:
            logger.info(f"Validating specialty {specialty_id} with Administration Service")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                return ServiceResult.error_result(
                    "Administration Service is currently unavailable",
                    "SERVICE_UNAVAILABLE"
                )
            
            response = self._make_request(
                "GET",
                f"{self.base_url}/api/v1/specialties/{specialty_id}"
            )
            
            if response['status_code'] == 200:
                specialty_data = response['json']()
                is_active = specialty_data.get("status") == "active"
                
                self.circuit_breaker.record_success()
                
                return ServiceResult.success_result({
                    "specialty_id": str(specialty_id),
                    "exists": True,
                    "is_active": is_active,
                    "name": specialty_data.get("name"),
                    "validated_at": datetime.utcnow().isoformat()
                })
            
            elif response['status_code'] == 404:
                return ServiceResult.success_result({
                    "specialty_id": str(specialty_id),
                    "exists": False,
                    "is_active": False,
                    "validated_at": datetime.utcnow().isoformat()
                })
            
            else:
                self.circuit_breaker.record_failure()
                return ServiceResult.error_result(
                    f"Administration Service returned error: {response['status_code']}",
                    "SERVICE_ERROR"
                )
                
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to validate specialty: {str(e)}")
            return ServiceResult.error_result(
                "Failed to validate specialty with Administration Service",
                "INTEGRATION_ERROR"
            )
    
    def get_specialty_details(self, specialty_ids: List[UUID]) -> ServiceResult:
        """Get details for multiple specialties."""
        try:
            logger.info(f"Getting details for {len(specialty_ids)} specialties")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                return ServiceResult.error_result(
                    "Administration Service is currently unavailable",
                    "SERVICE_UNAVAILABLE"
                )
            
            # For demo purposes, we'll make individual requests
            # In a real implementation, you might have a batch endpoint
            specialty_details = []
            
            for specialty_id in specialty_ids:
                try:
                    response = self._make_request(
                        "GET",
                        f"{self.base_url}/api/v1/specialties/{specialty_id}"
                    )
                    
                    if response['status_code'] == 200:
                        specialty_data = response['json']()
                        specialty_details.append({
                            "id": str(specialty_id),
                            "name": specialty_data.get("name", "Unknown"),
                            "description": specialty_data.get("description", "")
                        })
                    else:
                        # If specialty not found, add placeholder
                        specialty_details.append({
                            "id": str(specialty_id),
                            "name": "Unknown Specialty",
                            "description": "Specialty details not available"
                        })
                
                except Exception as e:
                    logger.warning(f"Failed to get details for specialty {specialty_id}: {str(e)}")
                    specialty_details.append({
                        "id": str(specialty_id),
                        "name": "Unknown Specialty",
                        "description": "Error retrieving specialty details"
                    })
            
            self.circuit_breaker.record_success()
            
            return ServiceResult.success_result({
                "specialty_details": specialty_details,
                "requested_count": len(specialty_ids),
                "retrieved_count": len(specialty_details),
                "retrieved_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to get specialty details: {str(e)}")
            return ServiceResult.error_result(
                "Failed to get specialty details from Administration Service",
                "INTEGRATION_ERROR"
            )
    
    def report_user_registration(self, user, user_type: str) -> ServiceResult:
        """Report user registration to Administration Service for analytics."""
        try:
            logger.info(f"Reporting {user_type} registration to Administration Service")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                logger.warning("Administration Service unavailable, skipping registration report")
                return ServiceResult.success_result({
                    "reported": False,
                    "reason": "Service unavailable"
                })
            
            # Prepare registration data
            registration_data = {
                "user_id": str(user.id),
                "user_type": user_type,
                "email": user.email,
                "name": user.name,
                "registration_date": user.created_at.isoformat(),
                "source_service": "user-management"
            }
            
            # Add user-type specific data
            if user_type == "doctor" and hasattr(user, 'specialties'):
                registration_data["specialties"] = [str(s) for s in user.specialties]
                registration_data["location"] = user.location
            
            response = self._make_request(
                "POST",
                f"{self.base_url}/api/v1/analytics/user-registrations",
                json=registration_data
            )
            
            if response['status_code'] in [200, 201]:
                self.circuit_breaker.record_success()
                return ServiceResult.success_result({
                    "reported": True,
                    "user_id": str(user.id),
                    "reported_at": datetime.utcnow().isoformat()
                })
            else:
                # Non-critical failure, don't break circuit
                logger.warning(f"Failed to report registration: {response['status_code']}")
                return ServiceResult.success_result({
                    "reported": False,
                    "reason": f"Service returned {response['status_code']}"
                })
                
        except Exception as e:
            logger.warning(f"Failed to report user registration: {str(e)}")
            # Non-critical failure, return success but indicate not reported
            return ServiceResult.success_result({
                "reported": False,
                "reason": str(e)
            })
    
    def report_profile_update(self, user, changes: Dict[str, Any]) -> ServiceResult:
        """Report profile update to Administration Service for analytics."""
        try:
            logger.info(f"Reporting profile update to Administration Service")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                logger.warning("Administration Service unavailable, skipping profile update report")
                return ServiceResult.success_result({
                    "reported": False,
                    "reason": "Service unavailable"
                })
            
            # Prepare update data
            update_data = {
                "user_id": str(user.id),
                "user_type": "doctor" if hasattr(user, 'specialties') else "patient",
                "changed_fields": changes.get("changed_fields", []),
                "update_date": datetime.utcnow().isoformat(),
                "source_service": "user-management"
            }
            
            response = self._make_request(
                "POST",
                f"{self.base_url}/api/v1/analytics/profile-updates",
                json=update_data
            )
            
            if response['status_code'] in [200, 201]:
                self.circuit_breaker.record_success()
                return ServiceResult.success_result({
                    "reported": True,
                    "user_id": str(user.id),
                    "reported_at": datetime.utcnow().isoformat()
                })
            else:
                logger.warning(f"Failed to report profile update: {response['status_code']}")
                return ServiceResult.success_result({
                    "reported": False,
                    "reason": f"Service returned {response['status_code']}"
                })
                
        except Exception as e:
            logger.warning(f"Failed to report profile update: {str(e)}")
            return ServiceResult.success_result({
                "reported": False,
                "reason": str(e)
            })
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with common configuration using urllib."""
        headers = kwargs.get("headers", self.headers)
        timeout = kwargs.get("timeout", self.timeout_seconds)
        data = kwargs.get("json")
        
        try:
            # Prepare request
            if data:
                data = json.dumps(data).encode('utf-8')
                headers = headers.copy()
                headers['Content-Type'] = 'application/json'
            
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            
            # Make request
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_data = response.read().decode('utf-8')
                return {
                    'status_code': response.status,
                    'text': response_data,
                    'json': lambda: json.loads(response_data) if response_data else {}
                }
                
        except urllib.error.HTTPError as e:
            return {
                'status_code': e.code,
                'text': e.read().decode('utf-8') if e.fp else '',
                'json': lambda: {}
            }
        except urllib.error.URLError as e:
            raise ConnectionError(f"Connection failed: {e}")
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def health_check(self) -> ServiceResult:
        """Check if Administration Service is healthy."""
        try:
            response = self._make_request("GET", f"{self.base_url}/health")
            
            if response['status_code'] == 200:
                health_data = response['json']()
                return ServiceResult.success_result({
                    "status": "healthy",
                    "service": "administration-service",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "details": health_data
                })
            else:
                return ServiceResult.error_result(
                    f"Administration Service health check failed: {response['status_code']}",
                    "HEALTH_CHECK_FAILED"
                )
                
        except Exception as e:
            return ServiceResult.error_result(
                f"Administration Service health check failed: {str(e)}",
                "HEALTH_CHECK_ERROR"
            )
    
    def get_service_info(self) -> ServiceResult:
        """Get service configuration information."""
        return ServiceResult.success_result({
            "base_url": self.base_url,
            "timeout_seconds": self.timeout_seconds,
            "has_api_key": bool(self.api_key),
            "circuit_breaker_open": self.circuit_breaker.is_open,
            "circuit_breaker_failures": self.circuit_breaker.failure_count
        })