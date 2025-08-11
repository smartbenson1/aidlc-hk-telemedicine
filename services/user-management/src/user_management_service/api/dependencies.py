#!/usr/bin/env python3
"""
API Dependencies

Provides dependency injection functions for the User Management Service API.
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import jwt
import os

from ..main import UserManagementServiceDemo
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)
security = HTTPBearer()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# Global service container
service_container: UserManagementServiceDemo = None


def get_service_container() -> UserManagementServiceDemo:
    """Dependency to get the service container."""
    global service_container
    if service_container is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service container not initialized"
        )
    return service_container


def set_service_container(container: UserManagementServiceDemo):
    """Set the global service container."""
    global service_container
    service_container = container


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Get the current authenticated user from JWT token."""
    
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        
        user_id = payload.get("sub")
        user_type = payload.get("user_type")
        session_id = payload.get("session_id")
        
        if not all([user_id, user_type, session_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Validate session is still active
        session_validation = service.session_manager.validate_session(session_id)
        if not session_validation.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid"
            )
        
        return {
            "user_id": user_id,
            "user_type": user_type,
            "session_id": session_id,
            "token_payload": payload
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_doctor(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the current authenticated user, ensuring they are a doctor."""
    
    if current_user["user_type"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor access required"
        )
    
    return current_user


async def get_current_patient(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the current authenticated user, ensuring they are a patient."""
    
    if current_user["user_type"] != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required"
        )
    
    return current_user


# Optional authentication dependency for endpoints that work with or without auth
async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Get the current authenticated user if token is provided, otherwise return None."""
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, service)
    except HTTPException:
        return None