# User Management Service

## Unit Overview
The User Management Service is responsible for managing the complete lifecycle of both doctors and patients in the system. This includes registration, profile management, and doctor availability management. This unit provides the foundation for all user-related operations in the platform.

## Business Domain
- Doctor registration and profile management
- Patient registration and profile management  
- Doctor availability and schedule management
- User authentication and authorization

## User Stories

### Doctor Registration and Profile Management

#### US-D001: Doctor Registration
**As a doctor**, I want to register on the platform so that I can offer my services to patients.

**Acceptance Criteria:**
- GIVEN I am a new doctor
- WHEN I access the registration page
- THEN I can enter my basic information (name, email, phone, location)
- AND I can select my medical specialties from a predefined list
- AND I can add my experience details
- AND I can set my rating (initially 0)
- AND I receive a confirmation email upon successful registration

#### US-D002: Doctor Profile Management
**As a registered doctor**, I want to update my profile information so that patients have accurate information about me.

**Acceptance Criteria:**
- GIVEN I am a registered doctor
- WHEN I access my profile page
- THEN I can update my contact information
- AND I can modify my specialties
- AND I can update my experience details
- AND I can view my current rating
- AND changes are saved immediately

### Doctor Availability Management

#### US-D003: Set Individual Time Slots
**As a doctor**, I want to set individual available time slots so that patients can book appointments during my available hours.

**Acceptance Criteria:**
- GIVEN I am a registered doctor
- WHEN I access my availability management page
- THEN I can add individual 1-hour time slots up to one month in advance
- AND I can specify if the slot is for telemedicine or in-person appointments
- AND I can associate different specialties with different time slots
- AND I can see all my scheduled appointments

#### US-D004: Manage Existing Time Slots
**As a doctor**, I want to modify or remove my available time slots so that I can adjust my schedule as needed.

**Acceptance Criteria:**
- GIVEN I have existing time slots
- WHEN I view my availability calendar
- THEN I can remove unbooked time slots
- AND I can modify the appointment type (telemedicine/in-person) for unbooked slots
- AND I cannot modify or remove slots that are already booked

### Patient Registration and Profile Management

#### US-P001: Patient Registration
**As a patient**, I want to register on the platform so that I can book appointments with doctors.

**Acceptance Criteria:**
- GIVEN I am a new patient
- WHEN I access the registration page
- THEN I can enter my basic information (name, email, phone)
- AND I can provide my medical history
- AND I can add emergency contact information
- AND I receive a confirmation email upon successful registration

#### US-P002: Patient Profile Management
**As a patient**, I want to update my profile information so that doctors have accurate information about me.

**Acceptance Criteria:**
- GIVEN I am a registered patient
- WHEN I access my profile page
- THEN I can update my contact information
- AND I can modify my medical history
- AND I can update my emergency contact details
- AND changes are saved immediately

## Integration Requirements

### Outbound Dependencies
- **Notification Service**: Send registration confirmation emails
- **Administration Service**: Provide user data for analytics and management

### Inbound Dependencies
- **Appointment & Matching Service**: Provide doctor availability and profile data
- **Administration Service**: Receive user management commands

### Shared Data Models
- Doctor Profile (ID, name, email, phone, location, specialties, experience, rating)
- Patient Profile (ID, name, email, phone, medical_history, emergency_contact)
- Doctor Availability (doctor_id, datetime, appointment_type, specialty, status)
- Medical Specialties (predefined list)

## API Contracts

### Doctor Management APIs
- POST /doctors/register
- GET /doctors/{id}/profile
- PUT /doctors/{id}/profile
- POST /doctors/{id}/availability
- GET /doctors/{id}/availability
- PUT /doctors/{id}/availability/{slot_id}
- DELETE /doctors/{id}/availability/{slot_id}

### Patient Management APIs
- POST /patients/register
- GET /patients/{id}/profile
- PUT /patients/{id}/profile

### Query APIs (for other services)
- GET /doctors/search (by specialty, location, availability)
- GET /doctors/{id}/available-slots
- GET /patients/{id}/basic-info

## Business Rules
1. Doctor ratings start at 0 and are updated by external systems
2. Time slots are 1-hour intervals
3. Availability can be set up to one month in advance
4. Booked time slots cannot be modified or deleted
5. Each doctor can have multiple specialties
6. Medical specialties are from a predefined list managed by Administration Service