"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# Enums for API models
class NotificationTypeEnum(str, Enum):
    REGISTRATION_CONFIRMATION = "registration_confirmation"
    APPOINTMENT_BOOKING = "appointment_booking"
    APPOINTMENT_REMINDER = "appointment_reminder"
    RESCHEDULE_REQUEST = "reschedule_request"
    RESCHEDULE_CONFIRMATION = "reschedule_confirmation"
    SYSTEM_ALERT = "system_alert"

class RecipientTypeEnum(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"
    ADMIN = "admin"

class PriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"

# Request Models
class SendNotificationRequest(BaseModel):
    """Request model for sending immediate notifications."""
    recipient_email: EmailStr
    recipient_name: str = Field(..., min_length=1, max_length=100)
    recipient_type: RecipientTypeEnum
    notification_type: NotificationTypeEnum
    template_name: str = Field(..., min_length=1, max_length=100)
    template_variables: Dict[str, Any] = Field(default_factory=dict)
    priority: PriorityEnum = PriorityEnum.NORMAL
    
    class Config:
        schema_extra = {
            "example": {
                "recipient_email": "patient@example.com",
                "recipient_name": "John Doe",
                "recipient_type": "patient",
                "notification_type": "appointment_reminder",
                "template_name": "appointment_reminder_patient",
                "template_variables": {
                    "patient_name": "John Doe",
                    "doctor_name": "Dr. Smith",
                    "appointment_date": "2024-02-15",
                    "appointment_time": "10:00 AM"
                },
                "priority": "normal"
            }
        }

class ScheduleNotificationRequest(BaseModel):
    """Request model for scheduling notifications."""
    recipient_email: EmailStr
    recipient_name: str = Field(..., min_length=1, max_length=100)
    recipient_type: RecipientTypeEnum
    notification_type: NotificationTypeEnum
    template_name: str = Field(..., min_length=1, max_length=100)
    template_variables: Dict[str, Any] = Field(default_factory=dict)
    priority: PriorityEnum = PriorityEnum.NORMAL
    scheduled_time: datetime = Field(..., description="ISO 8601 datetime for when to send the notification")
    
    @validator('scheduled_time')
    def validate_future_time(cls, v):
        if v <= datetime.now():
            raise ValueError('Scheduled time must be in the future')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "recipient_email": "patient@example.com",
                "recipient_name": "John Doe",
                "recipient_type": "patient",
                "notification_type": "appointment_reminder",
                "template_name": "appointment_reminder_patient",
                "template_variables": {
                    "patient_name": "John Doe",
                    "doctor_name": "Dr. Smith",
                    "appointment_date": "2024-02-15",
                    "appointment_time": "10:00 AM"
                },
                "priority": "normal",
                "scheduled_time": "2024-02-14T18:00:00Z"
            }
        }

class CreateTemplateRequest(BaseModel):
    """Request model for creating email templates."""
    template_name: str = Field(..., min_length=1, max_length=100)
    template_type: NotificationTypeEnum
    subject_template: str = Field(..., min_length=1, max_length=200)
    body_template: str = Field(..., min_length=1, max_length=10000)
    required_variables: List[str] = Field(default_factory=list)
    optional_variables: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(None, max_length=500)
    
    class Config:
        schema_extra = {
            "example": {
                "template_name": "appointment_reminder_patient",
                "template_type": "appointment_reminder",
                "subject_template": "Appointment Reminder - {appointment_date}",
                "body_template": "Dear {patient_name},\n\nThis is a reminder for your appointment with {doctor_name} on {appointment_date} at {appointment_time}.\n\nBest regards,\nHealthcare Team",
                "required_variables": ["patient_name", "doctor_name", "appointment_date", "appointment_time"],
                "optional_variables": ["clinic_address", "phone_number"],
                "description": "Template for patient appointment reminders"
            }
        }

class RenderTemplateRequest(BaseModel):
    """Request model for rendering templates."""
    template_name: str = Field(..., min_length=1, max_length=100)
    template_variables: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "template_name": "appointment_reminder_patient",
                "template_variables": {
                    "patient_name": "John Doe",
                    "doctor_name": "Dr. Smith",
                    "appointment_date": "2024-02-15",
                    "appointment_time": "10:00 AM"
                }
            }
        }

# Response Models
class NotificationResponse(BaseModel):
    """Response model for notification operations."""
    success: bool
    notification_id: str
    status: NotificationStatusEnum
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "notification_id": "notif_123456789",
                "status": "pending",
                "message": "Notification queued for delivery"
            }
        }

class NotificationStatusResponse(BaseModel):
    """Response model for notification status queries."""
    success: bool
    notification_id: str
    status: NotificationStatusEnum
    recipient_email: str
    notification_type: NotificationTypeEnum
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "notification_id": "notif_123456789",
                "status": "delivered",
                "recipient_email": "patient@example.com",
                "notification_type": "appointment_reminder",
                "created_at": "2024-01-01T10:00:00Z",
                "sent_at": "2024-01-01T10:01:00Z",
                "delivered_at": "2024-01-01T10:02:00Z",
                "failure_reason": None,
                "retry_count": 0
            }
        }

class TemplateResponse(BaseModel):
    """Response model for template operations."""
    success: bool
    template_id: str
    template_name: str
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "template_id": "tmpl_123456789",
                "template_name": "appointment_reminder_patient",
                "message": "Template created successfully"
            }
        }

class RenderedTemplateResponse(BaseModel):
    """Response model for template rendering."""
    success: bool
    rendered_subject: str
    rendered_body: str
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "rendered_subject": "Appointment Reminder - February 15, 2024",
                "rendered_body": "Dear John Doe,\n\nThis is a reminder for your appointment with Dr. Smith on February 15, 2024 at 10:00 AM.\n\nBest regards,\nHealthcare Team"
            }
        }

class ErrorResponse(BaseModel):
    """Response model for errors."""
    success: bool = False
    error: str
    message: str
    details: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "Validation Error",
                "message": "Invalid template variables",
                "details": ["Missing required variable: patient_name"]
            }
        }