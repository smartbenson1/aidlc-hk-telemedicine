"""
Appointment Service Integration for the User Management Service.
"""

import logging
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from ..utils.base_models import ServiceResult, ConflictCheckResult, RetryConfig, CircuitBreakerState
from ..utils.exceptions import IntegrationError
from ..utils.enums import SERVICE_TIMEOUTS

logger = logging.getLogger(__name__)


class AppointmentServiceIntegration:
    """Integration service for communicating with the Appointment Service."""
    
    def __init__(self, base_url: str = "http://localhost:8081",
                 api_key: Optional[str] = None,
                 timeout_seconds: int = SERVICE_TIMEOUTS["appointment_service"]):
        """Initialize the appointment service integration."""
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
    
    def check_appointment_conflicts(self, doctor_id: UUID, datetime_slot: datetime) -> ConflictCheckResult:
        """Check if a time slot conflicts with existing appointments."""
        try:
            logger.info(f"Checking appointment conflicts for doctor {doctor_id} at {datetime_slot}")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                logger.warning("Appointment Service unavailable, assuming no conflicts")
                return ConflictCheckResult(
                    has_conflict=False,
                    message="Could not verify conflicts - service unavailable"
                )
            
            # Prepare request data
            conflict_check_data = {
                "doctor_id": str(doctor_id),
                "datetime": datetime_slot.isoformat(),
                "check_window_minutes": 60  # Check for 1-hour conflicts
            }
            
            # Make request with retry logic
            for attempt in range(1, self.retry_config.max_attempts + 1):
                try:
                    response = self._make_request(
                        "POST",
                        f"{self.base_url}/api/v1/appointments/check-conflicts",
                        json=conflict_check_data
                    )
                    
                    if response['status_code'] == 200:
                        conflict_data = response['json']()
                        
                        self.circuit_breaker.record_success()
                        
                        return ConflictCheckResult(
                            has_conflict=conflict_data.get("has_conflict", False),
                            conflicting_appointments=conflict_data.get("conflicting_appointments", []),
                            message=conflict_data.get("message", "Conflict check completed")
                        )
                    
                    elif response['status_code'] == 404:
                        # Endpoint not found, assume no conflicts
                        logger.warning("Conflict check endpoint not found, assuming no conflicts")
                        return ConflictCheckResult(
                            has_conflict=False,
                            message="Conflict check endpoint not available"
                        )
                    
                    else:
                        # Server error, retry if possible
                        if attempt < self.retry_config.max_attempts:
                            delay = self.retry_config.get_delay(attempt)
                            logger.warning(f"Conflict check failed (attempt {attempt}), retrying in {delay}s")
                            import time
                            time.sleep(delay)
                            continue
                        else:
                            self.circuit_breaker.record_failure()
                            logger.error(f"Conflict check failed after {attempt} attempts")
                            return ConflictCheckResult(
                                has_conflict=False,
                                message=f"Could not verify conflicts - service error {response['status_code']}"
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
            logger.warning("Appointment Service request timed out, assuming no conflicts")
            return ConflictCheckResult(
                has_conflict=False,
                message="Could not verify conflicts - request timed out"
            )
        
        except ConnectionError:
            self.circuit_breaker.record_failure()
            logger.warning("Could not connect to Appointment Service, assuming no conflicts")
            return ConflictCheckResult(
                has_conflict=False,
                message="Could not verify conflicts - connection error"
            )
        
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to check appointment conflicts: {str(e)}")
            return ConflictCheckResult(
                has_conflict=False,
                message=f"Could not verify conflicts - {str(e)}"
            )
    
    def get_doctor_appointments(self, doctor_id: UUID, start_date: datetime, 
                              end_date: datetime) -> ServiceResult:
        """Get appointments for a doctor within a date range."""
        try:
            logger.info(f"Getting appointments for doctor {doctor_id} from {start_date} to {end_date}")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                return ServiceResult.error_result(
                    "Appointment Service is currently unavailable",
                    "SERVICE_UNAVAILABLE"
                )
            
            # Prepare query parameters
            params = {
                "doctor_id": str(doctor_id),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            response = self._make_request(
                "GET",
                f"{self.base_url}/api/v1/appointments",
                params=params
            )
            
            if response['status_code'] == 200:
                appointments_data = response['json']()
                
                self.circuit_breaker.record_success()
                
                return ServiceResult.success_result({
                    "appointments": appointments_data.get("appointments", []),
                    "total_count": appointments_data.get("total_count", 0),
                    "doctor_id": str(doctor_id),
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "retrieved_at": datetime.utcnow().isoformat()
                })
            
            elif response['status_code'] == 404:
                # No appointments found
                return ServiceResult.success_result({
                    "appointments": [],
                    "total_count": 0,
                    "doctor_id": str(doctor_id),
                    "message": "No appointments found for the specified period"
                })
            
            else:
                self.circuit_breaker.record_failure()
                return ServiceResult.error_result(
                    f"Appointment Service returned error: {response['status_code']}",
                    "SERVICE_ERROR"
                )
                
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to get doctor appointments: {str(e)}")
            return ServiceResult.error_result(
                "Failed to get appointments from Appointment Service",
                "INTEGRATION_ERROR"
            )
    
    def notify_availability_change(self, doctor_id: UUID, availability_change: Dict[str, Any]) -> ServiceResult:
        """Notify Appointment Service of availability changes."""
        try:
            logger.info(f"Notifying Appointment Service of availability change for doctor {doctor_id}")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                logger.warning("Appointment Service unavailable, skipping availability notification")
                return ServiceResult.success_result({
                    "notified": False,
                    "reason": "Service unavailable"
                })
            
            # Prepare notification data
            notification_data = {
                "doctor_id": str(doctor_id),
                "change_type": availability_change.get("change_type", "modified"),
                "availability_id": availability_change.get("availability_id"),
                "datetime": availability_change.get("datetime"),
                "appointment_type": availability_change.get("appointment_type"),
                "specialty_id": availability_change.get("specialty_id"),
                "status": availability_change.get("status"),
                "notification_time": datetime.utcnow().isoformat(),
                "source_service": "user-management"
            }
            
            response = self._make_request(
                "POST",
                f"{self.base_url}/api/v1/availability/notifications",
                json=notification_data
            )
            
            if response['status_code'] in [200, 201]:
                self.circuit_breaker.record_success()
                return ServiceResult.success_result({
                    "notified": True,
                    "doctor_id": str(doctor_id),
                    "change_type": availability_change.get("change_type"),
                    "notified_at": datetime.utcnow().isoformat()
                })
            else:
                # Non-critical failure, don't break circuit
                logger.warning(f"Failed to notify availability change: {response['status_code']}")
                return ServiceResult.success_result({
                    "notified": False,
                    "reason": f"Service returned {response['status_code']}"
                })
                
        except Exception as e:
            logger.warning(f"Failed to notify availability change: {str(e)}")
            # Non-critical failure, return success but indicate not notified
            return ServiceResult.success_result({
                "notified": False,
                "reason": str(e)
            })
    
    def get_appointment_statistics(self, doctor_id: Optional[UUID] = None) -> ServiceResult:
        """Get appointment statistics from Appointment Service."""
        try:
            logger.info("Getting appointment statistics from Appointment Service")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                return ServiceResult.error_result(
                    "Appointment Service is currently unavailable",
                    "SERVICE_UNAVAILABLE"
                )
            
            # Prepare query parameters
            params = {}
            if doctor_id:
                params["doctor_id"] = str(doctor_id)
            
            response = self._make_request(
                "GET",
                f"{self.base_url}/api/v1/appointments/statistics",
                params=params
            )
            
            if response['status_code'] == 200:
                stats_data = response['json']()
                
                self.circuit_breaker.record_success()
                
                return ServiceResult.success_result({
                    "statistics": stats_data,
                    "doctor_id": str(doctor_id) if doctor_id else None,
                    "retrieved_at": datetime.utcnow().isoformat()
                })
            
            else:
                self.circuit_breaker.record_failure()
                return ServiceResult.error_result(
                    f"Appointment Service returned error: {response['status_code']}",
                    "SERVICE_ERROR"
                )
                
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to get appointment statistics: {str(e)}")
            return ServiceResult.error_result(
                "Failed to get statistics from Appointment Service",
                "INTEGRATION_ERROR"
            )
    
    def validate_appointment_booking(self, doctor_id: UUID, patient_id: UUID, 
                                   datetime_slot: datetime) -> ServiceResult:
        """Validate that an appointment can be booked."""
        try:
            logger.info(f"Validating appointment booking for doctor {doctor_id}, patient {patient_id}")
            
            # Check circuit breaker
            if self.circuit_breaker.is_open:
                return ServiceResult.error_result(
                    "Appointment Service is currently unavailable",
                    "SERVICE_UNAVAILABLE"
                )
            
            # Prepare validation data
            validation_data = {
                "doctor_id": str(doctor_id),
                "patient_id": str(patient_id),
                "datetime": datetime_slot.isoformat()
            }
            
            response = self._make_request(
                "POST",
                f"{self.base_url}/api/v1/appointments/validate-booking",
                json=validation_data
            )
            
            if response['status_code'] == 200:
                validation_result = response['json']()
                
                self.circuit_breaker.record_success()
                
                return ServiceResult.success_result({
                    "can_book": validation_result.get("can_book", False),
                    "validation_errors": validation_result.get("errors", []),
                    "message": validation_result.get("message", "Validation completed"),
                    "validated_at": datetime.utcnow().isoformat()
                })
            
            else:
                self.circuit_breaker.record_failure()
                return ServiceResult.error_result(
                    f"Appointment Service returned error: {response['status_code']}",
                    "SERVICE_ERROR"
                )
                
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to validate appointment booking: {str(e)}")
            return ServiceResult.error_result(
                "Failed to validate booking with Appointment Service",
                "INTEGRATION_ERROR"
            )
    
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
        """Check if Appointment Service is healthy."""
        try:
            response = self._make_request("GET", f"{self.base_url}/health")
            
            if response['status_code'] == 200:
                health_data = response['json']()
                return ServiceResult.success_result({
                    "status": "healthy",
                    "service": "appointment-service",
                    "response_time_ms": 0,  # urllib doesn't provide elapsed time
                    "details": health_data
                })
            else:
                return ServiceResult.error_result(
                    f"Appointment Service health check failed: {response['status_code']}",
                    "HEALTH_CHECK_FAILED"
                )
                
        except Exception as e:
            return ServiceResult.error_result(
                f"Appointment Service health check failed: {str(e)}",
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