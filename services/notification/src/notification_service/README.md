# Notification Service - Domain Model Implementation

A simple and intuitive Python implementation of the notification service domain model for the Doctor Appointment Platform.

## Overview

This implementation provides a comprehensive notification service that handles email notifications and reminders for the healthcare platform. It supports various notification types including appointment reminders, booking confirmations, and system alerts.

## Features

- **Core Domain Models**: Notification, EmailTemplate, NotificationQueue, DeliveryStatus, NotificationRequest
- **Template Management**: Dynamic email templates with variable substitution
- **Queue Management**: Priority-based notification queuing and processing
- **Delivery Tracking**: Comprehensive delivery status tracking with retry logic
- **User Story Support**: Implements US-S001 (Patient reminders) and US-S002 (Doctor notifications)

## Directory Structure

```
notification_service/
├── models/           # Domain model classes
│   ├── notification.py
│   ├── email_template.py
│   ├── notification_queue.py
│   ├── delivery_status.py
│   └── notification_request.py
├── repositories/     # In-memory repository implementations
│   └── base_repository.py
├── services/         # Business logic services (planned)
├── utils/           # Utility classes and helpers
│   ├── helpers.py
│   └── validation.py
├── enums/           # Enumeration definitions
│   └── notification_enums.py
├── exceptions/      # Custom exception classes
│   └── notification_exceptions.py
├── tests/           # Unit tests (planned)
├── examples/        # Usage examples and demos
│   └── basic_usage.py
└── README.md
```

## Quick Start

### 1. Basic Usage

```python
from notification_service.models.notification import Notification
from notification_service.models.email_template import EmailTemplate
from notification_service.enums import NotificationType, RecipientType, Priority

# Create an email template
template = EmailTemplate(
    template_name="appointment_reminder",
    template_type=NotificationType.APPOINTMENT_REMINDER,
    subject_template="Appointment Reminder - {appointment_date}",
    body_template="Dear {patient_name}, you have an appointment with {doctor_name} on {appointment_date}.",
    required_variables=["patient_name", "doctor_name", "appointment_date"]
)

# Create a notification
notification = Notification(
    recipient_email="patient@example.com",
    recipient_name="John Doe",
    recipient_type=RecipientType.PATIENT,
    notification_type=NotificationType.APPOINTMENT_REMINDER,
    template_name="appointment_reminder",
    template_variables={
        "patient_name": "John Doe",
        "doctor_name": "Dr. Smith",
        "appointment_date": "2024-02-15"
    },
    priority=Priority.NORMAL
)

# Render template
rendered = template.render(notification.template_variables)
notification.subject = rendered['subject']
notification.body = rendered['body']

print(f"Notification created: {notification.id}")
print(f"Subject: {notification.subject}")
```

### 2. Running Examples

```bash
cd notification_service
python examples/basic_usage.py
```

This will demonstrate:
- Creating email templates
- Processing notification requests
- Template rendering
- Queue management
- Delivery tracking
- User story implementations (US-S001 and US-S002)

## Core Components

### 1. Notification Model

Central entity for managing email notifications with support for:
- Recipient information and types (doctor, patient, admin)
- Template-based content generation
- Priority levels and scheduling
- Status tracking and retry logic
- Delivery confirmation

### 2. EmailTemplate Model

Template management for dynamic content:
- Template types for different notification categories
- Variable substitution with required/optional variables
- Multiple formats (HTML, text, mixed)
- Version control and status management

### 3. NotificationQueue Model

Queue management for processing:
- Priority-based queuing (urgent, high, normal, low)
- Scheduled delivery support
- Retry logic with configurable attempts
- Processing status tracking

### 4. DeliveryStatus Model

Delivery tracking and monitoring:
- Provider-specific delivery status
- Bounce and complaint handling
- Response code and message tracking
- Delivery attempt counting

### 5. NotificationRequest Model

External service integration:
- Request validation and processing
- Source service tracking
- Correlation ID for tracing
- Error handling and status updates

## User Story Implementation

### US-S001: Patient Appointment Reminders

**Requirement**: Patients receive appointment reminders 1 day before their scheduled appointments.

**Implementation**:
```python
# Create patient reminder template
template = EmailTemplate(
    template_name="patient_appointment_reminder",
    template_type=NotificationType.APPOINTMENT_REMINDER,
    subject_template="Appointment Reminder - Tomorrow at {appointment_time}",
    body_template="Dear {patient_name}, reminder for your appointment with {doctor_name}...",
    required_variables=["patient_name", "appointment_date", "appointment_time", "doctor_name"]
)

# Schedule reminder 24 hours before appointment
request = NotificationRequest(
    source_service="appointment_service",
    notification_type=NotificationType.APPOINTMENT_REMINDER,
    recipient_type=RecipientType.PATIENT,
    scheduled_time=appointment_datetime - timedelta(hours=24)
)
```

### US-S002: Doctor Appointment Notifications

**Requirement**: Doctors receive appointment notifications 1 day before appointments with patient information.

**Implementation**:
```python
# Create doctor notification template
template = EmailTemplate(
    template_name="doctor_appointment_notification",
    template_type=NotificationType.APPOINTMENT_REMINDER,
    subject_template="Upcoming Appointment - {patient_name} tomorrow",
    body_template="Dear Dr. {doctor_name}, you have an appointment with {patient_name}. Symptoms: {patient_symptoms}",
    required_variables=["doctor_name", "patient_name", "patient_symptoms"]
)

# Schedule notification 24 hours before appointment
request = NotificationRequest(
    source_service="appointment_service",
    notification_type=NotificationType.APPOINTMENT_REMINDER,
    recipient_type=RecipientType.DOCTOR,
    scheduled_time=appointment_datetime - timedelta(hours=24)
)
```

## Enumerations

The service uses comprehensive enumerations for type safety:

- **NotificationType**: registration_confirmation, appointment_booking, appointment_reminder, etc.
- **RecipientType**: doctor, patient, admin
- **Priority**: low, normal, high, urgent
- **NotificationStatus**: pending, sent, delivered, failed, bounced
- **QueueStatus**: queued, processing, completed, failed, expired
- **DeliveryStatus**: pending, sent, delivered, failed, bounced, complained, rejected

## Validation

All models include comprehensive validation:
- Email format validation
- Required field checking
- Length constraints
- Enum value validation
- JSON data validation
- Business rule enforcement

## Error Handling

Custom exception hierarchy:
- `NotificationServiceError`: Base exception
- `ValidationError`: Data validation failures
- `TemplateRenderingError`: Template processing errors
- `DeliveryError`: Notification delivery failures
- `QueueError`: Queue operation failures

## Data Persistence

Currently uses in-memory storage via the `InMemoryRepository` class:
- CRUD operations
- Criteria-based querying
- Indexing support
- Pagination
- Data conversion (to/from dictionaries)

## Testing

Run the basic usage example to verify functionality:

```bash
python examples/basic_usage.py
```

Expected output includes:
- Model creation and validation
- Template rendering
- Queue processing simulation
- Delivery status tracking
- User story demonstrations

## Future Enhancements

The current implementation provides a solid foundation for:
- Service layer implementation
- Repository pattern with database persistence
- External email provider integration
- Webhook processing
- Analytics and reporting
- Comprehensive test suite

## Dependencies

- Python 3.7+
- Standard library only (no external dependencies)
- Uses dataclasses, datetime, json, uuid, re, enum

## Contributing

This is a domain model implementation following the specification in `aidlc-docs/construction/domain_model_notification_service.md`. All components are designed to be simple, intuitive, and maintainable while providing comprehensive functionality for notification management.

## License

Part of the Doctor Appointment Platform project.