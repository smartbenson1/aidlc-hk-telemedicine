# User Management Service API Documentation

## Overview

The User Management Service API provides comprehensive endpoints for managing users (doctors and patients), sessions, availability, and medical specialties in a healthcare appointment platform.

## Base URL

```
https://your-api-gateway-url.amazonaws.com/
```

## Authentication

Currently, the API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### Health and Status

#### GET /health
Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET /api/health/ready
Comprehensive readiness check with service statistics.

**Response:**
```json
{
  "status": "ready",
  "service": "user-management-service",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": true,
    "email_service": true,
    "admin_service": true,
    "appointment_service": true
  },
  "statistics": {
    "total_users": 150,
    "active_sessions": 25,
    "total_slots": 500
  }
}
```

### Doctor Registration

#### POST /api/doctors/register
Register a new doctor in the system.

**Request Body:**
```json
{
  "name": "Dr. John Smith",
  "email": "john.smith@example.com",
  "phone": "+1234567890",
  "location": "New York, NY",
  "specialties": ["cardiology", "internal-medicine"],
  "experience": "10 years of experience in cardiology and internal medicine"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_type": "doctor",
    "email": "john.smith@example.com",
    "name": "Dr. John Smith",
    "message": "Doctor registered successfully"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/doctors/email-availability
Check if an email address is available for doctor registration.

**Query Parameters:**
- `email` (required): Email address to check

**Response:**
```json
{
  "email": "test@example.com",
  "is_available": true,
  "message": "Email is available for registration"
}
```

#### GET /api/doctors/{doctor_id}
Get doctor profile information.

**Path Parameters:**
- `doctor_id`: UUID of the doctor

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Dr. John Smith",
  "email": "john.smith@example.com",
  "phone": "+1234567890",
  "location": "New York, NY",
  "specialties": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "name": "Cardiology",
      "description": "Heart and cardiovascular system"
    }
  ],
  "experience": "10 years of experience",
  "rating": 4.8,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### PUT /api/doctors/{doctor_id}
Update doctor profile information.

**Path Parameters:**
- `doctor_id`: UUID of the doctor

**Request Body:**
```json
{
  "name": "Dr. John Smith Jr.",
  "phone": "+1234567891",
  "location": "Boston, MA",
  "specialties": ["cardiology"],
  "experience": "12 years of experience in cardiology"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "updated_fields": ["name", "phone", "location", "experience"],
    "message": "Profile updated successfully"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Patient Registration

#### POST /api/patients/register
Register a new patient in the system.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "+1234567890",
  "medical_history": "No significant medical history",
  "emergency_contact_name": "John Doe",
  "emergency_contact_phone": "+1234567891",
  "emergency_contact_relationship": "Spouse"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "789e0123-e89b-12d3-a456-426614174002",
    "user_type": "patient",
    "email": "jane.doe@example.com",
    "name": "Jane Doe",
    "message": "Patient registered successfully"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/patients/{patient_id}
Get patient profile information.

**Path Parameters:**
- `patient_id`: UUID of the patient

**Response:**
```json
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "+1234567890",
  "medical_history": "No significant medical history",
  "emergency_contact": {
    "name": "John Doe",
    "phone": "+1234567891",
    "relationship": "Spouse"
  },
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Session Management

#### POST /api/sessions
Create a new user session.

**Request Body:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_type": "doctor",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "session-123e4567-e89b-12d3-a456-426614174003",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_type": "doctor",
    "expires_at": "2024-01-16T10:30:00Z",
    "message": "Session created successfully"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/sessions/{session_id}/validate
Validate a user session.

**Path Parameters:**
- `session_id`: UUID of the session

**Response:**
```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_type": "doctor",
    "expires_at": "2024-01-16T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Availability Management

#### POST /api/availability/slots
Add a new availability time slot (doctors only).

**Request Body:**
```json
{
  "datetime": "2024-01-20T10:00:00Z",
  "appointment_type": "in_person",
  "specialty_id": "456e7890-e89b-12d3-a456-426614174001"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "slot_id": "slot-123e4567-e89b-12d3-a456-426614174004",
    "doctor_id": "123e4567-e89b-12d3-a456-426614174000",
    "datetime": "2024-01-20T10:00:00Z",
    "appointment_type": "in_person",
    "specialty_id": "456e7890-e89b-12d3-a456-426614174001",
    "message": "Time slot added successfully"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/availability/query
Query availability slots with optional filters.

**Query Parameters:**
- `doctor_id` (optional): Filter by doctor ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `appointment_type` (optional): Filter by appointment type
- `specialty_id` (optional): Filter by specialty ID

**Response:**
```json
{
  "success": true,
  "data": {
    "slots": [
      {
        "id": "slot-123e4567-e89b-12d3-a456-426614174004",
        "doctor_id": "123e4567-e89b-12d3-a456-426614174000",
        "datetime": "2024-01-20T10:00:00Z",
        "appointment_type": "in_person",
        "specialty_id": "456e7890-e89b-12d3-a456-426614174001",
        "status": "available",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total_count": 1,
    "filters": {
      "doctor_id": null,
      "start_date": "2024-01-20",
      "end_date": "2024-01-25",
      "appointment_type": null,
      "specialty_id": null
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Medical Specialties

#### GET /api/specialties
Get all medical specialties.

**Response:**
```json
{
  "success": true,
  "data": {
    "specialties": [
      {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "name": "Cardiology",
        "description": "Heart and cardiovascular system",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total_count": 1
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_TYPE",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req-123e4567-e89b-12d3-a456-426614174005"
}
```

### Common Error Codes

- `VALIDATION_ERROR` (400): Invalid input data
- `AUTHENTICATION_ERROR` (401): Invalid or missing authentication
- `AUTHORIZATION_ERROR` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `BUSINESS_RULE_ERROR` (422): Business logic violation
- `INTERNAL_ERROR` (500): Server error

## Rate Limiting

The API implements rate limiting:
- **Rate Limit**: 100 requests per second
- **Burst Limit**: 200 requests
- **Daily Quota**: 10,000 requests per day

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Data Types

### Appointment Types
- `in_person`: In-person appointment
- `telemedicine`: Remote/video appointment

### User Status
- `active`: User is active
- `inactive`: User is temporarily inactive
- `suspended`: User is suspended

### Slot Status
- `available`: Slot is available for booking
- `booked`: Slot is booked
- `blocked`: Slot is blocked by doctor

## SDK Examples

### Python SDK Example

```python
import requests
import json

class UserManagementClient:
    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
    
    def register_doctor(self, doctor_data):
        """Register a new doctor."""
        response = self.session.post(
            f"{self.base_url}/api/doctors/register",
            json=doctor_data
        )
        return response.json()
    
    def get_doctor_profile(self, doctor_id):
        """Get doctor profile."""
        response = self.session.get(
            f"{self.base_url}/api/doctors/{doctor_id}"
        )
        return response.json()
    
    def query_availability(self, **filters):
        """Query availability slots."""
        response = self.session.get(
            f"{self.base_url}/api/availability/query",
            params=filters
        )
        return response.json()

# Usage example
client = UserManagementClient("https://your-api-url.amazonaws.com")

# Register a doctor
doctor_data = {
    "name": "Dr. Jane Smith",
    "email": "jane.smith@example.com",
    "phone": "+1234567890",
    "location": "Boston, MA",
    "specialties": ["cardiology"],
    "experience": "8 years of experience"
}

result = client.register_doctor(doctor_data)
print(f"Doctor registered: {result['data']['user_id']}")
```

## Interactive Documentation

The API provides interactive documentation:
- **Swagger UI**: `https://your-api-url.amazonaws.com/docs`
- **ReDoc**: `https://your-api-url.amazonaws.com/redoc`

## Support

For API support and questions:
- Review this documentation
- Check the interactive API documentation
- Contact the development team

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial API release
- Doctor and patient registration
- Session management
- Availability management
- Medical specialties management
- Comprehensive error handling
- Rate limiting and security features