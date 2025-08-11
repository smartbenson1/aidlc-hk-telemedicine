# DynamoDB Schema Design for User Management Service

## Overview
This document defines the DynamoDB table structure for the User Management Service, migrating from file-based JSON storage to a scalable NoSQL database.

## Design Principles
- **Single Table Design**: Use a single DynamoDB table with composite keys for optimal performance
- **Access Patterns**: Design based on query patterns from the existing service
- **Scalability**: Support for high read/write throughput
- **Cost Optimization**: Minimize table count and optimize for on-demand billing

## Table Structure

### Primary Table: `user-management-service`

#### Primary Key Structure
- **Partition Key (PK)**: Entity type and identifier
- **Sort Key (SK)**: Sub-entity type and identifier or timestamp

#### Global Secondary Indexes (GSI)

##### GSI1: Email Index
- **GSI1PK**: `EMAIL#{email}`
- **GSI1SK**: `USER#{user_type}`
- **Purpose**: Email uniqueness checks and user lookup by email

##### GSI2: Doctor Specialty Index
- **GSI2PK**: `SPECIALTY#{specialty_id}`
- **GSI2SK**: `DOCTOR#{doctor_id}`
- **Purpose**: Find doctors by specialty

##### GSI3: Availability Query Index
- **GSI3PK**: `AVAILABILITY#{doctor_id}`
- **GSI3SK**: `DATE#{date}#{time}`
- **Purpose**: Query doctor availability by date range

## Entity Patterns

### 1. Doctor Entity
```
PK: DOCTOR#{doctor_id}
SK: PROFILE
GSI1PK: EMAIL#{email}
GSI1SK: USER#doctor

Attributes:
- id: UUID
- name: String
- email: String
- phone: String
- location: String
- specialties: List<UUID>
- experience: String
- rating: Number
- status: String (ACTIVE, INACTIVE, SUSPENDED)
- created_at: ISO8601 String
- updated_at: ISO8601 String
- entity_type: "doctor"
```

### 2. Patient Entity
```
PK: PATIENT#{patient_id}
SK: PROFILE
GSI1PK: EMAIL#{email}
GSI1SK: USER#patient

Attributes:
- id: UUID
- name: String
- email: String
- phone: String
- medical_history: String
- emergency_contact: Map {
    name: String,
    phone: String,
    relationship: String
  }
- status: String (ACTIVE, INACTIVE, SUSPENDED)
- created_at: ISO8601 String
- updated_at: ISO8601 String
- entity_type: "patient"
```

### 3. Medical Specialty Entity
```
PK: SPECIALTY#{specialty_id}
SK: METADATA

Attributes:
- id: UUID
- name: String
- description: String
- status: String (ACTIVE, INACTIVE)
- created_at: ISO8601 String
- updated_at: ISO8601 String
- entity_type: "specialty"
```

### 4. Doctor Availability Entity
```
PK: DOCTOR#{doctor_id}
SK: AVAILABILITY#{datetime}
GSI3PK: AVAILABILITY#{doctor_id}
GSI3SK: DATE#{date}#{time}

Attributes:
- id: UUID
- doctor_id: UUID
- datetime: ISO8601 String
- appointment_type: String (IN_PERSON, TELEMEDICINE)
- specialty_id: UUID
- status: String (AVAILABLE, BOOKED, CANCELLED)
- created_at: ISO8601 String
- updated_at: ISO8601 String
- entity_type: "availability"
```

### 5. User Session Entity
```
PK: SESSION#{session_id}
SK: METADATA

Attributes:
- session_id: UUID
- user_id: UUID
- user_type: String (doctor, patient)
- ip_address: String
- user_agent: String
- created_at: ISO8601 String
- expires_at: ISO8601 String
- is_active: Boolean
- entity_type: "session"
- ttl: Number (Unix timestamp for automatic deletion)
```

### 6. Event Entity (for event publishing)
```
PK: EVENT#{event_id}
SK: TIMESTAMP#{timestamp}

Attributes:
- event_id: UUID
- event_type: String (user_registered, profile_updated, availability_updated)
- user_id: UUID
- user_type: String
- event_data: Map
- status: String (PENDING, PROCESSED, FAILED)
- created_at: ISO8601 String
- processed_at: ISO8601 String (optional)
- entity_type: "event"
- ttl: Number (Unix timestamp for automatic deletion after 30 days)
```

## Access Patterns and Queries

### 1. User Registration
- **Check email availability**: Query GSI1 with `GSI1PK = EMAIL#{email}`
- **Create user**: Put item with `PK = USER_TYPE#{user_id}`, `SK = PROFILE`

### 2. User Authentication/Sessions
- **Create session**: Put item with `PK = SESSION#{session_id}`, `SK = METADATA`
- **Validate session**: Get item with `PK = SESSION#{session_id}`, `SK = METADATA`
- **Get user by session**: Get item, then query user by user_id

### 3. Profile Management
- **Get user profile**: Get item with `PK = USER_TYPE#{user_id}`, `SK = PROFILE`
- **Update profile**: Update item with same key

