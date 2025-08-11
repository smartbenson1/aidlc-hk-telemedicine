"""
User Session Management Service for the User Management Service.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from ..models.user_session import UserSession
from ..repositories.session_repository import UserSessionRepository
from ..repositories.doctor_repository import DoctorRepository
from ..repositories.patient_repository import PatientRepository
from ..requests.response_models import SessionResponse, UserContextResponse
from ..utils.base_models import ServiceResult, SessionData, SessionValidationResult
from ..utils.enums import UserType, SessionStatus, SESSION_TIMEOUT_HOURS
from ..utils.exceptions import SessionError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class UserSessionManager:
    """Service for managing user sessions."""
    
    def __init__(self, session_repository: UserSessionRepository,
                 doctor_repository: DoctorRepository,
                 patient_repository: PatientRepository):
        """Initialize the session manager."""
        self.session_repository = session_repository
        self.doctor_repository = doctor_repository
        self.patient_repository = patient_repository
    
    def create_session(self, user_id: UUID, user_type: str,
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> ServiceResult:
        """Create a new user session."""
        try:
            logger.info(f"Creating session for user {user_id} ({user_type})")
            
            # Validate user exists
            user = self._get_user(user_id, user_type)
            if not user:
                return ServiceResult.error_result(
                    f"{user_type.capitalize()} not found",
                    "NOT_FOUND_ERROR"
                )
            
            # Validate user is active
            if not user.is_active():
                return ServiceResult.error_result(
                    f"{user_type.capitalize()} account is not active",
                    "ACCOUNT_INACTIVE"
                )
            
            # Create session data
            session_data = SessionData(
                user_name=user.name,
                user_email=user.email,
                permissions=self._get_user_permissions(user_type),
                preferences={}
            )
            
            # Create session entity
            session = UserSession(
                user_id=user_id,
                user_type=UserType(user_type),
                ip_address=ip_address,
                user_agent=user_agent
            )
            session.set_session_data(session_data)
            
            # Save session (this will cleanup any existing active sessions)
            created_session = self.session_repository.create_session_with_cleanup(session)
            logger.info(f"Session created: {created_session.id}")
            
            # Create response
            response = SessionResponse(
                session_id=created_session.id,
                user_id=created_session.user_id,
                user_type=created_session.user_type,
                expires_at=created_session.expires_at,
                created_at=created_session.created_at,
                last_accessed=created_session.last_accessed
            )
            
            return ServiceResult.success_result(response)
            
        except Exception as e:
            logger.error(f"Session creation failed: {str(e)}")
            return ServiceResult.error_result(
                "Session creation failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def validate_session(self, session_id: UUID) -> ServiceResult:
        """Validate a session and return validation result."""
        try:
            validation_result = self.session_repository.validate_session(session_id)
            
            # Convert to service result
            if validation_result['is_valid']:
                session = validation_result.get('session')
                if session:
                    response = SessionValidationResult(
                        is_valid=True,
                        user_id=session.user_id,
                        user_type=session.user_type
                    )
                else:
                    response = SessionValidationResult(
                        is_valid=True,
                        user_id=validation_result['user_id'],
                        user_type=validation_result['user_type']
                    )
            else:
                response = SessionValidationResult(
                    is_valid=False,
                    error_message=validation_result['error']
                )
            
            return ServiceResult.success_result(response)
            
        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            return ServiceResult.error_result(
                "Session validation failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def get_session_info(self, session_id: UUID) -> ServiceResult:
        """Get session information."""
        try:
            session = self.session_repository.find_by_id(session_id)
            if not session:
                return ServiceResult.error_result(
                    "Session not found",
                    "NOT_FOUND_ERROR"
                )
            
            response = SessionResponse(
                session_id=session.id,
                user_id=session.user_id,
                user_type=session.user_type,
                expires_at=session.expires_at,
                created_at=session.created_at,
                last_accessed=session.last_accessed
            )
            
            return ServiceResult.success_result(response)
            
        except Exception as e:
            logger.error(f"Failed to get session info: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve session information",
                "INTERNAL_ERROR"
            )
    
    def get_user_context(self, session_id: UUID) -> ServiceResult:
        """Get user context from session."""
        try:
            # Validate session first
            validation_result = self.session_repository.validate_session(session_id)
            if not validation_result['is_valid']:
                return ServiceResult.error_result(
                    validation_result['error'] or "Invalid session",
                    "INVALID_SESSION"
                )
            
            session = validation_result.get('session')
            if not session:
                return ServiceResult.error_result(
                    "Session data not available",
                    "SESSION_ERROR"
                )
            
            # Get session data
            session_data = session.get_session_data()
            if not session_data:
                return ServiceResult.error_result(
                    "Session data corrupted",
                    "SESSION_ERROR"
                )
            
            # Create user context response
            response = UserContextResponse(
                user_id=session.user_id,
                user_type=session.user_type,
                name=session_data.user_name,
                email=session_data.user_email,
                permissions=session_data.permissions,
                preferences=session_data.preferences
            )
            
            return ServiceResult.success_result(response)
            
        except Exception as e:
            logger.error(f"Failed to get user context: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve user context",
                "INTERNAL_ERROR"
            )
    
    def refresh_session(self, session_id: UUID) -> ServiceResult:
        """Refresh a session's expiration time."""
        try:
            refreshed_session = self.session_repository.refresh_session(session_id)
            if not refreshed_session:
                return ServiceResult.error_result(
                    "Session not found or cannot be refreshed",
                    "SESSION_ERROR"
                )
            
            response = SessionResponse(
                session_id=refreshed_session.id,
                user_id=refreshed_session.user_id,
                user_type=refreshed_session.user_type,
                expires_at=refreshed_session.expires_at,
                created_at=refreshed_session.created_at,
                last_accessed=refreshed_session.last_accessed
            )
            
            return ServiceResult.success_result(response)
            
        except Exception as e:
            logger.error(f"Session refresh failed: {str(e)}")
            return ServiceResult.error_result(
                "Session refresh failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def terminate_session(self, session_id: UUID) -> ServiceResult:
        """Terminate a session."""
        try:
            terminated = self.session_repository.terminate_session(session_id)
            if not terminated:
                return ServiceResult.error_result(
                    "Session not found",
                    "NOT_FOUND_ERROR"
                )
            
            logger.info(f"Session terminated: {session_id}")
            return ServiceResult.success_result({
                "session_id": str(session_id),
                "message": "Session terminated successfully"
            })
            
        except Exception as e:
            logger.error(f"Session termination failed: {str(e)}")
            return ServiceResult.error_result(
                "Session termination failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def terminate_user_sessions(self, user_id: UUID) -> ServiceResult:
        """Terminate all sessions for a user."""
        try:
            terminated_count = self.session_repository.terminate_user_sessions(user_id)
            
            logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
            return ServiceResult.success_result({
                "user_id": str(user_id),
                "terminated_sessions": terminated_count,
                "message": f"Terminated {terminated_count} sessions"
            })
            
        except Exception as e:
            logger.error(f"User session termination failed: {str(e)}")
            return ServiceResult.error_result(
                "User session termination failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def cleanup_expired_sessions(self) -> ServiceResult:
        """Clean up expired sessions."""
        try:
            cleaned_count = self.session_repository.cleanup_expired_sessions()
            
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return ServiceResult.success_result({
                "cleaned_sessions": cleaned_count,
                "message": f"Cleaned up {cleaned_count} expired sessions"
            })
            
        except Exception as e:
            logger.error(f"Session cleanup failed: {str(e)}")
            return ServiceResult.error_result(
                "Session cleanup failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def get_user_session_history(self, user_id: UUID, limit: int = 10) -> ServiceResult:
        """Get session history for a user."""
        try:
            sessions = self.session_repository.get_user_session_history(user_id, limit)
            
            session_history = []
            for session in sessions:
                session_info = {
                    "session_id": str(session.id),
                    "created_at": session.created_at.isoformat(),
                    "last_accessed": session.last_accessed.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "status": session.status.value,
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent
                }
                session_history.append(session_info)
            
            return ServiceResult.success_result({
                "user_id": str(user_id),
                "sessions": session_history,
                "total_sessions": len(session_history)
            })
            
        except Exception as e:
            logger.error(f"Failed to get user session history: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve session history",
                "INTERNAL_ERROR"
            )
    
    def get_active_users_count(self) -> ServiceResult:
        """Get count of users with active sessions."""
        try:
            active_count = self.session_repository.get_active_users_count()
            
            return ServiceResult.success_result({
                "active_users": active_count,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to get active users count: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve active users count",
                "INTERNAL_ERROR"
            )
    
    def detect_suspicious_activity(self) -> ServiceResult:
        """Detect suspicious session activity."""
        try:
            suspicious_activity = self.session_repository.detect_suspicious_activity()
            
            return ServiceResult.success_result(suspicious_activity)
            
        except Exception as e:
            logger.error(f"Failed to detect suspicious activity: {str(e)}")
            return ServiceResult.error_result(
                "Failed to detect suspicious activity",
                "INTERNAL_ERROR"
            )
    
    def get_session_statistics(self) -> ServiceResult:
        """Get session statistics."""
        try:
            stats = self.session_repository.get_statistics()
            
            return ServiceResult.success_result(stats)
            
        except Exception as e:
            logger.error(f"Failed to get session statistics: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve session statistics",
                "INTERNAL_ERROR"
            )
    
    def _get_user(self, user_id: UUID, user_type: str):
        """Get user by ID and type."""
        if user_type == "doctor":
            return self.doctor_repository.find_by_id(user_id)
        elif user_type == "patient":
            return self.patient_repository.find_by_id(user_id)
        else:
            return None
    
    def _get_user_permissions(self, user_type: str) -> list:
        """Get default permissions for user type."""
        if user_type == "doctor":
            return [
                "read_own_profile",
                "update_own_profile",
                "manage_own_availability",
                "view_own_appointments"
            ]
        elif user_type == "patient":
            return [
                "read_own_profile",
                "update_own_profile",
                "book_appointments",
                "view_own_appointments"
            ]
        else:
            return []