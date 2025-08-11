# Appointment Booking System

This document describes the complete appointment booking system implementation for HealMatch Easy.

## 🎯 Overview

The appointment booking system allows patients to:
- Browse available doctors
- View doctor availability by date
- Book appointments with specific time slots
- Receive appointment confirmations
- Cancel appointments if needed

## 🏗️ Architecture

### Backend Components

1. **AppointmentBookingService** (`services/user-management/src/user_management_service/services/appointment_service.py`)
   - Core business logic for appointment management
   - Handles booking, cancellation, and availability checking
   - Integrates with DynamoDB for data persistence

2. **Appointment API Endpoints** (`services/user-management/src/user_management_service/api/routers/appointments.py`)
   - RESTful API endpoints for appointment operations
   - Integrated with Flask application
   - Handles HTTP requests and responses

3. **DynamoDB Schema** (`services/user-management/src/user_management_service/database/appointments_table_schema.py`)
   - Appointments table with GSI for efficient querying
   - Supports queries by patient, doctor, and date

### Frontend Components

1. **AppointmentBooking.tsx** - Complete booking form with:
   - Patient information collection
   - Date and time slot selection
   - Doctor information display
   - Real-time availability checking

2. **AppointmentConfirmation.tsx** - Confirmation page showing:
   - Appointment details
   - Doctor information
   - Next steps for the patient

3. **API Integration** - Updated `api.ts` with appointment endpoints

## 📊 Database Schema

### Appointments Table (`user-management-appointments`)

```
Primary Key: appointment_id (String)

Attributes:
- appointment_id: Unique identifier
- patient_id: Patient identifier
- doctor_id: Doctor identifier  
- appointment_date: Date in YYYY-MM-DD format
- appointment_time: Time in HH:MM format
- duration_minutes: Appointment duration (default: 30)
- reason: Reason for visit
- notes: Additional notes
- status: scheduled | cancelled | completed
- created_at: Creation timestamp
- updated_at: Last update timestamp

Global Secondary Indexes:
- patient-appointments-index: patient_id (HASH) + appointment_date (RANGE)
- doctor-appointments-index: doctor_id (HASH) + appointment_date (RANGE)
```

## 🔌 API Endpoints

### Book Appointment
```
POST /api/appointments
Content-Type: application/json

{
  "patient_id": "string",
  "doctor_id": "string", 
  "appointment_date": "YYYY-MM-DD",
  "appointment_time": "HH:MM",
  "duration_minutes": 30,
  "reason": "string",
  "notes": "string"
}

Response:
{
  "success": true,
  "appointment_id": "string",
  "message": "Appointment booked successfully",
  "appointment": { ... }
}
```

### Get Appointments
```
GET /api/appointments?user_id={id}&user_type={patient|doctor}

Response:
{
  "success": true,
  "appointments": [...]
}
```

### Get Doctor Availability
```
GET /api/appointments/availability/{doctor_id}?date=YYYY-MM-DD

Response:
{
  "success": true,
  "available_slots": ["09:00", "09:30", "10:00", ...],
  "date": "YYYY-MM-DD",
  "doctor_id": "string"
}
```

### Cancel Appointment
```
DELETE /api/appointments/{appointment_id}

Response:
{
  "success": true,
  "message": "Appointment cancelled successfully"
}
```

## 🚀 Deployment

### 1. Setup DynamoDB Table
```bash
python scripts/setup-appointments-table.py
```

### 2. Deploy to Lambda
```bash
python deploy_appointment_service.py
```

### 3. Test the Implementation
```bash
python test_appointment_booking.py
```

## 🧪 Testing

The system includes comprehensive testing:

1. **Unit Tests** - Test individual service methods
2. **Integration Tests** - Test API endpoints
3. **End-to-End Tests** - Test complete booking flow

### Running Tests
```bash
# Test appointment booking service
python test_appointment_booking.py

# Test API endpoints (requires deployed service)
curl -X POST https://your-api-gateway-url/api/appointments \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"test","doctor_id":"test","appointment_date":"2024-01-15","appointment_time":"10:00"}'
```

## 🎨 Frontend Features

### Appointment Booking Page
- **Patient Information Form**: Name, email, phone
- **Doctor Selection**: Shows selected doctor details
- **Date Picker**: Calendar with minimum date validation
- **Time Slot Selection**: Dynamic loading of available slots
- **Appointment Details**: Reason and notes fields
- **Real-time Validation**: Form validation and error handling

### Appointment Confirmation Page
- **Confirmation Details**: Complete appointment information
- **Doctor Information**: Contact details and location
- **Patient Information**: Booking details
- **Next Steps**: Instructions for the patient
- **Navigation Options**: Book another or return home

## 🔧 Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# DynamoDB Tables
APPOINTMENTS_TABLE=user-management-appointments
DOCTORS_TABLE=appointment-matching-doctors
```

### Frontend Configuration
```typescript
// API Configuration in frontend/src/lib/api.ts
export const API_CONFIG = {
  USER_MANAGEMENT: 'https://your-api-gateway-url/prod/api'
};
```

## 📈 Features

### ✅ Implemented
- Complete appointment booking flow
- Doctor availability checking
- Appointment confirmation
- Cancellation functionality
- Real-time form validation
- Responsive design
- Error handling

### 🚧 Future Enhancements
- Email notifications
- SMS reminders
- Calendar integration
- Recurring appointments
- Video consultation support
- Payment integration
- Insurance verification

## 🐛 Troubleshooting

### Common Issues

1. **DynamoDB Table Not Found**
   ```bash
   # Run table setup script
   python scripts/setup-appointments-table.py
   ```

2. **Lambda Function Update Failed**
   ```bash
   # Check AWS credentials and permissions
   aws sts get-caller-identity
   ```

3. **Frontend API Errors**
   ```bash
   # Check API Gateway URL in frontend/src/lib/api.ts
   # Verify CORS configuration
   ```

### Debug Mode
```python
# Enable debug logging in appointment service
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the test scripts for examples
3. Check AWS CloudWatch logs for backend errors
4. Use browser developer tools for frontend debugging

## 🎉 Success!

The appointment booking system is now fully functional with:
- ✅ Backend API endpoints
- ✅ DynamoDB data persistence  
- ✅ Frontend booking interface
- ✅ Confirmation workflow
- ✅ Error handling
- ✅ Testing suite
- ✅ Deployment scripts

Patients can now successfully book appointments with doctors through the HealMatch Easy platform!
## 🔒 Security Notice

⚠️ **Important Security Warning**: 
- Never commit real AWS credentials to version control
- Always use environment variables for sensitive configuration
- The `.env` files are excluded from git by default
- Use AWS IAM roles and credential chain for production deployments

### Frontend Environment Variables
Create a `.env` file in the `frontend/` directory:
```bash
# Copy the example file
cp frontend/.env.example frontend/.env

# Edit with your actual API endpoints
REACT_APP_USER_MANAGEMENT_API=https://your-actual-api-gateway-url/prod/api
REACT_APP_APPOINTMENT_MATCHING_API=https://your-actual-api-gateway-url/prod
REACT_APP_ADMINISTRATION_API=https://your-actual-api-gateway-url/prod/api
```

