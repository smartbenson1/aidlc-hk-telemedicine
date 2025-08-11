# Appointment & Matching Service

## Unit Overview
The Appointment & Matching Service is responsible for the core business logic of the platform: matching patients with suitable doctors based on symptoms and managing the complete appointment lifecycle. This service handles symptom analysis, doctor recommendations, appointment booking, viewing, and rescheduling.

## Business Domain
- Symptom description and analysis
- Doctor-patient matching algorithm
- Appointment booking and confirmation
- Appointment viewing and management
- Appointment rescheduling for both patients and doctors

## User Stories

### Patient Symptom Description and Doctor Matching

#### US-P003: Describe Symptoms
**As a patient**, I want to describe my symptoms in free text so that the system can match me with appropriate doctors.

**Acceptance Criteria:**
- GIVEN I am a registered patient
- WHEN I start the appointment booking process
- THEN I can enter my symptoms and health concerns in a free-text field
- AND the system accepts detailed descriptions
- AND I can proceed to see doctor recommendations

#### US-P004: View Doctor Recommendations
**As a patient**, I want to see recommended doctors based on my symptoms so that I can choose the most suitable one.

**Acceptance Criteria:**
- GIVEN I have described my symptoms
- WHEN the system processes my request
- THEN I see up to 3 recommended doctors
- AND doctors are ranked by rating when symptoms match multiple specialties
- AND I can see each doctor's rating, experience, and location
- AND I can see available appointment slots for each doctor
- AND appointments are prioritized by earliest availability

#### US-P005: View Doctor Availability
**As a patient**, I want to see doctor availability so that I can choose a convenient appointment time.

**Acceptance Criteria:**
- GIVEN I am viewing doctor recommendations
- WHEN I select a doctor
- THEN I can see their available time slots for the next month
- AND I can see if appointments are telemedicine or in-person
- AND I can filter by appointment type if needed

### Appointment Booking and Management

#### US-P006: Book Appointment
**As a patient**, I want to book an appointment with a selected doctor so that I can receive medical care.

**Acceptance Criteria:**
- GIVEN I have selected a doctor and time slot
- WHEN I confirm the booking
- THEN the appointment is created in the system
- AND the doctor receives an email notification
- AND I receive a booking confirmation email
- AND the time slot becomes unavailable to other patients

#### US-P007: View My Appointments
**As a patient**, I want to view my scheduled appointments so that I can keep track of my medical care.

**Acceptance Criteria:**
- GIVEN I am a registered patient
- WHEN I access my appointments page
- THEN I can see all my upcoming appointments
- AND I can see past appointments
- AND each appointment shows doctor details, date, time, and type

#### US-P008: Reschedule Appointment
**As a patient**, I want to reschedule my appointment so that I can adjust to changes in my schedule.

**Acceptance Criteria:**
- GIVEN I have a scheduled appointment
- WHEN I request to reschedule
- THEN I must provide a justification
- AND I can select from available alternative time slots
- AND both the doctor and I receive email notifications about the change

#### US-D005: Doctor View Appointments
**As a doctor**, I want to view my scheduled appointments so that I can prepare for patient consultations.

**Acceptance Criteria:**
- GIVEN I am a registered doctor
- WHEN I access my appointments page
- THEN I can see all my upcoming appointments
- AND I can see patient symptoms and health concerns
- AND I can see patient contact and emergency contact information

#### US-D006: Doctor Reschedule Appointment
**As a doctor**, I want to reschedule appointments when necessary so that I can manage unexpected schedule changes.

**Acceptance Criteria:**
- GIVEN I have a scheduled appointment
- WHEN I request to reschedule
- THEN I must provide a justification
- AND I can propose alternative time slots from my availability
- AND the patient receives an email notification about the proposed change
- AND the patient can accept or request different alternatives

## Integration Requirements

### Outbound Dependencies
- **User Management Service**: Get doctor profiles, availability, and patient information
- **Notification Service**: Send appointment confirmations, reschedule notifications
- **Administration Service**: Provide appointment data for analytics

### Inbound Dependencies
- **User Management Service**: Receive availability updates
- **Notification Service**: Receive notification delivery confirmations

### Shared Data Models
- Appointment (ID, patient_id, doctor_id, datetime, type, status, symptoms, justification)
- Symptom Description (patient_id, symptoms_text, timestamp)
- Doctor Recommendation (doctor_id, match_score, available_slots)
- Appointment Status (scheduled, completed, cancelled, rescheduled)

## API Contracts

### Matching APIs
- POST /matching/analyze-symptoms
- GET /matching/recommend-doctors
- GET /doctors/{id}/availability-details

### Appointment Management APIs
- POST /appointments/book
- GET /appointments/patient/{patient_id}
- GET /appointments/doctor/{doctor_id}
- PUT /appointments/{id}/reschedule
- GET /appointments/{id}/details

### Internal APIs
- POST /appointments/create-internal
- PUT /appointments/{id}/update-status
- GET /appointments/by-date-range

## Business Rules

### Matching Algorithm Rules
1. System matches patients to doctors based on medical specialties
2. When multiple specialties match, doctors are ranked by rating
3. Within the same rating, earliest available appointments are prioritized
4. System recommends maximum 3 doctors per request
5. Symptom analysis uses keyword matching against specialty descriptions

### Appointment Booking Rules
1. Patients can only book appointments up to one month in advance
2. Time slots are 1-hour intervals
3. Each time slot can only be booked by one patient
4. Doctors cannot decline appointment requests once slots are made available
5. Both patients and doctors can reschedule with justification

### Rescheduling Rules
1. Rescheduling requires justification from the requesting party
2. New time slot must be available and within the one-month window
3. Both parties must be notified of reschedule requests
4. Patients can accept doctor reschedule proposals or request alternatives
5. Maximum 2 reschedules allowed per appointment

## Matching Algorithm Logic
1. Parse symptom text for medical keywords
2. Map keywords to medical specialties using predefined mapping
3. Query available doctors by matching specialties
4. Rank doctors by rating (highest first)
5. Within same rating, prioritize by earliest available appointment
6. Return top 3 recommendations with available time slots