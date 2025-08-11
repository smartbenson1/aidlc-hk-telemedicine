# Shared Component Model

## Overview
This document defines the comprehensive component model for the Doctor Appointment Platform. Each component includes detailed attributes, CRUD behaviors, relationships, and business rules based on the shared data models and user stories.

## Core Entity Components

### Doctor Profile Component

#### Attributes
```
Doctor {
  // Identity
  id: UUID (Primary Key)
  
  // Basic Information
  name: String (required, max 100 chars)
  email: String (required, unique, email format)
  phone: String (required, phone format)
  location: String (required, max 200 chars)
  
  // Professional Information
  specialties: List<UUID> (required, min 1, references MedicalSpecialty)
  experience: String (required, max 1000 chars)
  rating: Decimal (0.0-5.0, default 0.0)
  
  // System Fields
  status: Enum (active, inactive, suspended)
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (system/admin user)
  updated_by: UUID (system/admin user)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(doctorData: DoctorCreateRequest): Doctor

// Read
+ findById(id: UUID): Doctor
+ findByEmail(email: String): Doctor
+ findBySpecialty(specialtyId: UUID): List<Doctor>
+ findAll(): List<Doctor>

// Update
+ update(id: UUID, updates: DoctorUpdateRequest): Doctor
+ updateStatus(id: UUID, status: DoctorStatus): Doctor

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateEmail(email: String): Boolean
+ validatePhone(phone: String): Boolean
+ validateSpecialties(specialties: List<UUID>): Boolean
```

#### Relationships
- One-to-Many: Doctor → DoctorAvailability
- One-to-Many: Doctor → Appointment
- Many-to-Many: Doctor ↔ MedicalSpecialty

### Patient Profile Component

#### Attributes
```
Patient {
  // Identity
  id: UUID (Primary Key)
  
  // Basic Information
  name: String (required, max 100 chars)
  email: String (required, unique, email format)
  phone: String (required, phone format)
  
  // Medical Information
  medical_history: String (max 2000 chars)
  emergency_contact_name: String (required, max 100 chars)
  emergency_contact_phone: String (required, phone format)
  emergency_contact_relationship: String (required, max 50 chars)
  
  // System Fields
  status: Enum (active, inactive, suspended)
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (system/admin user)
  updated_by: UUID (system/admin user)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(patientData: PatientCreateRequest): Patient

// Read
+ findById(id: UUID): Patient
+ findByEmail(email: String): Patient
+ findAll(): List<Patient>

// Update
+ update(id: UUID, updates: PatientUpdateRequest): Patient
+ updateStatus(id: UUID, status: PatientStatus): Patient

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateEmail(email: String): Boolean
+ validatePhone(phone: String): Boolean
+ validateEmergencyContact(name: String, phone: String, relationship: String): Boolean
```

#### Relationships
- One-to-Many: Patient → Appointment

### Medical Specialty Component

#### Attributes
```
MedicalSpecialty {
  // Identity
  id: UUID (Primary Key)
  
  // Basic Information
  name: String (required, unique, max 100 chars)
  description: String (max 500 chars)
  
  // System Fields
  status: Enum (active, inactive)
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(specialtyData: SpecialtyCreateRequest): MedicalSpecialty

// Read
+ findById(id: UUID): MedicalSpecialty
+ findByName(name: String): MedicalSpecialty
+ findAll(): List<MedicalSpecialty>
+ findActive(): List<MedicalSpecialty>

// Update
+ update(id: UUID, updates: SpecialtyUpdateRequest): MedicalSpecialty
+ updateStatus(id: UUID, status: SpecialtyStatus): MedicalSpecialty

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateName(name: String): Boolean
+ validateDescription(description: String): Boolean
```

#### Relationships
- Many-to-Many: MedicalSpecialty ↔ Doctor

## Operational Components

### Doctor Availability Component

#### Attributes
```
DoctorAvailability {
  // Identity
  id: UUID (Primary Key)
  doctor_id: UUID (Foreign Key, required)
  
  // Scheduling Information
  datetime: DateTime (required, future date)
  appointment_type: Enum (telemedicine, in_person)
  specialty_id: UUID (Foreign Key to MedicalSpecialty)
  
  // Status Management
  status: Enum (available, booked, blocked)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (system/admin user)
  updated_by: UUID (system/admin user)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(availabilityData: AvailabilityCreateRequest): DoctorAvailability

// Read
+ findById(id: UUID): DoctorAvailability
+ findByDoctor(doctorId: UUID): List<DoctorAvailability>
+ findByDateRange(start: DateTime, end: DateTime): List<DoctorAvailability>
+ findAvailable(doctorId: UUID, start: DateTime, end: DateTime): List<DoctorAvailability>

// Update
+ update(id: UUID, updates: AvailabilityUpdateRequest): DoctorAvailability
+ updateStatus(id: UUID, status: AvailabilityStatus): DoctorAvailability

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateDateTime(datetime: DateTime): Boolean
+ validateSpecialty(specialtyId: UUID): Boolean
+ validateBookingWindow(datetime: DateTime): Boolean
```

