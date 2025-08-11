# Domain Model - Appointment Matching Service

## Overview
This document defines the comprehensive domain model for the Appointment Matching Service. The service is responsible for symptom analysis, doctor-patient matching, appointment booking, and appointment lifecycle management. The model includes both shared components from the platform and service-specific components designed to implement the business logic defined in the user stories.

## Shared Components (from shared_model.md)

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

## Service-Specific Components

### SymptomDescription Component

#### Attributes
```
SymptomDescription {
  // Identity
  id: UUID (Primary Key)
  patient_id: UUID (Foreign Key, required)
  
  // Symptom Information
  symptoms_text: String (required, max 2000 chars)
  parsed_keywords: List<String> (extracted keywords)
  confidence_score: Decimal (0.0-1.0, NLP confidence)
  
  // Analysis Results
  matched_specialties: List<UUID> (references MedicalSpecialty)
  analysis_timestamp: DateTime (when analysis was performed)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (patient user)
  updated_by: UUID (system process)
}
```

#### Behaviors (CRUD Operations)
```
// Create
+ create(symptomData: SymptomDescriptionRequest): SymptomDescription

// Read
+ findById(id: UUID): SymptomDescription
+ findByPatient(patientId: UUID): List<SymptomDescription>
+ findByKeywords(keywords: List<String>): List<SymptomDescription>

// Update
+ update(id: UUID, updates: SymptomUpdateRequest): SymptomDescription
+ updateAnalysisResults(id: UUID, keywords: List<String>, specialties: List<UUID>, confidence: Decimal): SymptomDescription

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateSymptomsText(text: String): Boolean
+ validateConfidenceScore(score: Decimal): Boolean
+ validateSpecialties(specialties: List<UUID>): Boolean
```

#### Relationships
- Many-to-One: SymptomDescription → Patient
- Many-to-Many: SymptomDescription ↔ MedicalSpecialty

### DoctorRecommendation Component

#### Attributes
```
DoctorRecommendation {
  // Identity
  id: UUID (Primary Key)
  symptom_description_id: UUID (Foreign Key, required)
  patient_id: UUID (Foreign Key, required)
  
  // Recommendation Details
  recommended_doctors: List<UUID> (max 3, references Doctor)
  match_scores: List<Decimal> (0.0-1.0, matching confidence per doctor)
  available_slots: List<DateTime> (earliest available slots per doctor)
  
  // Algorithm Metadata
  algorithm_version: String (version of matching algorithm used)
  ranking_factors: String (JSON, factors used in ranking)
  
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
+ create(recommendationData: DoctorRecommendationRequest): DoctorRecommendation

// Read
+ findById(id: UUID): DoctorRecommendation
+ findBySymptomDescription(symptomDescriptionId: UUID): DoctorRecommendation
+ findByPatient(patientId: UUID): List<DoctorRecommendation>

// Update
+ update(id: UUID, updates: RecommendationUpdateRequest): DoctorRecommendation
+ updateRecommendations(id: UUID, doctors: List<UUID>, scores: List<Decimal>, slots: List<DateTime>): DoctorRecommendation

// Delete
+ delete(id: UUID): void

// Validation Rules
+ validateDoctorCount(doctors: List<UUID>): Boolean
+ validateMatchScores(scores: List<Decimal>): Boolean
+ validateAvailableSlots(slots: List<DateTime>): Boolean
```

#### Relationships
- One-to-One: DoctorRecommendation → SymptomDescription
- Many-to-One: DoctorRecommendation → Patient
- Many-to-Many: DoctorRecommendation ↔ Doctor

### SymptomAnalyzer Component

#### Attributes
```
SymptomAnalyzer {
  // Identity
  id: UUID (Primary Key)
  
  // NLP Configuration
  model_name: String (required, NLP model identifier)
  model_version: String (required, model version)
  confidence_threshold: Decimal (0.0-1.0, minimum confidence for matches)
  
  // Keyword Extraction Settings
  max_keywords: Integer (default 20, maximum keywords to extract)
  min_keyword_length: Integer (default 3, minimum character length)
  stop_words: List<String> (words to ignore during analysis)
  
  // Medical Dictionary
  medical_terms: List<String> (medical terminology dictionary)
  specialty_keywords: Map<UUID, List<String>> (specialty to keywords mapping)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Analysis Operations)
```
// Analysis
+ analyzeSymptoms(symptomsText: String): AnalysisResult
+ extractKeywords(text: String): List<String>
+ calculateConfidence(keywords: List<String>, text: String): Decimal
+ identifyMedicalTerms(keywords: List<String>): List<String>

