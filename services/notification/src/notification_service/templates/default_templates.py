"""Default email templates for the notification service."""

from ..models.email_template import EmailTemplate
from ..enums import NotificationType, TemplateFormat, TemplateStatus

def get_default_templates():
    """Get list of default email templates."""
    
    templates = []
    
    # Patient appointment reminder template
    patient_reminder = EmailTemplate(
        template_name="appointment_reminder_patient",
        template_type=NotificationType.APPOINTMENT_REMINDER,
        subject_template="Appointment Reminder - {appointment_date}",
        body_template="""Dear {patient_name},

This is a friendly reminder that you have an appointment scheduled for:

Date: {appointment_date}
Time: {appointment_time}
Doctor: {doctor_name}
Location: {appointment_location}

Please arrive 15 minutes early and bring your insurance card and a valid ID.

If you need to reschedule or cancel your appointment, please call us at {clinic_phone} at least 24 hours in advance.

Thank you,
{clinic_name}

---
This is an automated message. Please do not reply to this email.""",
        required_variables=["patient_name", "appointment_date", "appointment_time", "doctor_name"],
        optional_variables=["appointment_location", "clinic_phone", "clinic_name"],
        template_format=TemplateFormat.TEXT,
        description="24-hour appointment reminder for patients"
    )
    templates.append(patient_reminder)
    
    # Doctor appointment notification template
    doctor_notification = EmailTemplate(
        template_name="appointment_reminder_doctor",
        template_type=NotificationType.APPOINTMENT_REMINDER,
        subject_template="Upcoming Appointment - {patient_name} on {appointment_date}",
        body_template="""Dear Dr. {doctor_name},

You have an upcoming appointment scheduled for:

Patient: {patient_name}
Date: {appointment_date}
Time: {appointment_time}
Type: {appointment_type}

Patient Contact Information:
Email: {patient_email}
Phone: {patient_phone}

Reason for Visit:
{patient_symptoms}

Please review the patient's medical history before the appointment.

Best regards,
Scheduling System

---
This is an automated message.""",
        required_variables=["doctor_name", "patient_name", "appointment_date", "appointment_time"],
        optional_variables=["appointment_type", "patient_email", "patient_phone", "patient_symptoms"],
        template_format=TemplateFormat.TEXT,
        description="24-hour appointment notification for doctors"
    )
    templates.append(doctor_notification)
    
    # Patient registration confirmation template
    patient_registration = EmailTemplate(
        template_name="patient_registration_confirmation",
        template_type=NotificationType.REGISTRATION_CONFIRMATION,
        subject_template="Welcome to HealMatch Easy - Registration Confirmed",
        body_template="""Dear {patient_name},

Welcome to HealMatch Easy! Your patient account has been successfully created.

Account Details:
Name: {patient_name}
Email: {patient_email}
Registration Date: {registration_date}

You can now:
- Search for doctors by specialty
- Book appointments online
- Receive appointment reminders
- Manage your medical information

To get started, visit our platform and describe your symptoms to find the best matching doctors.

If you have any questions, please contact our support team.

Best regards,
The HealMatch Easy Team

---
This is an automated message. Please do not reply to this email.""",
        required_variables=["patient_name", "patient_email", "registration_date"],
        optional_variables=["support_email", "platform_url"],
        template_format=TemplateFormat.TEXT,
        description="Registration confirmation email for new patients"
    )
    templates.append(patient_registration)
    
    # Doctor registration confirmation template
    doctor_registration = EmailTemplate(
        template_name="doctor_registration_confirmation",
        template_type=NotificationType.REGISTRATION_CONFIRMATION,
        subject_template="Welcome to HealMatch Easy - Doctor Account Confirmed",
        body_template="""Dear Dr. {doctor_name},

Welcome to HealMatch Easy! Your doctor account has been successfully created.

Account Details:
Name: Dr. {doctor_name}
Email: {doctor_email}
Specialty: {doctor_specialty}
Registration Date: {registration_date}

Your profile is now active and patients can:
- Find you through our matching system
- Book appointments with you
- Receive information about your expertise

You will receive email notifications for:
- New appointment bookings
- Appointment reminders
- Patient inquiries

To manage your availability and profile, please log into your doctor portal.

If you have any questions, please contact our support team.

Best regards,
The HealMatch Easy Team

---
This is an automated message. Please do not reply to this email.""",
        required_variables=["doctor_name", "doctor_email", "registration_date"],
        optional_variables=["doctor_specialty", "support_email", "portal_url"],
        template_format=TemplateFormat.TEXT,
        description="Registration confirmation email for new doctors"
    )
    templates.append(doctor_registration)
    
    # Appointment booking confirmation for patient
    appointment_booking_patient = EmailTemplate(
        template_name="appointment_booking_confirmation_patient",
        template_type=NotificationType.APPOINTMENT_BOOKING,
        subject_template="Appointment Confirmed - {doctor_name} on {appointment_date}",
        body_template="""Dear {patient_name},

Your appointment has been successfully booked!

Appointment Details:
Doctor: {doctor_name}
Specialty: {doctor_specialty}
Date: {appointment_date}
Time: {appointment_time}
Location: {appointment_location}
Type: {appointment_type}

Preparation Instructions:
- Arrive 15 minutes early
- Bring your insurance card and valid ID
- Bring a list of current medications
- Prepare any questions you want to ask

If you need to reschedule or cancel, please call us at {clinic_phone} at least 24 hours in advance.

You will receive a reminder email 24 hours before your appointment.

Thank you for choosing HealMatch Easy!

Best regards,
{clinic_name}

---
This is an automated message. Please do not reply to this email.""",
        required_variables=["patient_name", "doctor_name", "appointment_date", "appointment_time"],
        optional_variables=["doctor_specialty", "appointment_location", "appointment_type", "clinic_phone", "clinic_name"],
        template_format=TemplateFormat.TEXT,
        description="Appointment booking confirmation for patients"
    )
    templates.append(appointment_booking_patient)
    
    # Appointment booking notification for doctor
    appointment_booking_doctor = EmailTemplate(
        template_name="appointment_booking_notification_doctor",
        template_type=NotificationType.APPOINTMENT_BOOKING,
        subject_template="New Appointment Booked - {patient_name} on {appointment_date}",
        body_template="""Dear Dr. {doctor_name},

A new appointment has been booked with you.

Appointment Details:
Patient: {patient_name}
Date: {appointment_date}
Time: {appointment_time}
Type: {appointment_type}

Patient Information:
Email: {patient_email}
Phone: {patient_phone}

Reason for Visit:
{patient_symptoms}

The patient has been sent a confirmation email with preparation instructions.

You will receive a reminder email 24 hours before the appointment.

Best regards,
Scheduling System

---
This is an automated message.""",
        required_variables=["doctor_name", "patient_name", "appointment_date", "appointment_time"],
        optional_variables=["appointment_type", "patient_email", "patient_phone", "patient_symptoms"],
        template_format=TemplateFormat.TEXT,
        description="New appointment booking notification for doctors"
    )
    templates.append(appointment_booking_doctor)
    
    return templates

def load_default_templates(template_repository):
    """Load default templates into the repository."""
    templates = get_default_templates()
    
    for template in templates:
        try:
            # Check if template already exists
            existing = template_repository.find_by_name(template.template_name)
            if not existing:
                template_repository.save(template)
                print(f"Loaded default template: {template.template_name}")
            else:
                print(f"Template already exists: {template.template_name}")
        except Exception as e:
            print(f"Failed to load template {template.template_name}: {e}")
    
    print(f"Finished loading {len(templates)} default templates")