#### Relationships
- Many-to-One: DoctorAvailability → Doctor
- Many-to-One: DoctorAvailability → MedicalSpecialty
- One-to-One: DoctorAvailability → Appointment (when booked)

### Appointment Component

#### Attributes
```
Appointment {
  // Identity
  id: UUID (Primary Key)
  patient_id: UUID (Foreign Key, required)
  doctor_id: UUID (Foreign Key, required)
  availability_id: UUID (Foreign Key, required)
  
  // Appointment Details
  datetime: DateTime (required)
  appointment_type: Enum (telemedicine, in_person)
  symptoms: String (required, max 2000 chars)
  
  // Status Management
  status: Enum (scheduled, completed, cancelled, rescheduled, no_show)
  reschedule_reason: String (nullable, max 500 chars)
  reschedule_count: Integer (default 0, max 2)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (system/admin user)
  updated_by: UUID (system/admin user)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(appointmentData: AppointmentCreateRequest): Appointment

// Read
+ findById(id: UUID): Appointment
+ findByPatient(patientId: UUID): List<Appointment>
+ findByDoctor(doctorId: UUID): List<Appointment>
+ findByDateRange(start: DateTime, end: DateTime): List<Appointment>
+ findUpcoming(): List<Appointment>

// Update
+ update(id: UUID, updates: AppointmentUpdateRequest): Appointment
+ updateStatus(id: UUID, status: AppointmentStatus, reason: String): Appointment

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateBookingWindow(datetime: DateTime): Boolean
+ validateRescheduleLimit(rescheduleCount: Integer): Boolean
+ validateSymptoms(symptoms: String): Boolean
```

#### Relationships
- Many-to-One: Appointment → Patient
- Many-to-One: Appointment → Doctor
- One-to-One: Appointment → DoctorAvailability
- One-to-Many: Appointment → Notification

### Notification Component

#### Attributes
```
Notification {
  // Identity
  id: UUID (Primary Key)
  
  // Recipient Information
  recipient_email: String (required, email format)
  recipient_name: String (required)
  recipient_type: Enum (doctor, patient, admin)
  
  // Notification Details
  notification_type: Enum (registration_confirmation, appointment_booking, 
                          appointment_reminder, reschedule_request, 
                          reschedule_confirmation, system_alert)
  subject: String (required, max 200 chars)
  body: String (required, max 5000 chars)
  
  // Template Information (as attributes)
  template_name: String (required, max 100 chars)
  template_variables: JSON (template data for rendering)
  
  // Scheduling and Delivery
  scheduled_time: DateTime (nullable, for future delivery)
  priority: Enum (low, normal, high, urgent)
  status: Enum (pending, sent, delivered, failed, bounced)
  sent_at: DateTime (nullable)
  delivered_at: DateTime (nullable)
  failure_reason: String (nullable)
  retry_count: Integer (default 0, max 3)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (system/admin user)
  updated_by: UUID (system/admin user)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(notificationData: NotificationCreateRequest): Notification

// Read
+ findById(id: UUID): Notification
+ findByRecipient(email: String): List<Notification>
+ findByType(notificationType: NotificationType): List<Notification>
+ findPending(): List<Notification>
+ findScheduled(): List<Notification>

// Update
+ update(id: UUID, updates: NotificationUpdateRequest): Notification
+ updateStatus(id: UUID, status: NotificationStatus): Notification
+ incrementRetryCount(id: UUID): Notification

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateEmail(email: String): Boolean
+ validateTemplate(templateName: String, variables: JSON): Boolean
+ validateScheduledTime(scheduledTime: DateTime): Boolean
```

#### Relationships
- Many-to-One: Notification → Appointment (optional)

## Administrative Components

### Admin User Component

