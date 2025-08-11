"""Basic usage example for notification service models."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from notification_service.models.notification import Notification
from notification_service.models.email_template import EmailTemplate
from notification_service.models.notification_queue import NotificationQueue
from notification_service.models.delivery_status import DeliveryStatus
from notification_service.models.notification_request import NotificationRequest
from notification_service.enums import (
    NotificationType, RecipientType, Priority, NotificationStatus,
    TemplateFormat, TemplateStatus, QueueType, QueueStatus,
    DeliveryStatusEnum, BounceType, RequestStatus
)


def demonstrate_notification_models():
    """Demonstrate basic usage of notification service models."""
    
    print("=== Notification Service Models Demo ===\n")
    
    # 1. Create an email template
    print("1. Creating Email Template...")
    template = EmailTemplate(
        template_name="appointment_reminder",
        template_type=NotificationType.APPOINTMENT_REMINDER,
        subject_template="Appointment Reminder - {appointment_date}",
        body_template="""
        Dear {patient_name},
        
        This is a reminder that you have an appointment scheduled with Dr. {doctor_name} 
        on {appointment_date} at {appointment_time}.
        
        Please arrive 15 minutes early.
        
        Best regards,
        Healthcare Team
        """,
        required_variables=["patient_name", "doctor_name", "appointment_date", "appointment_time"],
        optional_variables=["clinic_address", "phone_number"],
        template_format=TemplateFormat.TEXT,
        description="Template for 24-hour appointment reminders"
    )
    
    print(f"Created template: {template.template_name}")
    print(f"Template ID: {template.id}")
    print(f"Required variables: {template.required_variables}")
    
    # 2. Create a notification request
    print("\n2. Creating Notification Request...")
    request = NotificationRequest(
        source_service="appointment_service",
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        recipient_email="patient@example.com",
        recipient_name="John Doe",
        recipient_type=RecipientType.PATIENT,
        template_name="appointment_reminder",
        template_variables={
            "patient_name": "John Doe",
            "doctor_name": "Dr. Smith",
            "appointment_date": "2024-02-15",
            "appointment_time": "10:00 AM"
        },
        priority=Priority.NORMAL,
        scheduled_time=datetime.now().replace(tzinfo=None) + timedelta(hours=1)  # Schedule for 1 hour from now
    )
    
    print(f"Created request: {request.request_id}")
    print(f"Recipient: {request.recipient_email}")
    print(f"Scheduled for: {request.scheduled_time}")
    
    # 3. Render template with variables
    print("\n3. Rendering Template...")
    try:
        rendered = template.render(request.template_variables)
        print(f"Rendered subject: {rendered['subject']}")
        print(f"Rendered body preview: {rendered['body'][:100]}...")
    except Exception as e:
        print(f"Template rendering error: {e}")
    
    # 4. Create notification from request
    print("\n4. Creating Notification...")
    notification = Notification(
        recipient_email=request.recipient_email,
        recipient_name=request.recipient_name,
        recipient_type=request.recipient_type,
        notification_type=request.notification_type,
        subject=rendered['subject'],
        body=rendered['body'],
        template_name=request.template_name,
        template_variables=request.template_variables,
        priority=request.priority,
        scheduled_time=request.scheduled_time
    )
    
    print(f"Created notification: {notification.id}")
    print(f"Status: {notification.status.value}")
    print(f"Priority: {notification.priority.value}")
    
    # 5. Add to queue
    print("\n5. Adding to Queue...")
    queue_item = NotificationQueue(
        queue_name="appointment_reminders",
        queue_type=QueueType.SCHEDULED,
        notification_id=notification.id,
        priority=notification.priority,
        scheduled_time=notification.scheduled_time or datetime.now()
    )
    
    print(f"Queued item: {queue_item.id}")
    print(f"Queue type: {queue_item.queue_type.value}")
    print(f"Ready for processing: {queue_item.is_ready_for_processing()}")
    
    # 6. Simulate processing
    print("\n6. Simulating Processing...")
    queue_item.start_processing()
    print(f"Processing started at: {queue_item.processing_started_at}")
    
    # Update notification status
    notification.update_status(NotificationStatus.SENT)
    print(f"Notification status updated to: {notification.status.value}")
    print(f"Sent at: {notification.sent_at}")
    
    # 7. Create delivery status
    print("\n7. Creating Delivery Status...")
    delivery = DeliveryStatus(
        notification_id=notification.id,
        delivery_provider="smtp_provider",
        recipient_email=notification.recipient_email,
        delivery_attempt=1,
        status=DeliveryStatusEnum.SENT
    )
    
    print(f"Delivery status: {delivery.id}")
    print(f"Provider: {delivery.delivery_provider}")
    print(f"Status: {delivery.status.value}")
    
    # 8. Simulate successful delivery
    print("\n8. Simulating Successful Delivery...")
    delivery.update_status(
        DeliveryStatusEnum.DELIVERED,
        response_code="250",
        response_message="Message delivered successfully"
    )
    
    notification.update_status(NotificationStatus.DELIVERED)
    queue_item.complete_processing()
    
    print(f"Final notification status: {notification.status.value}")
    print(f"Delivered at: {notification.delivered_at}")
    print(f"Queue status: {queue_item.status.value}")
    print(f"Processing completed at: {queue_item.completed_at}")
    
    # 9. Update request status
    print("\n9. Updating Request Status...")
    request.update_status(RequestStatus.PROCESSED)
    request.link_notification(notification.id)
    
    print(f"Request status: {request.status.value}")
    print(f"Linked notification: {request.notification_id}")
    print(f"Processed at: {request.processed_at}")
    
    print("\n=== Demo Complete ===")
    
    # 10. Show data conversion
    print("\n10. Data Conversion Examples...")
    
    # Convert to dict and back
    notification_dict = notification.to_dict()
    notification_restored = Notification.from_dict(notification_dict)
    
    print(f"Original notification ID: {notification.id}")
    print(f"Restored notification ID: {notification_restored.id}")
    print(f"Data integrity check: {notification.id == notification_restored.id}")
    
    # Show template validation
    print(f"\nTemplate validation result: {template.validate().is_valid}")
    print(f"Notification can retry: {notification.can_retry()}")
    print(f"Notification age: {notification.get_age_in_minutes()} minutes")


def demonstrate_user_story_us_s001():
    """Demonstrate US-S001: Patient appointment reminders."""
    
    print("\n=== US-S001: Patient Appointment Reminders ===")
    
    # Create template for patient reminders
    patient_reminder_template = EmailTemplate(
        template_name="patient_appointment_reminder",
        template_type=NotificationType.APPOINTMENT_REMINDER,
        subject_template="Appointment Reminder - Tomorrow at {appointment_time}",
        body_template="""
        Dear {patient_name},
        
        This is a friendly reminder that you have an appointment scheduled for tomorrow:
        
        Date: {appointment_date}
        Time: {appointment_time}
        Doctor: {doctor_name}
        Location: {appointment_location}
        
        Please arrive 15 minutes early and bring your insurance card.
        
        If you need to reschedule, please call us at {clinic_phone}.
        
        Thank you,
        {clinic_name}
        """,
        required_variables=["patient_name", "appointment_date", "appointment_time", "doctor_name"],
        optional_variables=["appointment_location", "clinic_phone", "clinic_name"]
    )
    
    # Create notification request (would come from appointment service)
    reminder_request = NotificationRequest(
        source_service="appointment_service",
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        recipient_email="john.doe@email.com",
        recipient_name="John Doe",
        recipient_type=RecipientType.PATIENT,
        template_name="patient_appointment_reminder",
        template_variables={
            "patient_name": "John Doe",
            "appointment_date": "February 15, 2024",
            "appointment_time": "10:00 AM",
            "doctor_name": "Dr. Sarah Smith",
            "appointment_location": "Main Clinic, Room 205",
            "clinic_phone": "(555) 123-4567",
            "clinic_name": "HealthCare Plus"
        },
        priority=Priority.NORMAL,
        scheduled_time=datetime.now().replace(tzinfo=None) + timedelta(hours=24)  # 24 hours before appointment
    )
    
    print(f"Patient reminder request created: {reminder_request.request_id}")
    print(f"Scheduled for: {reminder_request.scheduled_time}")
    print(f"Recipient: {reminder_request.recipient_name} ({reminder_request.recipient_email})")
    
    # Render and create notification
    rendered_content = patient_reminder_template.render(reminder_request.template_variables)
    
    patient_notification = Notification(
        recipient_email=reminder_request.recipient_email,
        recipient_name=reminder_request.recipient_name,
        recipient_type=reminder_request.recipient_type,
        notification_type=reminder_request.notification_type,
        subject=rendered_content['subject'],
        body=rendered_content['body'],
        template_name=reminder_request.template_name,
        template_variables=reminder_request.template_variables,
        priority=reminder_request.priority,
        scheduled_time=reminder_request.scheduled_time
    )
    
    print(f"Patient notification created: {patient_notification.id}")
    print(f"Subject: {patient_notification.subject}")
    print(f"US-S001 requirement satisfied: Patient will receive appointment reminder 1 day before appointment")


def demonstrate_user_story_us_s002():
    """Demonstrate US-S002: Doctor appointment notifications."""
    
    print("\n=== US-S002: Doctor Appointment Notifications ===")
    
    # Create template for doctor notifications
    doctor_notification_template = EmailTemplate(
        template_name="doctor_appointment_notification",
        template_type=NotificationType.APPOINTMENT_REMINDER,
        subject_template="Upcoming Appointment - {patient_name} tomorrow at {appointment_time}",
        body_template="""
        Dear Dr. {doctor_name},
        
        You have an upcoming appointment scheduled for tomorrow:
        
        Patient: {patient_name}
        Date: {appointment_date}
        Time: {appointment_time}
        Type: {appointment_type}
        
        Patient Symptoms/Reason:
        {patient_symptoms}
        
        Patient Contact: {patient_phone}
        
        Please review the patient's medical history before the appointment.
        
        Best regards,
        Scheduling System
        """,
        required_variables=["doctor_name", "patient_name", "appointment_date", "appointment_time", "patient_symptoms"],
        optional_variables=["appointment_type", "patient_phone"]
    )
    
    # Create notification request for doctor
    doctor_reminder_request = NotificationRequest(
        source_service="appointment_service",
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        recipient_email="dr.smith@clinic.com",
        recipient_name="Dr. Sarah Smith",
        recipient_type=RecipientType.DOCTOR,
        template_name="doctor_appointment_notification",
        template_variables={
            "doctor_name": "Dr. Sarah Smith",
            "patient_name": "John Doe",
            "appointment_date": "February 15, 2024",
            "appointment_time": "10:00 AM",
            "appointment_type": "Follow-up Consultation",
            "patient_symptoms": "Follow-up for hypertension management. Patient reports feeling dizzy occasionally.",
            "patient_phone": "(555) 987-6543"
        },
        priority=Priority.NORMAL,
        scheduled_time=datetime.now().replace(tzinfo=None) + timedelta(hours=24)  # 24 hours before appointment
    )
    
    print(f"Doctor reminder request created: {doctor_reminder_request.request_id}")
    print(f"Scheduled for: {doctor_reminder_request.scheduled_time}")
    print(f"Recipient: {doctor_reminder_request.recipient_name} ({doctor_reminder_request.recipient_email})")
    
    # Render and create notification
    rendered_content = doctor_notification_template.render(doctor_reminder_request.template_variables)
    
    doctor_notification = Notification(
        recipient_email=doctor_reminder_request.recipient_email,
        recipient_name=doctor_reminder_request.recipient_name,
        recipient_type=doctor_reminder_request.recipient_type,
        notification_type=doctor_reminder_request.notification_type,
        subject=rendered_content['subject'],
        body=rendered_content['body'],
        template_name=doctor_reminder_request.template_name,
        template_variables=doctor_reminder_request.template_variables,
        priority=doctor_reminder_request.priority,
        scheduled_time=doctor_reminder_request.scheduled_time
    )
    
    print(f"Doctor notification created: {doctor_notification.id}")
    print(f"Subject: {doctor_notification.subject}")
    print(f"US-S002 requirement satisfied: Doctor will receive appointment notification 1 day before appointment with patient information")


if __name__ == "__main__":
    try:
        demonstrate_notification_models()
        demonstrate_user_story_us_s001()
        demonstrate_user_story_us_s002()
        
        print("\n🎉 All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()