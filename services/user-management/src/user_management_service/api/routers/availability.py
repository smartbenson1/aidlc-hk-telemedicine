#!/usr/bin/env python3
"""
Availability Router

Provides availability management endpoints for the User Management Service API.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from uuid import UUID

from ..dependencies import get_service_container, get_current_user
from ...main import UserManagementServiceDemo
from ...requests.availability_requests import TimeSlotRequest, BulkAvailabilityRequest, AvailabilityQueryRequest
from ...utils.enums import AppointmentType
from ...utils.logging_utils import get_logger
from ...utils.exceptions import ValidationError, BusinessRuleError

logger = get_logger(__name__)
router = APIRouter()


class TimeSlotAPI(BaseModel):
    """API model for time slot creation/update."""
    datetime: datetime = Field(..., description="Slot date and time")
    appointment_type: str = Field(..., description="Appointment type (in_person or telemedicine)")
    specialty_id: str = Field(..., description="Medical specialty ID")


class BulkTimeSlotAPI(BaseModel):
    """API model for bulk time slot creation."""
    doctor_id: str = Field(..., description="Doctor ID")
    time_slots: List[TimeSlotAPI] = Field(..., min_items=1, max_items=50)


class TimeSlotResponse(BaseModel):
    """API response model for time slot information."""
    id: str
    doctor_id: str
    datetime: str
    appointment_type: str
    specialty_id: str
    status: str
    created_at: str
    updated_at: str


class AvailabilityQueryAPI(BaseModel):
    """API model for availability query."""
    doctor_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    appointment_type: Optional[str] = None
    specialty_id: Optional[str] = None


@router.post("/slots", response_model=Dict[str, Any], summary="Add a time slot")
async def add_time_slot(
    request: TimeSlotAPI,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Add a new availability time slot for a doctor."""
    
    try:
        # Only doctors can add time slots
        if current_user["user_type"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can add time slots"
            )
        
        # Parse appointment type
        try:
            appointment_type = AppointmentType(request.appointment_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid appointment_type. Valid values: {[t.value for t in AppointmentType]}"
            )
        
        # Parse specialty ID
        try:
            specialty_id = UUID(request.specialty_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid specialty_id format"
            )
        
        # Create time slot request
        slot_request = TimeSlotRequest(
            datetime=request.datetime,
            appointment_type=appointment_type,
            specialty_id=specialty_id
        )
        
        # Add time slot
        result = service.availability_service.add_time_slot(
            current_user["user_id"], slot_request, current_user["session_id"]
        )
        
        if result.success:
            logger.info(f"Time slot added successfully: {result.data.availability_id}")
            return {
                "success": True,
                "data": {
                    "slot_id": result.data.availability_id,
                    "doctor_id": current_user["user_id"],
                    "datetime": request.datetime.isoformat(),
                    "appointment_type": request.appointment_type,
                    "specialty_id": request.specialty_id,
                    "message": "Time slot added successfully"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
            
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Add time slot failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add time slot"
        )


@router.post("/slots/bulk", response_model=Dict[str, Any], summary="Add multiple time slots")
async def add_bulk_time_slots(
    request: BulkTimeSlotAPI,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Add multiple availability time slots for a doctor."""
    
    try:
        # Only doctors can add time slots, and only for themselves
        if current_user["user_type"] != "doctor" or current_user["user_id"] != request.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can add time slots for themselves"
            )
        
        # Convert API slots to domain requests
        time_slot_requests = []
        for slot in request.time_slots:
            try:
                appointment_type = AppointmentType(slot.appointment_type.lower())
                specialty_id = UUID(slot.specialty_id)
                
                time_slot_requests.append(TimeSlotRequest(
                    datetime=slot.datetime,
                    appointment_type=appointment_type,
                    specialty_id=specialty_id
                ))
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid slot data: {e}"
                )
        
        # Create bulk request
        bulk_request = BulkAvailabilityRequest(
            doctor_id=UUID(request.doctor_id),
            time_slots=time_slot_requests
        )
        
        # Add bulk time slots
        result = service.availability_service.add_bulk_availability(
            bulk_request, current_user["session_id"]
        )
        
        if result.success:
            logger.info(f"Bulk time slots added successfully: {len(result.data.availability_ids)} slots")
            return {
                "success": True,
                "data": {
                    "slot_ids": result.data.availability_ids,
                    "doctor_id": request.doctor_id,
                    "slots_added": len(result.data.availability_ids),
                    "message": f"Successfully added {len(result.data.availability_ids)} time slots"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
            
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Add bulk time slots failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add bulk time slots"
        )


@router.put("/slots/{slot_id}", response_model=Dict[str, Any], summary="Update a time slot")
async def update_time_slot(
    slot_id: str,
    request: TimeSlotAPI,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Update an existing availability time slot."""
    
    try:
        # Only doctors can update time slots
        if current_user["user_type"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can update time slots"
            )
        
        # Parse appointment type
        try:
            appointment_type = AppointmentType(request.appointment_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid appointment_type. Valid values: {[t.value for t in AppointmentType]}"
            )
        
        # Parse specialty ID
        try:
            specialty_id = UUID(request.specialty_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid specialty_id format"
            )
        
        # Parse slot ID
        try:
            slot_uuid = UUID(slot_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid slot_id format"
            )
        
        # Create time slot request
        slot_request = TimeSlotRequest(
            datetime=request.datetime,
            appointment_type=appointment_type,
            specialty_id=specialty_id
        )
        
        # Update time slot
        result = service.availability_service.modify_time_slot(
            slot_uuid, slot_request, current_user["session_id"]
        )
        
        if result.success:
            logger.info(f"Time slot updated successfully: {slot_id}")
            return {
                "success": True,
                "data": {
                    "slot_id": slot_id,
                    "updated_fields": result.data.updated_fields,
                    "message": "Time slot updated successfully"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            if "not found" in result.error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Time slot not found"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.error_message
                )
                
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Update time slot failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update time slot"
        )


@router.delete("/slots/{slot_id}", response_model=Dict[str, Any], summary="Remove a time slot")
async def remove_time_slot(
    slot_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Remove an availability time slot."""
    
    try:
        # Only doctors can remove time slots
        if current_user["user_type"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can remove time slots"
            )
        
        # Parse slot ID
        try:
            slot_uuid = UUID(slot_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid slot_id format"
            )
        
        # Remove time slot
        result = service.availability_service.remove_time_slot(
            slot_uuid, current_user["session_id"]
        )
        
        if result.success:
            logger.info(f"Time slot removed successfully: {slot_id}")
            return {
                "success": True,
                "data": {
                    "slot_id": slot_id,
                    "message": "Time slot removed successfully"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            if "not found" in result.error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Time slot not found"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.error_message
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove time slot failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove time slot"
        )


@router.get("/query", response_model=Dict[str, Any], summary="Query availability slots")
async def query_availability(
    doctor_id: Optional[str] = Query(None, description="Doctor ID filter"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    appointment_type: Optional[str] = Query(None, description="Appointment type filter"),
    specialty_id: Optional[str] = Query(None, description="Specialty ID filter"),
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Query availability slots with optional filters."""
    
    try:
        # Parse dates
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use YYYY-MM-DD"
                )
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use YYYY-MM-DD"
                )
        
        # Parse doctor ID
        parsed_doctor_id = None
        if doctor_id:
            try:
                parsed_doctor_id = UUID(doctor_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid doctor_id format"
                )
        
        # Parse appointment type
        parsed_appointment_type = None
        if appointment_type:
            try:
                parsed_appointment_type = AppointmentType(appointment_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid appointment_type. Valid values: {[t.value for t in AppointmentType]}"
                )
        
        # Parse specialty ID
        parsed_specialty_id = None
        if specialty_id:
            try:
                parsed_specialty_id = UUID(specialty_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid specialty_id format"
                )
        
        # Create query
        query = AvailabilityQueryRequest(
            doctor_id=parsed_doctor_id,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            appointment_type=parsed_appointment_type,
            specialty_id=parsed_specialty_id
        )
        
        # Query availability
        result = service.availability_service.query_availability(query)
        
        if result.success:
            # Format response
            slots = []
            for slot in result.data:
                slots.append({
                    "id": str(slot.id),
                    "doctor_id": str(slot.doctor_id),
                    "datetime": slot.datetime.isoformat(),
                    "appointment_type": slot.appointment_type.value,
                    "specialty_id": str(slot.specialty_id),
                    "status": slot.status.value,
                    "created_at": slot.created_at.isoformat(),
                    "updated_at": slot.updated_at.isoformat()
                })
            
            return {
                "success": True,
                "data": {
                    "slots": slots,
                    "total_count": len(slots),
                    "filters": {
                        "doctor_id": doctor_id,
                        "start_date": start_date,
                        "end_date": end_date,
                        "appointment_type": appointment_type,
                        "specialty_id": specialty_id
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
            
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query availability failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query availability"
        )


@router.get("/statistics", response_model=Dict[str, Any], summary="Get availability statistics")
async def get_availability_statistics(
    service: UserManagementServiceDemo = Depends(get_service_container)
) -> Dict[str, Any]:
    """Get availability statistics."""
    
    try:
        result = service.availability_service.get_availability_statistics()
        
        if result.success:
            return {
                "success": True,
                "data": result.data,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get availability statistics"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get availability statistics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get availability statistics"
        )