// Configuration
+ updateModel(modelName: String, version: String): SymptomAnalyzer
+ updateThreshold(threshold: Decimal): SymptomAnalyzer
+ addMedicalTerms(terms: List<String>): SymptomAnalyzer
+ updateSpecialtyKeywords(specialtyId: UUID, keywords: List<String>): SymptomAnalyzer

// Validation Rules
+ validateConfidenceThreshold(threshold: Decimal): Boolean
+ validateModelConfiguration(modelName: String, version: String): Boolean
+ validateKeywordSettings(maxKeywords: Integer, minLength: Integer): Boolean
```

### SpecialtyMatcher Component

#### Attributes
```
SpecialtyMatcher {
  // Identity
  id: UUID (Primary Key)
  
  // Matching Configuration
  fuzzy_threshold: Decimal (0.0-1.0, minimum similarity for fuzzy matching)
  exact_match_weight: Decimal (weight for exact keyword matches)
  fuzzy_match_weight: Decimal (weight for fuzzy matches)
  
  // Specialty Mapping
  specialty_keywords: Map<UUID, List<String>> (specialty to keywords mapping)
  keyword_synonyms: Map<String, List<String>> (keyword synonyms for fuzzy matching)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Matching Operations)
```
// Matching
+ matchSpecialties(keywords: List<String>): List<SpecialtyMatch>
+ calculateExactMatches(keywords: List<String>, specialtyId: UUID): Integer
+ calculateFuzzyMatches(keywords: List<String>, specialtyId: UUID): Decimal
+ rankSpecialties(matches: List<SpecialtyMatch>): List<SpecialtyMatch>

// Configuration
+ updateFuzzyThreshold(threshold: Decimal): SpecialtyMatcher
+ updateMatchWeights(exactWeight: Decimal, fuzzyWeight: Decimal): SpecialtyMatcher
+ addSpecialtyKeywords(specialtyId: UUID, keywords: List<String>): SpecialtyMatcher
+ addKeywordSynonyms(keyword: String, synonyms: List<String>): SpecialtyMatcher

// Validation Rules
+ validateFuzzyThreshold(threshold: Decimal): Boolean
+ validateMatchWeights(exactWeight: Decimal, fuzzyWeight: Decimal): Boolean
+ validateSpecialtyKeywords(specialtyId: UUID, keywords: List<String>): Boolean
```

### DoctorRanker Component

#### Attributes
```
DoctorRanker {
  // Identity
  id: UUID (Primary Key)
  
  // Ranking Configuration
  rating_weight: Decimal (weight for doctor rating in ranking)
  availability_weight: Decimal (weight for earliest availability)
  max_recommendations: Integer (default 3, maximum doctors to recommend)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Ranking Operations)
```
// Ranking
+ rankDoctors(doctors: List<Doctor>, specialtyMatches: List<SpecialtyMatch>): List<DoctorRank>
+ calculateRatingScore(rating: Decimal): Decimal
+ calculateAvailabilityScore(earliestSlot: DateTime): Decimal
+ combineScores(ratingScore: Decimal, availabilityScore: Decimal): Decimal

// Configuration
+ updateRankingWeights(ratingWeight: Decimal, availabilityWeight: Decimal): DoctorRanker
+ updateMaxRecommendations(maxRecommendations: Integer): DoctorRanker

// Validation Rules
+ validateRankingWeights(ratingWeight: Decimal, availabilityWeight: Decimal): Boolean
+ validateMaxRecommendations(maxRecommendations: Integer): Boolean
```

### AvailabilityChecker Component

#### Attributes
```
AvailabilityChecker {
  // Identity
  id: UUID (Primary Key)
  
  // Checking Configuration
  booking_window_days: Integer (default 30, days in advance for booking)
  slot_duration_minutes: Integer (default 60, appointment slot duration)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Availability Operations)
