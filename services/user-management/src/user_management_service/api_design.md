# User Management Service API Design

## API Endpoints Overview

Based on the existing domain services, here are the REST API endpoints:

### 1. Registration Endpoints

#### POST /api/doctors/register
- **Purpose**: Register a new doctor
- **Request Body**: DoctorRegistrationRequest
- **Response**: RegistrationResult
- **Status Codes**: 201 (Created), 400 (Validation Error), 409 (Email Exists)

#### POST /api/patients/register
- **Purpose**: Register a new patient
- **Request Body**: PatientRegistrationRequest
- **Response**: RegistrationResult
- **Status Codes**: 201 (Created), 400 (Validation Error), 409 (Email Exists)

#### GET /api/registration/email-availability
- **Purpose**: Check if email is available
- **Query Parameters**: email (string), user_type (doctor|patient)
- **Response**: EmailAvailabilityResult
- **Status Codes**: 200 (OK), 400 (Invalid Parameters)

#### GET /api/registration/statistics
- **Purpose**: Get registration statistics
- **Response**: RegistrationStatistics
- **Status Codes**: 200 (OK)

### 2. Session Management Endpoints

#### POST /api/sessions
- **Purpose**: Create a new user session
- **Request Body**: SessionCreateRequest
- **Response**: SessionResult
- **Status Codes**: 201 (Created), 400 (Validation Error), 404 (User Not Found)

#### GET /api/sessions/{session_id}
- **Purpose**: Validate a session
- **Path Parameters**: session_id (UUID)
- **Response**: SessionValidationResult
- **Status Codes**: 200 (OK), 404 (Session Not Found)

#### PUT /api/sessions/{session_id}/refresh
- **Purpose**: Refresh a session
- **Path Parameters**: session_id (UUID)
- **Response**: SessionResult
- **Status Codes**: 200 (OK), 404 (Session Not Found)

#### DELETE /api/sessions/{session_id}
- **Purpose**: Terminate a session
- **Path Parameters**: session_id (UUID)
- **Response**: Success message
- **Status Codes**: 200 (OK), 404 (Session Not Found)

#### GET /api/sessions/{session_id}/context
- **Purpose**: Get user context from session
- **Path Parameters**: session_id (UUID)
- **Response**: UserContext
- **Status Codes**: 200 (OK), 404 (Session Not Found)

#### GET /api/sessions/statistics
- **Purpose**: Get session statistics
- **Response**: SessionStatistics
- **Status Codes**: 200 (OK)

### 3. Profile Management Endpoints

#### GET /api/doctors/{doctor_id}/profile
- **Purpose**: Get doctor profile
- **Path Parameters**: doctor_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Response**: DoctorProfileView
- **Status Codes**: 200 (OK), 401 (Unauthorized), 404 (Not Found)

#### PUT /api/doctors/{doctor_id}/profile
- **Purpose**: Update doctor profile
- **Path Parameters**: doctor_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Request Body**: DoctorProfileUpdateRequest
- **Response**: ProfileUpdateResult
- **Status Codes**: 200 (OK), 400 (Validation Error), 401 (Unauthorized), 404 (Not Found)

#### GET /api/patients/{patient_id}/profile
- **Purpose**: Get patient profile
- **Path Parameters**: patient_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Response**: PatientProfileView
- **Status Codes**: 200 (OK), 401 (Unauthorized), 404 (Not Found)

#### PUT /api/patients/{patient_id}/profile
- **Purpose**: Update patient profile
- **Path Parameters**: patient_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Request Body**: PatientProfileUpdateRequest
- **Response**: ProfileUpdateResult
- **Status Codes**: 200 (OK), 400 (Validation Error), 401 (Unauthorized), 404 (Not Found)

### 4. Doctor Availability Endpoints

#### POST /api/doctors/{doctor_id}/availability
- **Purpose**: Add a time slot
- **Path Parameters**: doctor_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Request Body**: TimeSlotRequest
- **Response**: AvailabilityResult
- **Status Codes**: 201 (Created), 400 (Validation Error), 401 (Unauthorized), 409 (Conflict)

#### PUT /api/doctors/{doctor_id}/availability/{slot_id}
- **Purpose**: Modify a time slot
- **Path Parameters**: doctor_id (UUID), slot_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Request Body**: TimeSlotRequest
- **Response**: AvailabilityResult
- **Status Codes**: 200 (OK), 400 (Validation Error), 401 (Unauthorized), 404 (Not Found)