#### Attributes
```
AdminUser {
  // Identity
  id: UUID (Primary Key)
  
  // Basic Information
  username: String (required, unique, max 50 chars)
  email: String (required, unique, email format)
  name: String (required, max 100 chars)
  
  // Authentication
  password_hash: String (required, encrypted)
  last_login: DateTime (nullable)
  login_attempts: Integer (default 0)
  locked_until: DateTime (nullable)
  
  // Authorization
  role: Enum (super_admin, admin, support)
  permissions: List<String> (role-based permissions)
  
  // System Fields
  status: Enum (active, inactive, locked)
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(adminData: AdminCreateRequest): AdminUser

// Read
+ findById(id: UUID): AdminUser
+ findByUsername(username: String): AdminUser
+ findByEmail(email: String): AdminUser
+ findAll(): List<AdminUser>
+ findByRole(role: AdminRole): List<AdminUser>

// Update
+ update(id: UUID, updates: AdminUpdateRequest): AdminUser
+ updatePassword(id: UUID, passwordHash: String): AdminUser
+ updateStatus(id: UUID, status: AdminStatus): AdminUser

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateUsername(username: String): Boolean
+ validateEmail(email: String): Boolean
+ validateRole(role: AdminRole): Boolean
+ validatePermissions(permissions: List<String>): Boolean
```

#### Relationships
- One-to-Many: AdminUser → AuditLog

### System Metrics Component

#### Attributes
```
SystemMetrics {
  // Identity
  id: UUID (Primary Key)
  
  // Metric Information
  metric_name: String (required, max 100 chars)
  metric_category: Enum (user, appointment, system, business)
  metric_value: Decimal (required)
  metric_unit: String (max 20 chars)
  
  // Context
  period_start: DateTime (required)
  period_end: DateTime (required)
  aggregation_type: Enum (sum, average, count, max, min)
  
  // Metadata
  tags: String (JSON format for filtering and grouping)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (system process)
  updated_by: UUID (system process)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(metricsData: MetricsCreateRequest): SystemMetrics

// Read
+ findById(id: UUID): SystemMetrics
+ findByName(metricName: String): List<SystemMetrics>
+ findByCategory(category: MetricCategory): List<SystemMetrics>
+ findByPeriod(start: DateTime, end: DateTime): List<SystemMetrics>
+ findAll(): List<SystemMetrics>

// Update
+ update(id: UUID, updates: MetricsUpdateRequest): SystemMetrics
+ updateValue(id: UUID, value: Decimal): SystemMetrics

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateMetricName(name: String): Boolean
+ validateValue(value: Decimal): Boolean
+ validatePeriod(start: DateTime, end: DateTime): Boolean
```

### Audit Log Component

#### Attributes
```
AuditLog {
  // Identity
  id: UUID (Primary Key)
  
  // Action Information
  action: String (required, max 100 chars)
  entity_type: String (required, max 50 chars)
  entity_id: UUID (nullable)
  
  // User Information
  user_id: UUID (required)
  user_type: Enum (admin, system, doctor, patient)
  user_name: String (required)
  
  // Entity-level Change Details
  entity_before: String (JSON, nullable, entity state before change)
  entity_after: String (JSON, nullable, entity state after change)
  
  // Context
  ip_address: String (nullable)
  user_agent: String (nullable)
  session_id: String (nullable)
  
  // System Fields
  timestamp: DateTime (auto-generated)
  severity: Enum (info, warning, error, critical)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(auditData: AuditCreateRequest): AuditLog

// Read
+ findById(id: UUID): AuditLog
+ findByEntity(entityType: String, entityId: UUID): List<AuditLog>
+ findByUser(userId: UUID): List<AuditLog>
+ findByAction(action: String): List<AuditLog>
+ findByDateRange(start: DateTime, end: DateTime): List<AuditLog>
+ findAll(): List<AuditLog>

// Update
+ update(id: UUID, updates: AuditUpdateRequest): AuditLog

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateAction(action: String): Boolean
+ validateEntityType(entityType: String): Boolean
+ validateUserType(userType: UserType): Boolean
```

## Event and Integration Components

### User Registration Event

#### Attributes
```
UserRegistrationEvent {
  // Event Identity
  event_id: UUID (Primary Key)
  event_type: String (constant: "user_registered")
  
  // User Information
  user_id: UUID (required)
  user_type: Enum (doctor, patient)
  email: String (required)
  name: String (required)
  
  // Event Metadata
  timestamp: DateTime (auto-generated)
  source_service: String (required)
  correlation_id: UUID (for tracing)
  
  // Processing Status
  status: Enum (pending, processed, failed)
  processed_at: DateTime (nullable)
  error_message: String (nullable)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(eventData: UserRegistrationEventRequest): UserRegistrationEvent

// Read
+ findById(eventId: UUID): UserRegistrationEvent
+ findByUserId(userId: UUID): List<UserRegistrationEvent>
+ findByStatus(status: EventStatus): List<UserRegistrationEvent>
+ findPending(): List<UserRegistrationEvent>

// Update
+ update(eventId: UUID, updates: EventUpdateRequest): UserRegistrationEvent
+ updateStatus(eventId: UUID, status: EventStatus): UserRegistrationEvent

// Delete
+ delete(eventId: UUID): void
```