```
// Availability Checking
+ checkAvailability(doctorId: UUID, appointmentType: AppointmentType): List<DateTime>
+ getEarliestSlot(doctorId: UUID, appointmentType: AppointmentType): DateTime
+ validateSlotAvailability(doctorId: UUID, datetime: DateTime): Boolean
+ filterByAppointmentType(slots: List<DoctorAvailability>, type: AppointmentType): List<DoctorAvailability>

// Configuration
+ updateBookingWindow(days: Integer): AvailabilityChecker
+ updateSlotDuration(minutes: Integer): AvailabilityChecker

// Validation Rules
+ validateBookingWindow(days: Integer): Boolean
+ validateSlotDuration(minutes: Integer): Boolean
+ validateDateTime(datetime: DateTime): Boolean
```

### BookingValidator Component

#### Attributes
```
BookingValidator {
  // Identity
  id: UUID (Primary Key)
  
  // Validation Rules
  max_booking_days: Integer (default 30, maximum days in advance)
  min_booking_hours: Integer (default 1, minimum hours in advance)
  slot_duration_minutes: Integer (default 60, appointment duration)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Validation Operations)
```
// Booking Validation
+ validateBookingRequest(appointmentData: AppointmentBookingRequest): ValidationResult
+ validateBookingWindow(datetime: DateTime): Boolean
+ validateSlotAvailability(doctorId: UUID, datetime: DateTime): Boolean
+ validatePatientEligibility(patientId: UUID): Boolean
+ validateDoctorStatus(doctorId: UUID): Boolean

// Configuration
+ updateBookingRules(maxDays: Integer, minHours: Integer): BookingValidator
+ updateSlotDuration(minutes: Integer): BookingValidator

// Validation Rules
+ validateBookingDays(maxDays: Integer): Boolean
+ validateBookingHours(minHours: Integer): Boolean
+ validateSlotDuration(minutes: Integer): Boolean
```

### RescheduleValidator Component

#### Attributes
```
RescheduleValidator {
  // Identity
  id: UUID (Primary Key)
  
  // Reschedule Rules
  max_reschedules: Integer (default 2, maximum reschedules per appointment)
  min_justification_length: Integer (default 10, minimum characters for justification)
  reschedule_window_hours: Integer (default 24, minimum hours before appointment)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Validation Operations)
```
// Reschedule Validation
+ validateRescheduleRequest(appointmentId: UUID, rescheduleData: RescheduleRequest): ValidationResult
+ validateRescheduleLimit(appointmentId: UUID): Boolean
+ validateJustification(justification: String): Boolean
+ validateRescheduleWindow(currentDateTime: DateTime, appointmentDateTime: DateTime): Boolean
+ validateNewSlotAvailability(doctorId: UUID, newDateTime: DateTime): Boolean

// Configuration
+ updateRescheduleRules(maxReschedules: Integer, minJustification: Integer, windowHours: Integer): RescheduleValidator

// Validation Rules
+ validateMaxReschedules(maxReschedules: Integer): Boolean
+ validateJustificationLength(minLength: Integer): Boolean
+ validateRescheduleWindow(windowHours: Integer): Boolean
```

### AppointmentStatusManager Component

#### Attributes
```
AppointmentStatusManager {
  // Identity
  id: UUID (Primary Key)
  
  // Status Transition Rules
  allowed_transitions: Map<AppointmentStatus, List<AppointmentStatus>>
  auto_transition_rules: List<StatusTransitionRule>
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Status Management Operations)
```
// Status Management
+ transitionStatus(appointmentId: UUID, newStatus: AppointmentStatus, reason: String): Appointment
+ validateStatusTransition(currentStatus: AppointmentStatus, newStatus: AppointmentStatus): Boolean
+ getValidTransitions(currentStatus: AppointmentStatus): List<AppointmentStatus>
+ processAutoTransitions(): List<Appointment>

// Configuration
+ updateTransitionRules(transitions: Map<AppointmentStatus, List<AppointmentStatus>>): AppointmentStatusManager
+ addAutoTransitionRule(rule: StatusTransitionRule): AppointmentStatusManager

// Validation Rules
+ validateStatusTransition(currentStatus: AppointmentStatus, newStatus: AppointmentStatus): Boolean
+ validateTransitionReason(reason: String): Boolean
```

### UserServiceIntegration Component

#### Attributes
```
UserServiceIntegration {
  // Identity
  id: UUID (Primary Key)
  
  // Integration Configuration
  service_endpoint: String (User Management Service URL)
  api_key: String (authentication key)
  timeout_seconds: Integer (default 30, request timeout)
  retry_attempts: Integer (default 3, maximum retry attempts)
  
  // Circuit Breaker Settings
  failure_threshold: Integer (default 5, failures before opening circuit)
  recovery_timeout_seconds: Integer (default 60, time before attempting recovery)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Integration Operations)
