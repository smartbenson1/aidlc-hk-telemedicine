# User Management Service

Handles user registration, authentication, profile management, and session management.

## Features
- Patient and doctor registration
- User authentication and sessions
- Profile management
- Medical specialty management
- Doctor availability tracking

## Architecture
- FastAPI backend
- DynamoDB database
- AWS Lambda deployment
- API Gateway integration

## Deployment
```bash
cd infrastructure
cdk deploy UserManagementServiceStack
```

## Local Development
```bash
cd src
python -m uvicorn api.main:app --reload --port 8000
```

## API Documentation
- Health Check: `/health`
- Registration: `/registration/*`
- Profiles: `/profiles/*`
- Sessions: `/sessions/*`
- Specialties: `/specialties/*`
- Availability: `/availability/*`
