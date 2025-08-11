# User Stories Development Plan

## Project Overview
Doctor appointment platform that connects patients with medical specialists efficiently by matching symptoms/health concerns with doctor specialties and availability.

## Development Plan

### Phase 1: Requirements Analysis and Stakeholder Identification
- [x] 1.1 Identify all user types and stakeholders
  - Primary users: Patients, Doctors
  - Secondary users: Admin/Support staff
  - [Question] Are there any other user types we should consider (e.g., clinic administrators, insurance providers, medical assistants)?
  - [Answer] No

- [x] 1.2 Define core system boundaries and scope
  - [Question] Should the system handle payment processing, or will that be external?
  - [Answer] No
  - [Question] Do we need to integrate with existing Electronic Health Records (EHR) systems?
  - [Answer] No
  - [Question] Should the system support telemedicine/virtual appointments or only in-person?
  - [Answer] Yes, it should support both telemedicine and in-person.

### Phase 2: Doctor Journey Analysis
- [x] 2.1 Map doctor registration and profile setup process
  - [Question] What verification process is required for doctors (medical license verification, credentials)?
  - [Answer] No
  - [Question] Can doctors set different availability for different specialties if they have multiple?
  - [Answer] Yes. 

- [x] 2.2 Define availability management requirements
  - [Question] How granular should time slots be (15 min, 30 min, 1 hour intervals)?
  - [Answer] 1 hour
  - [Question] Should doctors be able to set recurring schedules or only individual time slots?
  - [Answer] Individual slots
  - [Question] Do we need to handle emergency slots or urgent care availability?
  - [Answer] No

- [x] 2.3 Identify doctor notification and communication needs
  - [Question] How should doctors be notified of new appointment requests?
  - [Answer] Through emails. 
  - [Question] Can doctors decline appointment requests, and if so, what happens next?
  - [Answer] No.

### Phase 3: Patient Journey Analysis
- [x] 3.1 Map patient registration and profile creation
  - [Question] What patient information is required for registration (insurance, medical history, emergency contacts)?
  - [Answer] medical history, emergency contacts
  - [Question] Should patients be able to create accounts without booking immediately?
  - [Answer] Yes.

- [x] 3.2 Define symptom description and matching process
  - [Question] Should the system use structured symptom selection (dropdown/checkboxes) or free-text description?
  - [Answer] Free-text description
  - [Question] Do we need to capture urgency levels for symptoms?
  - [Answer] No
  - [Question] Should the system ask follow-up questions based on initial symptoms?
  - [Answer] No

- [x] 3.3 Define appointment selection and booking process
  - [Question] How many doctor options should the system recommend to patients?
  - [Answer] 3 doctors.
  - [Question] What information about doctors should be shown to patients (ratings, experience, location, cost)?
  - [Answer] Ratings, experience, location
  - [Question] Can patients see doctor availability before or after describing symptoms?
  - [Answer] Yes.

### Phase 4: System Matching Logic Requirements
- [x] 4.1 Define specialty matching criteria
  - [Question] Should the system use a predefined list of medical specialties or allow custom entries?
  - [Answer] A predefined list of medical specilties.
  - [Question] How should the system handle cases where symptoms could match multiple specialties?
  - [Answer] Based on rating.

- [x] 4.2 Define availability matching logic
  - [Question] Should the system prioritize earliest available appointments or best specialty matches?
  - [Answer] Earliest appointment
  - [Question] How far in advance should patients be able to book appointments?
  - [Answer] One month

### Phase 5: Administrative and Support Features
- [x] 5.1 Define appointment management requirements
  - [Question] Who can cancel/reschedule appointments and under what conditions?
  - [Answer] Either patient or doctor can reschedule appointment by providing justification. And an email will be sent to notify.
  - [Question] Should there be automated reminders, and if so, how far in advance?
  - [Answer] 1 day in advance.

- [x] 5.2 Define system administration needs
  - [Question] Do we need reporting/analytics features for system usage?
  - [Answer] Yes
  - [Question] Should there be admin controls for managing doctors, patients, or specialties?
  - [Answer] Yes.

### Phase 6: User Story Creation
- [x] 6.1 Write epic-level user stories for each major user journey
- [x] 6.2 Break down epics into detailed user stories with acceptance criteria
- [x] 6.3 Prioritize user stories based on core functionality
- [x] 6.4 Review and validate user stories against business objectives

### Phase 7: Documentation and Review
- [x] 7.1 Create comprehensive user story document
- [x] 7.2 Add acceptance criteria using EARS format where applicable
- [x] 7.3 Include edge cases and error scenarios
- [x] 7.4 Final review and stakeholder approval

## Questions for Immediate Clarification
[Question] What is the primary business model - subscription for doctors, per-appointment fees, or other?
[Answer] per-appointment fee.

[Question] Are there any regulatory compliance requirements we need to consider (HIPAA, GDPR, etc.)?
[Answer] No.

[Question] What is the expected scale - local/regional or national/international platform?
[Answer] It's a local platform, targeting at 30 doctors and 200 appointment per day. 

[Question] Should the system support multiple languages?
[Answer] Only English.