```
// Data Retrieval
+ getDoctorProfile(doctorId: UUID): Doctor
+ getPatientProfile(patientId: UUID): Patient
+ getDoctorAvailability(doctorId: UUID, dateRange: DateRange): List<DoctorAvailability>
+ getMedicalSpecialties(): List<MedicalSpecialty>
+ getDoctorsBySpecialty(specialtyId: UUID): List<Doctor>

// Data Updates
+ updateDoctorAvailability(availabilityId: UUID, status: AvailabilityStatus): DoctorAvailability
+ notifyAvailabilityChange(doctorId: UUID, availabilityId: UUID): Boolean

// Configuration
+ updateEndpoint(endpoint: String): UserServiceIntegration
+ updateTimeout(seconds: Integer): UserServiceIntegration
+ updateRetrySettings(attempts: Integer): UserServiceIntegration

// Validation Rules
+ validateEndpoint(endpoint: String): Boolean
+ validateTimeout(seconds: Integer): Boolean
+ validateRetryAttempts(attempts: Integer): Boolean
```

### AdminServiceIntegration Component

#### Attributes
```
AdminServiceIntegration {
  // Identity
  id: UUID (Primary Key)
  
  // Integration Configuration
  service_endpoint: String (Administration Service URL)
  api_key: String (authentication key)
  timeout_seconds: Integer (default 30, request timeout)
  retry_attempts: Integer (default 3, maximum retry attempts)
  
  // Data Sync Settings
  sync_interval_minutes: Integer (default 60, metrics sync interval)
  batch_size: Integer (default 100, records per batch)
  
  // System Fields
  created_at: DateTime (auto-generated)
  updated_at: DateTime (auto-updated)
  created_by: UUID (admin user)
  updated_by: UUID (admin user)
}
```

#### Behaviors (Integration Operations)
```
// Analytics Data
+ sendAppointmentMetrics(metrics: List<AppointmentMetric>): Boolean
+ sendMatchingMetrics(metrics: List<MatchingMetric>): Boolean
+ sendSystemMetrics(metrics: List<SystemMetric>): Boolean

// Batch Operations
+ batchSendMetrics(metrics: List<Metric>): BatchResult
+ syncAppointmentData(appointments: List<Appointment>): Boolean

// Configuration
+ updateEndpoint(endpoint: String): AdminServiceIntegration
+ updateSyncSettings(intervalMinutes: Integer, batchSize: Integer): AdminServiceIntegration

// Validation Rules
+ validateEndpoint(endpoint: String): Boolean
+ validateSyncInterval(intervalMinutes: Integer): Boolean
+ validateBatchSize(batchSize: Integer): Boolean
```

## Component Relationships and Interactions

### Core Relationships
```
Patient 1:N SymptomDescription
SymptomDescription 1:1 DoctorRecommendation
DoctorRecommendation M:N Doctor
Doctor 1:N DoctorAvailability
DoctorAvailability 1:1 Appointment (when booked)
Appointment M:1 Patient
Appointment M:1 Doctor
Appointment 1:N AppointmentBookingEvent
```

### Service Component Relationships
```
SymptomAnalyzer → SymptomDescription (analyzes)
SpecialtyMatcher → SymptomDescription (matches specialties)
DoctorRanker → DoctorRecommendation (ranks doctors)
AvailabilityChecker → DoctorAvailability (checks availability)
BookingValidator → Appointment (validates booking)
RescheduleValidator → Appointment (validates reschedule)
AppointmentStatusManager → Appointment (manages status)
UserServiceIntegration → Doctor, Patient, DoctorAvailability (fetches data)
AdminServiceIntegration → Appointment (sends analytics)
```

## User Story Implementation Flows

### US-P003: Describe Symptoms
1. Patient submits symptoms text
2. SymptomDescription.create() stores the description
3. SymptomAnalyzer.analyzeSymptoms() processes the text using NLP
4. SymptomAnalyzer.extractKeywords() identifies medical keywords
5. SymptomDescription.updateAnalysisResults() stores parsed results