#### DELETE /api/doctors/{doctor_id}/availability/{slot_id}
- **Purpose**: Remove a time slot
- **Path Parameters**: doctor_id (UUID), slot_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Response**: Success message
- **Status Codes**: 200 (OK), 401 (Unauthorized), 404 (Not Found)

#### GET /api/doctors/availability
- **Purpose**: Query doctor availability
- **Query Parameters**: doctor_id (UUID), start_date (date), end_date (date), appointment_type (optional), specialty_id (optional)
- **Response**: List[DoctorAvailability]
- **Status Codes**: 200 (OK), 400 (Invalid Parameters)

#### POST /api/doctors/{doctor_id}/availability/bulk
- **Purpose**: Bulk add time slots
- **Path Parameters**: doctor_id (UUID)
- **Headers**: X-Session-ID (UUID)
- **Request Body**: BulkAvailabilityRequest
- **Response**: BulkAvailabilityResult
- **Status Codes**: 200 (OK), 400 (Validation Error), 401 (Unauthorized)

#### GET /api/doctors/availability/statistics
- **Purpose**: Get availability statistics
- **Response**: AvailabilityStatistics
- **Status Codes**: 200 (OK)

### 5. Medical Specialties Endpoints

#### GET /api/specialties
- **Purpose**: Get all medical specialties
- **Response**: List[MedicalSpecialty]
- **Status Codes**: 200 (OK)

#### GET /api/specialties/{specialty_id}
- **Purpose**: Get a specific medical specialty
- **Path Parameters**: specialty_id (UUID)
- **Response**: MedicalSpecialty
- **Status Codes**: 200 (OK), 404 (Not Found)

### 6. Health and Monitoring Endpoints

#### GET /api/health
- **Purpose**: Health check endpoint
- **Response**: HealthStatus
- **Status Codes**: 200 (OK), 503 (Service Unavailable)

#### GET /api/health/ready
- **Purpose**: Readiness check endpoint
- **Response**: ReadinessStatus
- **Status Codes**: 200 (OK), 503 (Not Ready)

#### GET /api/metrics
- **Purpose**: Get service metrics
- **Response**: ServiceMetrics
- **Status Codes**: 200 (OK)

## Request/Response Models

### Common Models
```python
class BaseResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime
    request_id: str

class ErrorResponse(BaseResponse):
    error_code: str
    details: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseResponse):
    data: List[Any]
    pagination: PaginationInfo

class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
```

### Session Models
```python
class SessionCreateRequest(BaseModel):
    user_id: UUID
    user_type: str  # "doctor" or "patient"
    ip_address: str
    user_agent: str

class SessionResult(BaseResponse):
    data: SessionData

class SessionData(BaseModel):
    session_id: UUID
    user_id: UUID
    user_type: str
    expires_at: datetime
```

### Health Check Models
```python
class HealthStatus(BaseModel):
    status: str  # "healthy" or "unhealthy"
    version: str
    timestamp: datetime
    checks: Dict[str, CheckResult]

class CheckResult(BaseModel):
    status: str
    message: str
    duration_ms: float
```

## Error Handling Strategy

### HTTP Status Codes
- **200 OK**: Successful GET, PUT, DELETE operations
- **201 Created**: Successful POST operations
- **400 Bad Request**: Validation errors, malformed requests
- **401 Unauthorized**: Authentication required or invalid session
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists or business rule violation
- **422 Unprocessable Entity**: Business logic validation errors
- **429 Too Many Requests**: Rate limiting
- **500 Internal Server Error**: Unexpected server errors
- **503 Service Unavailable**: Service temporarily unavailable

### Error Response Format
```python
{
    "success": false,
    "message": "Validation failed",
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-123456",
    "details": {
        "field_errors": {
            "email": ["Email format is invalid"],
            "phone": ["Phone number is required"]
        }
    }
}
```

## Authentication Strategy (Future)
- **Current**: No authentication (public API)
- **Future**: JWT tokens or AWS Cognito
- **Session Header**: X-Session-ID for session-based operations
- **API Key Header**: X-API-Key for future API key authentication

## Rate Limiting
- **Global Limit**: 100 requests per second
- **Per-IP Limit**: 50 requests per minute
- **Burst Limit**: 200 requests in 10 seconds

## CORS Configuration
- **Allowed Origins**: * (all domains)
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, X-Session-ID, X-API-Key
- **Max Age**: 3600 seconds

## API Versioning (Future)
- **Current**: No versioning
- **Future**: URL path versioning (/api/v1/, /api/v2/)
- **Header Versioning**: Accept-Version header support