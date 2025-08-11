# User Management Service - Integration Guide

## Overview

This guide provides comprehensive information for integrating with the User Management Service API. It covers authentication, API endpoints, request/response formats, error handling, and best practices.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Best Practices](#best-practices)
8. [SDK Examples](#sdk-examples)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Installation

```python
# Clone the repository
git clone <repository-url>
cd user_management_service

# Install dependencies (none required - uses standard library only)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Basic Usage

```python
from user_management_service.main import UserManagementServiceDemo

# Initialize the service
service = UserManagementServiceDemo()

# Setup sample data
specialties = service.setup_sample_data()

# Your integration code here...
```

## Authentication

### Session-Based Authentication

The User Management Service uses session-based authentication. All authenticated operations require a valid session ID.

#### Creating a Session

```python
# Create a session for a user
session_result = service.session_manager.create_session(
    user_id="user-uuid-here",
    user_type="doctor",  # or "patient"
    ip_address="192.168.1.100",
    user_agent="YourApp/1.0"
)

if session_result.success:
    session_id = session_result.data.session_id
    expires_at = session_result.data.expires_at
    print(f"Session created: {session_id}")
else:
    print(f"Session creation failed: {session_result.error_message}")
```

#### Validating a Session

```python
# Validate an existing session
validation_result = service.session_manager.validate_session(session_id)

if validation_result.success:
    print("Session is valid")
    user_context = service.session_manager.get_user_context(session_id)
    if user_context.success:
        print(f"User: {user_context.data.user_type} - {user_context.data.user_id}")
else:
    print("Session is invalid or expired")
```

#### Session Management

```python
# Refresh a session (extend expiration)
refresh_result = service.session_manager.refresh_session(session_id)

# Terminate a session
terminate_result = service.session_manager.terminate_session(session_id)
```

## API Endpoints

### Registration Endpoints

#### Register Doctor

```python
from user_management_service.requests.registration_requests import DoctorRegistrationRequest

request = DoctorRegistrationRequest(
    name="Dr. John Smith",
    email="john.smith@example.com",
    phone="(555) 123-4567",
    location="123 Medical Center Dr, New York, NY 10001",
    specialties=[specialty_id_1, specialty_id_2],
    experience="10 years of experience in cardiology."
)

result = service.registration_service.register_doctor(request)
```

#### Register Patient

```python
from user_management_service.requests.registration_requests import PatientRegistrationRequest

request = PatientRegistrationRequest(
    name="Jane Doe",
    email="jane.doe@example.com",
    phone="(555) 987-6543",
    medical_history="No known allergies.",
    emergency_contact_name="John Doe",
    emergency_contact_phone="(555) 987-6544",
    emergency_contact_relationship="spouse"
)

result = service.registration_service.register_patient(request)
```

#### Check Email Availability

```python
availability = service.registration_service.check_email_availability(
    email="test@example.com",
    user_type="doctor"
)

if availability.data:
    print("Email is available")
else:
    print("Email is already taken")
```

### Profile Management Endpoints

#### Get Doctor Profile

```python
profile_result = service.profile_service.get_doctor_profile(
    doctor_id=doctor_id,
    session_id=session_id
)

if profile_result.success:
    profile = profile_result.data
    print(f"Doctor: {profile.name}")
    print(f"Email: {profile.email}")
    print(f"Specialties: {len(profile.specialties)}")
    print(f"Rating: {profile.rating}")
```

#### Update Doctor Profile

```python
from user_management_service.requests.profile_update_requests import DoctorProfileUpdateRequest

update_request = DoctorProfileUpdateRequest(
    phone="(555) 123-4568",
    experience="Updated experience description"
)

result = service.profile_service.update_doctor_profile(
    doctor_id=doctor_id,
    request=update_request,
    session_id=session_id
)

if result.success:
    print(f"Profile updated. Changes: {result.data.changes_made}")
```

#### Get Patient Profile

```python
profile_result = service.profile_service.get_patient_profile(
    patient_id=patient_id,
    session_id=session_id
)
```

#### Update Patient Profile

```python
from user_management_service.requests.profile_update_requests import PatientProfileUpdateRequest

update_request = PatientProfileUpdateRequest(
    phone="(555) 987-6544",
    medical_history="Updated medical history"
)

result = service.profile_service.update_patient_profile(
    patient_id=patient_id,
    request=update_request,
    session_id=session_id
)
```

### Availability Management Endpoints

#### Add Time Slot

```python
from user_management_service.requests.availability_requests import TimeSlotRequest
from user_management_service.utils.enums import AppointmentType
from datetime import datetime, timedelta

# Create a time slot for tomorrow at 2 PM
tomorrow_2pm = datetime.utcnow() + timedelta(days=1)
tomorrow_2pm = tomorrow_2pm.replace(hour=14, minute=0, second=0, microsecond=0)

slot_request = TimeSlotRequest(
    datetime=tomorrow_2pm,
    appointment_type=AppointmentType.IN_PERSON,
    specialty_id=specialty_id
)

result = service.availability_service.add_time_slot(
    doctor_id=doctor_id,
    request=slot_request,
    session_id=session_id
)

if result.success:
    print(f"Time slot added: {result.data.slot_id}")
```

#### Query Doctor Availability

```python
from user_management_service.requests.availability_requests import AvailabilityQuery
from datetime import date, timedelta

query = AvailabilityQuery(
    doctor_id=doctor_id,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=7),
    appointment_type=AppointmentType.IN_PERSON,
    specialty_id=specialty_id
)

result = service.availability_service.get_doctor_availability(query)

if result.success:
    slots = result.data
    print(f"Found {len(slots)} available slots")
    for slot in slots:
        print(f"  {slot.datetime} - {slot.appointment_type}")
```

#### Bulk Add Time Slots

```python
from user_management_service.requests.availability_requests import BulkTimeSlotRequest

# Create multiple time slots
time_slots = []
base_date = datetime.utcnow() + timedelta(days=7)

for day in range(5):  # 5 days
    for hour in [9, 11, 14, 16]:  # 4 slots per day
        slot_time = base_date + timedelta(days=day)
        slot_time = slot_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        time_slots.append(TimeSlotRequest(
            datetime=slot_time,
            appointment_type=AppointmentType.IN_PERSON,
            specialty_id=specialty_id
        ))

bulk_request = BulkTimeSlotRequest(
    doctor_id=doctor_id,
    time_slots=time_slots
)

result = service.availability_service.bulk_add_time_slots(
    request=bulk_request,
    session_id=session_id
)

if result.success:
    print(f"Added {result.data.successful_additions} slots")
    print(f"Failed {result.data.failed_additions} slots")
```

## Request/Response Formats

### Standard Response Format

All API responses follow a consistent format:

```python
class ServiceResult:
    success: bool
    data: Any = None
    error_message: str = None
    error_code: str = None
    metadata: Dict[str, Any] = None
```

### Success Response Example

```python
{
    "success": True,
    "data": {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Dr. John Smith",
        "email": "john.smith@example.com",
        "status": "ACTIVE"
    },
    "error_message": None,
    "error_code": None,
    "metadata": {
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-123"
    }
}
```

### Error Response Example

```python
{
    "success": False,
    "data": None,
    "error_message": "Email address is already registered",
    "error_code": "EMAIL_ALREADY_EXISTS",
    "metadata": {
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-124"
    }
}
```

## Error Handling

### Error Types

The service defines several error types:

```python
from user_management_service.utils.exceptions import (
    ValidationError,
    BusinessRuleViolationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ExternalServiceError
)
```

### Error Handling Pattern

```python
try:
    result = service.registration_service.register_doctor(request)
    
    if result.success:
        # Handle success
        print(f"Doctor registered: {result.data.user_id}")
    else:
        # Handle business logic errors
        print(f"Registration failed: {result.error_message}")
        
        # Check specific error codes
        if result.error_code == "EMAIL_ALREADY_EXISTS":
            # Handle duplicate email
            pass
        elif result.error_code == "INVALID_SPECIALTY":
            # Handle invalid specialty
            pass
            
except ValidationError as e:
    # Handle validation errors
    print(f"Validation error: {e}")
    
except AuthenticationError as e:
    # Handle authentication errors
    print(f"Authentication error: {e}")
    
except ExternalServiceError as e:
    # Handle external service errors
    print(f"External service error: {e}")
    
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {e}")
```

### Common Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `EMAIL_ALREADY_EXISTS` | Email is already registered | Use different email |
| `INVALID_SESSION` | Session is invalid or expired | Create new session |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions | Check user role |
| `VALIDATION_FAILED` | Request validation failed | Fix request data |
| `BUSINESS_RULE_VIOLATION` | Business rule violated | Check business constraints |
| `RESOURCE_NOT_FOUND` | Requested resource not found | Verify resource ID |
| `EXTERNAL_SERVICE_ERROR` | External service unavailable | Retry later |

## Rate Limiting

### Business Rules

The service implements several rate limiting rules:

- **Doctor Registration**: Max 100 per day
- **Patient Registration**: Max 1000 per day
- **Time Slot Creation**: Max 12 per day per doctor
- **Profile Updates**: Max 10 per hour per user
- **Session Creation**: Max 5 per hour per user

### Handling Rate Limits

```python
result = service.registration_service.register_doctor(request)

if not result.success and result.error_code == "RATE_LIMIT_EXCEEDED":
    print(f"Rate limit exceeded: {result.error_message}")
    # Implement retry logic or inform user
```

## Best Practices

### 1. Session Management

```python
class SessionManager:
    def __init__(self, service):
        self.service = service
        self.session_id = None
        self.user_id = None
        
    def login(self, user_id, user_type, ip_address, user_agent):
        result = self.service.session_manager.create_session(
            user_id, user_type, ip_address, user_agent
        )
        
        if result.success:
            self.session_id = result.data.session_id
            self.user_id = user_id
            return True
        return False
    
    def ensure_valid_session(self):
        if not self.session_id:
            raise AuthenticationError("No active session")
            
        validation = self.service.session_manager.validate_session(self.session_id)
        if not validation.success:
            self.session_id = None
            raise AuthenticationError("Session expired")
    
    def logout(self):
        if self.session_id:
            self.service.session_manager.terminate_session(self.session_id)
            self.session_id = None
            self.user_id = None
```

### 2. Error Handling

```python
def safe_api_call(api_function, *args, **kwargs):
    """Wrapper for safe API calls with retry logic."""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = api_function(*args, **kwargs)
            
            if result.success:
                return result
            elif result.error_code in ["EXTERNAL_SERVICE_ERROR", "TEMPORARY_ERROR"]:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
            
            return result
            
        except ExternalServiceError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
                continue
            raise
    
    return ServiceResult(success=False, error_message="Max retries exceeded")
```

### 3. Data Validation

```python
def validate_doctor_registration(request):
    """Validate doctor registration request before submission."""
    errors = []
    
    if not request.name or len(request.name.strip()) < 2:
        errors.append("Name must be at least 2 characters")
    
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', request.email):
        errors.append("Invalid email format")
    
    if not request.specialties or len(request.specialties) == 0:
        errors.append("At least one specialty is required")
    
    if len(request.experience) < 10:
        errors.append("Experience description must be at least 10 characters")
    
    if errors:
        raise ValidationError("; ".join(errors))
```

### 4. Bulk Operations

```python
def process_bulk_registrations(service, doctor_requests):
    """Process multiple doctor registrations with error handling."""
    results = []
    
    for i, request in enumerate(doctor_requests):
        try:
            # Validate request
            validate_doctor_registration(request)
            
            # Submit registration
            result = service.registration_service.register_doctor(request)
            results.append({
                'index': i,
                'success': result.success,
                'data': result.data,
                'error': result.error_message
            })
            
        except ValidationError as e:
            results.append({
                'index': i,
                'success': False,
                'data': None,
                'error': str(e)
            })
        
        # Rate limiting - small delay between requests
        time.sleep(0.1)
    
    return results
```

## SDK Examples

### Python SDK Usage

```python
from user_management_service.main import UserManagementServiceDemo
from user_management_service.requests.registration_requests import DoctorRegistrationRequest

class UserManagementClient:
    def __init__(self):
        self.service = UserManagementServiceDemo()
        self.session_manager = SessionManager(self.service)
    
    def register_doctor(self, doctor_data):
        """Register a new doctor."""
        request = DoctorRegistrationRequest(**doctor_data)
        return self.service.registration_service.register_doctor(request)
    
    def get_doctor_profile(self, doctor_id):
        """Get doctor profile (requires authentication)."""
        self.session_manager.ensure_valid_session()
        return self.service.profile_service.get_doctor_profile(
            doctor_id, self.session_manager.session_id
        )

# Usage
client = UserManagementClient()

# Register doctor
doctor_data = {
    'name': 'Dr. Jane Smith',
    'email': 'jane.smith@example.com',
    'phone': '(555) 123-4567',
    'location': '123 Medical Center',
    'specialties': [specialty_id],
    'experience': 'Board certified cardiologist with 10 years experience'
}

result = client.register_doctor(doctor_data)
if result.success:
    print(f"Doctor registered: {result.data.user_id}")
```

### JavaScript Integration Example

```javascript
// Example of how you might integrate with a JavaScript frontend
class UserManagementAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.sessionId = null;
    }
    
    async registerDoctor(doctorData) {
        const response = await fetch(`${this.baseUrl}/doctors/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(doctorData)
        });
        
        return await response.json();
    }
    
    async getDoctorProfile(doctorId) {
        const response = await fetch(`${this.baseUrl}/doctors/${doctorId}`, {
            headers: {
                'Authorization': `Bearer ${this.sessionId}`,
            }
        });
        
        return await response.json();
    }
}

// Usage
const api = new UserManagementAPI('https://api.example.com');

const doctorData = {
    name: 'Dr. John Doe',
    email: 'john.doe@example.com',
    phone: '(555) 123-4567',
    location: '123 Medical Center',
    specialties: ['cardiology'],
    experience: 'Board certified cardiologist'
};

api.registerDoctor(doctorData)
    .then(result => {
        if (result.success) {
            console.log('Doctor registered:', result.data.user_id);
        } else {
            console.error('Registration failed:', result.error_message);
        }
    });
```

## Testing

### Unit Testing Example

```python
import unittest
from user_management_service.main import UserManagementServiceDemo
from user_management_service.requests.registration_requests import DoctorRegistrationRequest

class TestUserManagementService(unittest.TestCase):
    def setUp(self):
        self.service = UserManagementServiceDemo()
        self.specialties = self.service.setup_sample_data()
    
    def test_doctor_registration_success(self):
        """Test successful doctor registration."""
        request = DoctorRegistrationRequest(
            name="Dr. Test",
            email="test@example.com",
            phone="(555) 123-4567",
            location="Test Location",
            specialties=[self.specialties[0].id],
            experience="Test experience description"
        )
        
        result = self.service.registration_service.register_doctor(request)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data.user_id)
        self.assertEqual(result.data.name, "Dr. Test")
    
    def test_doctor_registration_duplicate_email(self):
        """Test doctor registration with duplicate email."""
        # Register first doctor
        request1 = DoctorRegistrationRequest(
            name="Dr. First",
            email="duplicate@example.com",
            phone="(555) 123-4567",
            location="Test Location",
            specialties=[self.specialties[0].id],
            experience="Test experience description"
        )
        
        result1 = self.service.registration_service.register_doctor(request1)
        self.assertTrue(result1.success)
        
        # Try to register second doctor with same email
        request2 = DoctorRegistrationRequest(
            name="Dr. Second",
            email="duplicate@example.com",
            phone="(555) 123-4568",
            location="Test Location",
            specialties=[self.specialties[0].id],
            experience="Test experience description"
        )
        
        result2 = self.service.registration_service.register_doctor(request2)
        self.assertFalse(result2.success)
        self.assertEqual(result2.error_code, "EMAIL_ALREADY_EXISTS")

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
def test_complete_user_workflow():
    """Test complete user workflow from registration to profile management."""
    service = UserManagementServiceDemo()
    specialties = service.setup_sample_data()
    
    # 1. Register doctor
    doctor_request = DoctorRegistrationRequest(
        name="Dr. Integration Test",
        email="integration@example.com",
        phone="(555) 123-4567",
        location="Test Location",
        specialties=[specialties[0].id],
        experience="Integration test experience"
    )
    
    registration_result = service.registration_service.register_doctor(doctor_request)
    assert registration_result.success
    doctor_id = registration_result.data.user_id
    
    # 2. Create session
    session_result = service.session_manager.create_session(
        doctor_id, "doctor", "127.0.0.1", "TestAgent/1.0"
    )
    assert session_result.success
    session_id = session_result.data.session_id
    
    # 3. Get profile
    profile_result = service.profile_service.get_doctor_profile(doctor_id, session_id)
    assert profile_result.success
    assert profile_result.data.name == "Dr. Integration Test"
    
    # 4. Update profile
    update_request = DoctorProfileUpdateRequest(
        phone="(555) 123-4568"
    )
    
    update_result = service.profile_service.update_doctor_profile(
        doctor_id, update_request, session_id
    )
    assert update_result.success
    assert "phone" in update_result.data.changes_made
    
    # 5. Add availability
    slot_request = TimeSlotRequest(
        datetime=datetime.utcnow() + timedelta(days=1),
        appointment_type=AppointmentType.IN_PERSON,
        specialty_id=specialties[0].id
    )
    
    slot_result = service.availability_service.add_time_slot(
        doctor_id, slot_request, session_id
    )
    assert slot_result.success
    
    print("✅ Complete workflow test passed!")
```

## Troubleshooting

### Common Issues

#### 1. Session Expired Errors

**Problem**: Getting "Invalid session" errors
**Solution**: 
```python
# Check session validity before API calls
validation = service.session_manager.validate_session(session_id)
if not validation.success:
    # Create new session
    session_result = service.session_manager.create_session(...)
```

#### 2. Validation Errors

**Problem**: Request validation failing
**Solution**:
```python
# Validate data before sending
try:
    validate_doctor_registration(request)
    result = service.registration_service.register_doctor(request)
except ValidationError as e:
    print(f"Fix these issues: {e}")
```

#### 3. Business Rule Violations

**Problem**: Time slot creation failing
**Solution**:
```python
# Check business rules
# - Time must be in future (at least 1 hour)
# - Within 30-day booking window
# - During business hours (6 AM - 11 PM)
# - Doctor has selected specialty
# - Not exceeding daily/weekly limits
```

#### 4. External Service Errors

**Problem**: Integration services failing
**Solution**:
```python
# Implement retry logic
def retry_external_call(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except ExternalServiceError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
from user_management_service.utils.logging_utils import setup_logging

# Enable debug logging
setup_logging(level=logging.DEBUG)

# Your code here - will show detailed logs
```

### Health Checks

Monitor service health:

```python
def check_service_health(service):
    """Check overall service health."""
    health_status = {
        'email_service': service.email_service.health_check(),
        'admin_service': service.admin_service.health_check(),
        'appointment_service': service.appointment_service.health_check(),
        'data_persistence': True,  # Check file system access
        'memory_usage': 'normal'   # Check memory usage
    }
    
    all_healthy = all(health_status.values())
    return all_healthy, health_status
```

## Support

For additional support:

1. **Documentation**: See README.md for comprehensive documentation
2. **Examples**: Run `python -m user_management_service.api_examples` for live examples
3. **Demo**: Run `python -m user_management_service.main` for full demo
4. **Issues**: Check error codes and messages for specific guidance

---

This integration guide provides everything needed to successfully integrate with the User Management Service. For the most up-to-date information, always refer to the source code and inline documentation.