### US-P004: View Doctor Recommendations
1. SpecialtyMatcher.matchSpecialties() maps symptoms to specialties using fuzzy matching
2. UserServiceIntegration.getDoctorsBySpecialty() fetches relevant doctors
3. AvailabilityChecker.checkAvailability() gets available slots for each doctor
4. DoctorRanker.rankDoctors() ranks by rating and earliest availability
5. DoctorRecommendation.create() stores top 3 recommendations

### US-P005: View Doctor Availability
1. UserServiceIntegration.getDoctorAvailability() fetches doctor's availability
2. AvailabilityChecker.filterByAppointmentType() filters by telemedicine/in-person
3. Return available slots for the next month

### US-P006: Book Appointment
1. BookingValidator.validateBookingRequest() validates the booking
2. AvailabilityChecker.validateSlotAvailability() confirms slot is available
3. Appointment.create() creates the appointment
4. UserServiceIntegration.updateDoctorAvailability() marks slot as booked
5. AppointmentBookingEvent.create() creates booking event
6. Notification triggers sent to both patient and doctor

### US-P007: View My Appointments
1. Appointment.findByPatient() retrieves patient's appointments
2. UserServiceIntegration.getDoctorProfile() enriches with doctor details
3. Return appointment list with doctor information

### US-P008: Reschedule Appointment (Patient)
1. RescheduleValidator.validateRescheduleRequest() validates the request
2. AvailabilityChecker.validateSlotAvailability() confirms new slot availability
3. AppointmentStatusManager.transitionStatus() updates to "rescheduled"
4. Appointment.update() updates with new datetime and reason
5. UserServiceIntegration.updateDoctorAvailability() updates availability slots
6. Notification triggers sent to both parties

### US-D005: Doctor View Appointments
1. Appointment.findByDoctor() retrieves doctor's appointments
2. UserServiceIntegration.getPatientProfile() enriches with patient details
3. Return appointment list with patient information and symptoms

### US-D006: Doctor Reschedule Appointment
1. RescheduleValidator.validateRescheduleRequest() validates doctor's request
2. Appointment.update() stores reschedule proposal with reason
3. AppointmentStatusManager.transitionStatus() updates status
4. Notification sent to patient with proposed alternatives
5. Patient can accept or request different alternatives

## Business Rules and Constraints

### Symptom Analysis Rules
1. NLP confidence threshold must be above configured minimum (default 0.7)
2. Maximum 20 keywords extracted per symptom description
3. Fuzzy matching threshold for specialty mapping (default 0.8)
4. Medical terms dictionary updated by admin users only

### Doctor Matching Rules
1. Maximum 3 doctor recommendations per request
2. Doctors ranked by rating (highest first), then by earliest availability
3. Only active doctors with available slots are recommended
4. Specialty matching uses both exact and fuzzy keyword matching

### Appointment Booking Rules
1. Appointments can only be booked up to 30 days in advance
2. Minimum 1 hour advance booking required
3. Time slots are exactly 60 minutes duration
4. Each slot can only be booked by one patient (confirmed bookings only)
5. Doctor availability must exist and be "available" status

### Rescheduling Rules
1. Maximum 2 reschedules allowed per appointment
2. Reschedule justification required (minimum 10 characters)
3. Minimum 24 hours notice required before appointment
4. New slot must be available and within booking window
5. Both parties notified of reschedule requests

### Integration Rules
1. Fresh data always fetched from User Management Service (no caching)
2. Circuit breaker opens after 5 consecutive failures
3. Maximum 3 retry attempts for failed service calls
4. 30-second timeout for external service calls
5. Analytics data sent to Administration Service in batches

### System Rules
1. All timestamps stored in UTC
2. All UUIDs are version 4 (random)
3. Audit trails maintained for all appointment changes
4. Error handling with correlation IDs for tracing
5. Status transitions follow defined state machine rules

## Component Lifecycle States

### SymptomDescription States
- created → analyzed → matched_to_specialties

### DoctorRecommendation States
- generated → presented → selected/expired

### Appointment Status Transitions
- scheduled → completed
- scheduled → cancelled
- scheduled → rescheduled → scheduled
- scheduled → no_show

### Integration Circuit Breaker States
- closed → open → half_open → closed

This domain model provides a comprehensive foundation for implementing the Appointment Matching Service with clear component definitions, relationships, and business logic flows that support all the defined user stories.