### Appointment Booking Event

#### Attributes
```
AppointmentBookingEvent {
  // Event Identity
  event_id: UUID (Primary Key)
  event_type: String (constant: "appointment_booked")
  
  // Appointment Information
  appointment_id: UUID (required)
  patient_id: UUID (required)
  doctor_id: UUID (required)
  datetime: DateTime (required)
  symptoms: String (required)
  
  // Event Metadata
  timestamp: DateTime (auto-generated)
  source_service: String (required)
  correlation_id: UUID (for tracing)
  
  // Processing Status
  status: Enum (pending, processed, failed)
  processed_at: DateTime (nullable)
  error_message: String (nullable)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(eventData: AppointmentBookingEventRequest): AppointmentBookingEvent

// Read
+ findById(eventId: UUID): AppointmentBookingEvent
+ findByAppointmentId(appointmentId: UUID): List<AppointmentBookingEvent>
+ findByStatus(status: EventStatus): List<AppointmentBookingEvent>
+ findPending(): List<AppointmentBookingEvent>

// Update
+ update(eventId: UUID, updates: EventUpdateRequest): AppointmentBookingEvent
+ updateStatus(eventId: UUID, status: EventStatus): AppointmentBookingEvent

// Delete
+ delete(eventId: UUID): void
```

### API Request/Response Component

#### Attributes
```
ApiRequestResponse {
  // Identity
  id: UUID (Primary Key)
  
  // Request Information
  request_id: String (required, unique)
  correlation_id: UUID (for tracing)
  service_name: String (required)
  endpoint: String (required)
  http_method: Enum (GET, POST, PUT, DELETE)
  
  // Request/Response Data
  request_headers: String (JSON format)
  request_body: String (JSON format, nullable)
  response_status: Integer (HTTP status code)
  response_headers: String (JSON format)
  response_body: String (JSON format, nullable)
  
  // Timing and Performance
  request_timestamp: DateTime (required)
  response_timestamp: DateTime (nullable)
  duration_ms: Integer (response time in milliseconds)
  
  // Circuit Breaker and Retry Logic
  retry_count: Integer (default 0)
  circuit_breaker_state: Enum (closed, open, half_open)
  failure_reason: String (nullable)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(apiData: ApiRequestResponseRequest): ApiRequestResponse

// Read
+ findById(id: UUID): ApiRequestResponse
+ findByRequestId(requestId: String): ApiRequestResponse
+ findByService(serviceName: String): List<ApiRequestResponse>
+ findByEndpoint(endpoint: String): List<ApiRequestResponse>
+ findFailures(): List<ApiRequestResponse>

// Update
+ update(id: UUID, updates: ApiUpdateRequest): ApiRequestResponse
+ updateResponse(id: UUID, responseData: ApiResponseData): ApiRequestResponse
+ incrementRetryCount(id: UUID): ApiRequestResponse

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateHttpMethod(method: String): Boolean
+ validateStatusCode(statusCode: Integer): Boolean
+ validateCircuitBreakerState(state: String): Boolean
```

### Error and Exception Component

#### Attributes
```
SystemError {
  // Identity
  id: UUID (Primary Key)
  
  // Error Information
  error_code: String (required, max 50 chars)
  error_type: Enum (validation, business, system, integration)
  error_message: String (required, max 500 chars)
  error_details: String (JSON format, detailed error information)
  
  // Context Information
  service_name: String (required)
  component_name: String (required)
  method_name: String (nullable)
  correlation_id: UUID (for tracing)
  
  // User and Request Context
  user_id: UUID (nullable)
  user_type: Enum (admin, doctor, patient, system)
  request_id: String (nullable)
  
  // Retry and Recovery
  is_retryable: Boolean (default false)
  retry_count: Integer (default 0)
  max_retries: Integer (default 3)
  next_retry_at: DateTime (nullable)
  
  // Resolution
  status: Enum (new, in_progress, resolved, ignored)
  resolved_at: DateTime (nullable)
  resolution_notes: String (nullable)
  
  // System Fields
  timestamp: DateTime (auto-generated)
  severity: Enum (low, medium, high, critical)
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(errorData: SystemErrorRequest): SystemError

// Read
+ findById(id: UUID): SystemError
+ findByErrorCode(errorCode: String): List<SystemError>
+ findByType(errorType: ErrorType): List<SystemError>
+ findBySeverity(severity: ErrorSeverity): List<SystemError>
+ findUnresolved(): List<SystemError>
+ findRetryable(): List<SystemError>

// Update
+ update(id: UUID, updates: ErrorUpdateRequest): SystemError
+ updateStatus(id: UUID, status: ErrorStatus): SystemError
+ incrementRetryCount(id: UUID): SystemError
+ markResolved(id: UUID, notes: String): SystemError

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateErrorCode(errorCode: String): Boolean
+ validateSeverity(severity: ErrorSeverity): Boolean
+ validateRetryLogic(isRetryable: Boolean, maxRetries: Integer): Boolean
```

