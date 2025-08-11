# Appointment Matching Service

A comprehensive Python implementation of an appointment matching service that handles symptom analysis, doctor-patient matching, appointment booking, and appointment lifecycle management.

## Features

- **Symptom Analysis**: NLP-based symptom analysis with keyword extraction and medical term identification
- **Specialty Matching**: Fuzzy matching of symptoms to medical specialties
- **Doctor Recommendations**: Intelligent ranking of doctors based on symptoms, ratings, and availability
- **Appointment Booking**: Complete appointment lifecycle management
- **Validation**: Comprehensive validation with business rules enforcement
- **In-Memory Storage**: Simple repository pattern with in-memory data storage

## Architecture

```
appointment_matching_service/
├── models/           # Domain model classes
├── repositories/     # In-memory repository implementations
├── services/         # Business logic services
├── validators/       # Validation components
├── integrations/     # External service integrations
├── utils/           # Utility classes and helpers
└── tests/           # Unit tests
```

## Quick Start

### Installation

```bash
# Clone or copy the appointment_matching_service directory
cd appointment_matching_service

# Install dependencies (optional - uses standard library)
pip install pytest  # for testing
```

### Basic Usage

```python
from appointment_matching_service.services.appointment_matching_service import AppointmentMatchingService
from appointment_matching_service.models.doctor import Doctor
from appointment_matching_service.models.patient import Patient
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize the service
service = AppointmentMatchingService()

# Create sample data
doctor = Doctor(
    name="Dr. John Smith",
    email="dr.smith@hospital.com",
    phone="+1-555-0123",
    location="New York, NY",
    specialties=["cardiology"],
    experience="10 years of cardiology experience",
    rating=Decimal('4.5')
)

patient = Patient(
    name="Jane Doe",
    email="jane.doe@email.com",
    phone="+1-555-0456",
    emergency_contact_name="John Doe",
    emergency_contact_phone="+1-555-0789",
    emergency_contact_relationship="Spouse"
)

# Save to repositories
saved_doctor = service.doctor_repository.create(doctor)
saved_patient = service.patient_repository.create(patient)

# US-P003: Describe symptoms
symptom_desc = service.describe_symptoms(
    patient_id=saved_patient.id,
    symptoms_text="I have chest pain and shortness of breath"
)

# US-P004: Get doctor recommendations
recommendations = service.get_doctor_recommendations(symptom_desc.id)

# US-P006: Book appointment
appointment_time = datetime.utcnow() + timedelta(days=1)
appointment = service.book_appointment(
    patient_id=saved_patient.id,
    doctor_id=saved_doctor.id,
    appointment_datetime=appointment_time,
    symptoms="Chest pain and shortness of breath"
)

# US-P007: View patient appointments
patient_appointments = service.get_patient_appointments(saved_patient.id)

# US-D005: View doctor appointments
doctor_appointments = service.get_doctor_appointments(saved_doctor.id)

print(f"Created appointment: {appointment.id}")
print(f"Patient has {len(patient_appointments)} appointments")
print(f"Doctor has {len(doctor_appointments)} appointments")
```

## User Story Implementation

### US-P003: Describe Symptoms
```python
# Patient describes symptoms in free text
symptom_desc = service.describe_symptoms(
    patient_id="patient-123",
    symptoms_text="I have been experiencing severe headaches and dizziness"
)
print(f"Analyzed symptoms with confidence: {symptom_desc.confidence_score}")
```

### US-P004: View Doctor Recommendations
```python
# Get up to 3 recommended doctors based on symptoms
recommendations = service.get_doctor_recommendations(symptom_desc.id)
print(f"Found {recommendations.get_recommendation_count()} doctor recommendations")
```

### US-P006: Book Appointment
```python
# Book appointment with selected doctor
appointment = service.book_appointment(
    patient_id="patient-123",
    doctor_id="doctor-456",
    appointment_datetime=datetime.utcnow() + timedelta(days=2),
    symptoms="Headaches and dizziness"
)
```

### US-P008: Reschedule Appointment
```python
# Reschedule existing appointment
new_time = datetime.utcnow() + timedelta(days=3)
rescheduled = service.reschedule_appointment(
    appointment_id=appointment.id,
    new_datetime=new_time,
    reason="Schedule conflict"
)
```

## Key Components

### Models
- **Doctor**: Doctor profile with specialties, rating, and contact info
- **Patient**: Patient profile with medical history and emergency contacts
- **Appointment**: Appointment with status management and rescheduling
- **SymptomDescription**: Symptom analysis with NLP results
- **DoctorRecommendation**: Ranked doctor recommendations

### Services
- **SymptomAnalyzer**: NLP-based symptom analysis
- **SpecialtyMatcher**: Fuzzy matching of symptoms to specialties
- **AppointmentMatchingService**: Main orchestrator service

### Repositories
- **InMemoryRepository**: Base repository with CRUD operations
- **DoctorRepository**: Doctor-specific queries
- **AppointmentRepository**: Appointment-specific queries

## Business Rules

### Symptom Analysis
- NLP confidence threshold: 0.7 (configurable)
- Maximum 20 keywords extracted per symptom description
- Fuzzy matching threshold: 0.8 for specialty mapping

### Doctor Matching
- Maximum 3 doctor recommendations per request
- Doctors ranked by rating (highest first), then by availability
- Only active doctors with available slots are recommended

### Appointment Booking
- Appointments can only be booked up to 30 days in advance
- Minimum 1 hour advance booking required
- Time slots are exactly 60 minutes duration
- Maximum 2 reschedules allowed per appointment

## Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Run specific test
python -m pytest tests/test_appointment_service.py
```

## Configuration

The service uses sensible defaults but can be configured:

```python
# Configure symptom analyzer
service.symptom_analyzer.update_threshold(Decimal('0.8'))
service.symptom_analyzer.add_medical_terms(['migraine', 'hypertension'])

# Configure specialty matcher
service.specialty_matcher.update_fuzzy_threshold(Decimal('0.75'))
service.specialty_matcher.add_specialty_keywords('cardiology', ['heart', 'cardiac'])
```

## Error Handling

The service includes comprehensive error handling:

- **ValidationError**: Data validation failures
- **NotFoundError**: Resource not found
- **BusinessRuleError**: Business rule violations
- **BookingError**: Appointment booking failures
- **AnalysisError**: Symptom analysis failures

## Logging

All components include structured logging:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Service operations are automatically logged
service = AppointmentMatchingService()
# INFO - AppointmentMatchingService - Appointment Matching Service initialized
```

## Limitations

This is a demonstration implementation with the following limitations:

1. **In-Memory Storage**: Data is not persisted between sessions
2. **Simplified NLP**: Basic keyword extraction (not production-grade NLP)
3. **Mock Integrations**: External service calls are simulated
4. **Basic Availability**: Simplified availability checking
5. **No Authentication**: No user authentication or authorization

## Future Enhancements

- Persistent database storage
- Advanced NLP with spaCy or similar
- Real-time availability checking
- Integration with external services
- Web API endpoints
- User authentication and authorization
- Advanced scheduling algorithms
- Notification system integration

## License

This is a demonstration implementation for educational purposes.