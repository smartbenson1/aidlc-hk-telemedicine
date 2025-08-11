# Appointment Matching Service

Intelligent appointment scheduling and doctor recommendation engine.

## Features
- Symptom analysis and interpretation
- Doctor recommendation based on specialties
- Appointment scheduling logic
- Specialty matching algorithms
- Availability management

## Architecture
- Python core logic
- AWS Lambda deployment
- DynamoDB for data storage
- API Gateway for REST endpoints

## Deployment
```bash
cd infrastructure
cdk deploy AppointmentMatchingStack
```

## Local Development
```bash
cd src
python main.py
```

## API Documentation
- Health Check: `/health`
- Symptom Analysis: `/analyze-symptoms`
- Doctor Recommendations: `/recommend-doctors`
- Appointment Booking: `/book-appointment`

See `lambda/api_documentation.yaml` for detailed API specs.