### 4. Doctor Availability
- **Add availability**: Put item with `PK = DOCTOR#{doctor_id}`, `SK = AVAILABILITY#{datetime}`
- **Query availability by doctor**: Query with `PK = DOCTOR#{doctor_id}`, `SK begins_with AVAILABILITY`
- **Query availability by date range**: Query GSI3 with `GSI3PK = AVAILABILITY#{doctor_id}`, `GSI3SK between DATE#{start_date} and DATE#{end_date}`

### 5. Medical Specialties
- **Get all specialties**: Scan with filter `entity_type = specialty` (or maintain in separate table)
- **Get specialty by ID**: Get item with `PK = SPECIALTY#{specialty_id}`, `SK = METADATA`

### 6. Statistics and Analytics
- **Count users by type**: Scan with filter on entity_type (consider using DynamoDB Streams for real-time counts)
- **Session statistics**: Scan sessions with filters on created_at and status

## Table Configuration

### Provisioned vs On-Demand
- **Recommendation**: On-Demand billing for variable workloads
- **Alternative**: Provisioned with auto-scaling for predictable traffic

### Indexes
- **Local Secondary Indexes**: None required
- **Global Secondary Indexes**: 3 GSIs as defined above

### TTL Configuration
- **Sessions**: TTL on `expires_at` field for automatic cleanup
- **Events**: TTL after 30 days for audit trail cleanup

### Backup and Recovery
- **Point-in-time Recovery**: Enable for production
- **Backup**: Daily automated backups
- **Cross-region replication**: Not required based on requirements

## Migration Strategy

### Phase 1: Dual Write
1. Keep existing file-based repositories
2. Add DynamoDB repositories alongside
3. Write to both systems during transition

### Phase 2: Read Migration
1. Migrate read operations to DynamoDB
2. Keep file system as backup
3. Validate data consistency

### Phase 3: Full Migration
1. Switch all operations to DynamoDB
2. Remove file-based repositories
3. Archive existing JSON files

### Data Migration Script
```python
# Pseudo-code for migration
def migrate_data():
    # Load existing JSON data
    doctors = load_json('doctors.json')
    patients = load_json('patients.json')
    specialties = load_json('medical_specialties.json')
    availability = load_json('doctor_availability.json')
    sessions = load_json('user_sessions.json')
    
    # Transform and load into DynamoDB
    for doctor in doctors:
        put_doctor_to_dynamodb(doctor)
    
    for patient in patients:
        put_patient_to_dynamodb(patient)
    
    # ... continue for other entities
```

## Performance Considerations

### Read Patterns
- **Hot partitions**: Distribute load across multiple partition keys
- **Consistent reads**: Use eventually consistent reads where possible
- **Batch operations**: Use batch_get_item for multiple items

### Write Patterns
- **Batch writes**: Use batch_write_item for bulk operations
- **Conditional writes**: Use condition expressions for data integrity
- **Atomic updates**: Use update expressions for partial updates

### Cost Optimization
- **Projection**: Only project required attributes in GSIs
- **Sparse indexes**: Use sparse GSIs for optional attributes
- **Compression**: Store large text fields compressed if needed

## Monitoring and Alerting

### CloudWatch Metrics
- **Read/Write capacity utilization**
- **Throttled requests**
- **Error rates**
- **Latency metrics**

### Alarms
- **High error rates**
- **Capacity utilization > 80%**
- **Throttling events**
- **High latency**

## Security

### Encryption
- **At rest**: Enable DynamoDB encryption
- **In transit**: Use HTTPS/TLS for all connections

### Access Control
- **IAM roles**: Least privilege access
- **VPC endpoints**: If using VPC (not required per requirements)
- **Audit logging**: CloudTrail for API calls

## Example Item Structures

### Doctor Item
```json
{
  "PK": "DOCTOR#123e4567-e89b-12d3-a456-426614174000",
  "SK": "PROFILE",
  "GSI1PK": "EMAIL#john.smith@example.com",
  "GSI1SK": "USER#doctor",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Dr. John Smith",
  "email": "john.smith@example.com",
  "phone": "(555) 123-4567",
  "location": "123 Medical Center Dr",
  "specialties": ["specialty-uuid-1", "specialty-uuid-2"],
  "experience": "10 years of experience",
  "rating": 4.5,
  "status": "ACTIVE",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "entity_type": "doctor"
}
```

### Availability Item
```json
{
  "PK": "DOCTOR#123e4567-e89b-12d3-a456-426614174000",
  "SK": "AVAILABILITY#2024-01-16T14:00:00Z",
  "GSI3PK": "AVAILABILITY#123e4567-e89b-12d3-a456-426614174000",
  "GSI3SK": "DATE#2024-01-16#14:00:00",
  "id": "availability-uuid",
  "doctor_id": "123e4567-e89b-12d3-a456-426614174000",
  "datetime": "2024-01-16T14:00:00Z",
  "appointment_type": "IN_PERSON",
  "specialty_id": "specialty-uuid-1",
  "status": "AVAILABLE",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "entity_type": "availability"
}
```

This schema design provides a scalable, cost-effective solution that maintains the existing functionality while enabling cloud-native features like automatic scaling, backup, and monitoring.