## Business Rules and Constraints

### Global Constraints
1. All entities must have audit fields (created_at, updated_at, created_by, updated_by)
2. All UUIDs are version 4 (random)
3. All timestamps are stored in UTC
4. All string fields have maximum length constraints
5. Email fields must pass email validation
6. Phone fields must pass phone number validation

### Doctor Profile Rules
1. Doctor must have at least one specialty
2. Rating is calculated externally and updated by system
3. Experience field is free text but required
4. Location is required for matching purposes
5. Email must be unique across all doctors
6. Status can be: active, inactive, suspended

### Patient Profile Rules
1. Emergency contact information is mandatory (name, phone, relationship)
2. Medical history is optional but recommended
3. Email must be unique across all patients
4. Phone number must be valid and reachable
5. Status can be: active, inactive, suspended

### Medical Specialty Rules
1. Specialty name must be unique
2. Description is optional but recommended
3. Status can be: active, inactive
4. Cannot be deleted if referenced by doctors

### Doctor Availability Rules
1. DateTime must be in the future
2. Must be within one month booking window
3. Time slots are exactly 1 hour duration
4. Status can be: available, booked, blocked
5. Cannot modify or delete booked slots

### Appointment Rules
1. Appointments can only be booked up to one month in advance
2. Time slots are exactly 1 hour duration
3. Maximum 2 reschedules allowed per appointment
4. Reschedule reason is mandatory when rescheduling
5. Appointments cannot be booked in the past
6. Doctor availability must exist and be available
7. Status can be: scheduled, completed, cancelled, rescheduled, no_show

### Notification Rules
1. Critical notifications (booking confirmations) have highest priority
2. Maximum 3 retry attempts for failed deliveries
3. Reminders are sent 24 hours before appointment
4. Template name and variables are required
5. Delivery status must be tracked
6. Status can be: pending, sent, delivered, failed, bounced

### Administrative Rules
1. Admin users must have unique username and email
2. Password must be hashed before storage
3. Role determines available permissions
4. Account can be locked after failed login attempts
5. Status can be: active, inactive, locked

### System Rules
1. Metrics are calculated in batch processes
2. Audit logs are immutable once created
3. Events are processed asynchronously
4. All API responses include correlation IDs
5. Sensitive data is encrypted at rest and in transit
6. Circuit breaker states: closed, open, half_open
7. Retry logic applies to retryable errors only

## Component Relationships Summary

```
Doctor 1:N DoctorAvailability
Doctor 1:N Appointment
Doctor M:N MedicalSpecialty (through specialty_ids list)
Patient 1:N Appointment
DoctorAvailability 1:1 Appointment (when booked)
Appointment 1:N Notification
AdminUser 1:N AuditLog

Events are loosely coupled and don't have direct relationships
SystemMetrics are aggregated from multiple sources
AuditLog tracks changes to all entities
ApiRequestResponse tracks service communications
SystemError tracks system failures and recovery
```

## Component Lifecycle States

### Doctor Status Transitions
- active ↔ inactive ↔ suspended

### Patient Status Transitions  
- active ↔ inactive ↔ suspended

### Appointment Status Transitions
- scheduled → completed
- scheduled → cancelled
- scheduled → rescheduled → scheduled
- scheduled → no_show

### Notification Status Transitions
- pending → sent → delivered
- pending → sent → failed
- failed → pending (retry)

### Admin Status Transitions
- active ↔ inactive
- active → locked → active

This component model provides a comprehensive foundation for implementing the Doctor Appointment Platform with clear structure, CRUD behaviors, validation rules, and business constraints for each component.