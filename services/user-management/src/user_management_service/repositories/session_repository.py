"""
User Session repository implementation for the User Management Service.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from .base_repository import InMemoryRepository
from ..models.user_session import UserSession
from ..utils.enums import UserType, SessionStatus
from ..utils.exceptions import BusinessRuleError


class UserSessionRepository(InMemoryRepository[UserSession]):
    """Repository for User Session entities."""
    
    def __init__(self):
        """Initialize the user session repository."""
        super().__init__("UserSession", "user_sessions.json")
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> UserSession:
        """Deserialize user session from dictionary data."""
        return UserSession.from_dict(data)
    
    def find_by_user(self, user_id: UUID) -> List[UserSession]:
        """Find all sessions for a user."""
        return self.find_by_field("user_id", user_id)
    
    def find_active_session_by_user(self, user_id: UUID) -> Optional[UserSession]:
        """Find active session for a user (assuming one active session per user)."""
        sessions = self.find_by_user(user_id)
        for session in sessions:
            if session.is_active():
                return session
        return None
    
    def find_by_status(self, status: SessionStatus) -> List[UserSession]:
        """Find sessions by status."""
        return self.find_by_field("status", status)
    
    def find_active_sessions(self) -> List[UserSession]:
        """Find all active sessions."""
        active_sessions = []
        for session in self.find_by_status(SessionStatus.ACTIVE):
            if not session.is_expired():
                active_sessions.append(session)
        return active_sessions
    
    def find_expired_sessions(self) -> List[UserSession]:
        """Find sessions that have expired but are still marked as active."""
        expired_sessions = []
        for session in self.find_by_status(SessionStatus.ACTIVE):
            if session.is_expired():
                expired_sessions.append(session)
        return expired_sessions
    
    def find_by_user_type(self, user_type: UserType) -> List[UserSession]:
        """Find sessions by user type."""
        return self.find_by_field("user_type", user_type)
    
    def find_by_ip_address(self, ip_address: str) -> List[UserSession]:
        """Find sessions by IP address."""
        return self.find_by_field("ip_address", ip_address)
    
    def find_sessions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[UserSession]:
        """Find sessions created within a date range."""
        results = []
        for session in self.find_all():
            if start_date <= session.created_at <= end_date:
                results.append(session)
        return sorted(results, key=lambda s: s.created_at, reverse=True)
    
    def create_session_with_cleanup(self, session: UserSession) -> UserSession:
        """Create session and cleanup any existing active sessions for the user."""
        # Find existing active session for the user
        existing_session = self.find_active_session_by_user(session.user_id)
        if existing_session:
            # Terminate the existing session
            existing_session.terminate()
            self.update(existing_session)
        
        return self.create(session)
    
    def validate_session(self, session_id: UUID) -> Dict[str, Any]:
        """Validate a session and return validation result."""
        session = self.find_by_id(session_id)
        
        if not session:
            return {
                'is_valid': False,
                'error': 'Session not found',
                'user_id': None,
                'user_type': None
            }
        
        if session.is_terminated():
            return {
                'is_valid': False,
                'error': 'Session has been terminated',
                'user_id': session.user_id,
                'user_type': session.user_type
            }
        
        if session.is_expired():
            # Mark session as expired
            session.expire()
            self.update(session)
            return {
                'is_valid': False,
                'error': 'Session has expired',
                'user_id': session.user_id,
                'user_type': session.user_type
            }
        
        # Update last accessed time
        session.update_access()
        self.update(session)
        
        return {
            'is_valid': True,
            'error': None,
            'user_id': session.user_id,
            'user_type': session.user_type,
            'session': session
        }
    
    def refresh_session(self, session_id: UUID) -> Optional[UserSession]:
        """Refresh a session's expiration time."""
        session = self.find_by_id(session_id)
        if session and session.is_active():
            session.refresh()
            return self.update(session)
        return None
    
    def terminate_session(self, session_id: UUID) -> bool:
        """Terminate a session."""
        session = self.find_by_id(session_id)
        if session:
            session.terminate()
            self.update(session)
            return True
        return False
    
    def terminate_user_sessions(self, user_id: UUID) -> int:
        """Terminate all sessions for a user."""
        sessions = self.find_by_user(user_id)
        terminated_count = 0
        
        for session in sessions:
            if session.is_active():
                session.terminate()
                self.update(session)
                terminated_count += 1
        
        return terminated_count
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions by marking them as expired."""
        expired_sessions = self.find_expired_sessions()
        cleaned_count = 0
        
        for session in expired_sessions:
            session.expire()
            self.update(session)
            cleaned_count += 1
        
        return cleaned_count
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Delete sessions older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        old_sessions = []
        
        for session in self.find_all():
            if session.created_at < cutoff_date and not session.is_active():
                old_sessions.append(session)
        
        deleted_count = 0
        for session in old_sessions:
            if self.delete(session.id):
                deleted_count += 1
        
        return deleted_count
    
    def get_user_session_history(self, user_id: UUID, limit: int = 10) -> List[UserSession]:
        """Get session history for a user."""
        sessions = self.find_by_user(user_id)
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions[:limit]
    
    def get_active_users_count(self) -> int:
        """Get count of users with active sessions."""
        active_sessions = self.find_active_sessions()
        unique_users = set(session.user_id for session in active_sessions)
        return len(unique_users)
    
    def get_concurrent_sessions_by_ip(self, ip_address: str) -> List[UserSession]:
        """Get concurrent active sessions from the same IP address."""
        sessions = self.find_by_ip_address(ip_address)
        return [session for session in sessions if session.is_active()]
    
    def detect_suspicious_activity(self) -> Dict[str, Any]:
        """Detect suspicious session activity."""
        suspicious_activity = {
            'multiple_sessions_same_ip': [],
            'rapid_session_creation': [],
            'unusual_user_agents': []
        }
        
        # Check for multiple active sessions from same IP
        ip_sessions = {}
        for session in self.find_active_sessions():
            if session.ip_address:
                if session.ip_address not in ip_sessions:
                    ip_sessions[session.ip_address] = []
                ip_sessions[session.ip_address].append(session)
        
        for ip, sessions in ip_sessions.items():
            if len(sessions) > 3:  # More than 3 active sessions from same IP
                suspicious_activity['multiple_sessions_same_ip'].append({
                    'ip_address': ip,
                    'session_count': len(sessions),
                    'user_ids': [str(s.user_id) for s in sessions]
                })
        
        # Check for rapid session creation (more than 5 sessions in last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_sessions = self.find_sessions_by_date_range(one_hour_ago, datetime.utcnow())
        
        user_session_counts = {}
        for session in recent_sessions:
            user_id = str(session.user_id)
            user_session_counts[user_id] = user_session_counts.get(user_id, 0) + 1
        
        for user_id, count in user_session_counts.items():
            if count > 5:
                suspicious_activity['rapid_session_creation'].append({
                    'user_id': user_id,
                    'session_count': count
                })
        
        return suspicious_activity
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        all_sessions = self.find_all()
        active_sessions = self.find_active_sessions()
        expired_sessions = self.find_expired_sessions()
        terminated_sessions = self.find_by_status(SessionStatus.TERMINATED)
        
        # Count by status
        status_counts = {
            'active': len(active_sessions),
            'expired': len(expired_sessions),
            'terminated': len(terminated_sessions)
        }
        
        # Count by user type
        type_counts = {}
        for user_type in UserType:
            type_counts[user_type.value] = len(self.find_by_user_type(user_type))
        
        # Calculate average session duration for completed sessions
        completed_sessions = expired_sessions + terminated_sessions
        if completed_sessions:
            total_duration = sum(
                (session.last_accessed - session.created_at).total_seconds()
                for session in completed_sessions
            )
            avg_duration_minutes = (total_duration / len(completed_sessions)) / 60
        else:
            avg_duration_minutes = 0
        
        return {
            'total_sessions': len(all_sessions),
            'active_users': self.get_active_users_count(),
            'status_distribution': status_counts,
            'user_type_distribution': type_counts,
            'average_session_duration_minutes': round(avg_duration_minutes, 1),
            'sessions_needing_cleanup': len(expired_sessions)
        }
    
    def search_sessions(self, criteria: Dict[str, Any]) -> List[UserSession]:
        """Search sessions by multiple criteria."""
        results = self.find_all()
        
        # Filter by user ID
        user_id = criteria.get('user_id')
        if user_id:
            results = [s for s in results if s.user_id == user_id]
        
        # Filter by user type
        user_type = criteria.get('user_type')
        if user_type:
            results = [s for s in results if s.user_type == user_type]
        
        # Filter by status
        status = criteria.get('status')
        if status:
            results = [s for s in results if s.status == status]
        
        # Filter by IP address
        ip_address = criteria.get('ip_address')
        if ip_address:
            results = [s for s in results if s.ip_address == ip_address]
        
        # Filter by date range
        start_date = criteria.get('start_date')
        end_date = criteria.get('end_date')
        if start_date and end_date:
            results = [s for s in results if start_date <= s.created_at <= end_date]
        
        # Filter active only
        if criteria.get('active_only', False):
            results = [s for s in results if s.is_active()]
        
        return sorted(results, key=lambda s: s.created_at, reverse=True)