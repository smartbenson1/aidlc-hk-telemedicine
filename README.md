# HealMatch Easy - Medical Appointment Matching Platform

A comprehensive healthcare platform that connects patients with doctors through intelligent symptom analysis and appointment matching.

## 🏗️ Domain-Driven Architecture

```
healmatch-easy/
├── services/
│   ├── user-management/          # User registration & authentication
│   ├── appointment-matching/     # Appointment scheduling & matching
│   ├── notification/            # Email & SMS notifications
│   └── administration/          # Admin dashboard & analytics
├── frontend/                    # React/TypeScript web application
├── shared/                      # Shared libraries and utilities
├── docs/                        # Project-wide documentation
└── scripts/                     # Deployment and utility scripts
```

## 🚀 Services Overview

### [User Management Service](services/user-management/)
- Patient and doctor registration
- Authentication and session management
- Profile management and medical specialties
- **Tech**: FastAPI, DynamoDB, AWS Lambda

### [Appointment Matching Service](services/appointment-matching/)
- Intelligent symptom analysis
- Doctor recommendation engine
- Appointment scheduling logic
- **Tech**: Python, AWS Lambda, DynamoDB

### [Notification Service](services/notification/)
- Email notifications and reminders
- SMS alerts (future)
- Template management and delivery tracking
- **Tech**: Python, AWS SES, DynamoDB

### [Administration Service](services/administration/)
- Admin dashboard and user management
- System metrics and analytics
- Platform monitoring and configuration
- **Tech**: Python, Admin interface

### [Frontend Application](frontend/)
- Modern React application with TypeScript
- Patient and doctor interfaces
- Appointment booking and management
- **Tech**: React, TypeScript, Vite, Tailwind CSS

## 🛠️ Technology Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend**: Python, FastAPI, AWS Lambda
- **Database**: AWS DynamoDB
- **Infrastructure**: AWS CDK, CloudFormation
- **Deployment**: AWS (Lambda, API Gateway, S3, CloudFront)

## 📖 Quick Start

### Deploy a Service
```bash
# Choose any service
cd services/user-management/infrastructure
pip install -r requirements.txt
cdk deploy

# Or appointment matching
cd services/appointment-matching/infrastructure  
pip install -r requirements.txt
cdk deploy
```

### Run Frontend
```bash
cd frontend
npm install
npm run dev
```

### Local Development
```bash
# Each service can run independently
cd services/user-management/src
python -m uvicorn api.main:app --reload --port 8000
```

## 📚 Documentation

- **Project Documentation**: [docs/](docs/)
- **Service Documentation**: Each service has its own README and docs
- **API Documentation**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

## 🏛️ Architecture Principles

- **Domain-Driven Design**: Each service owns its domain
- **Microservices**: Independent deployment and scaling
- **Event-Driven**: Loose coupling between services
- **Infrastructure as Code**: CDK for all infrastructure
- **API-First**: RESTful APIs with OpenAPI specs

## 🔧 Development

Each service is self-contained with:
- **Source Code**: `src/` directory
- **Infrastructure**: `infrastructure/` directory with CDK
- **Documentation**: Service-specific README and docs
- **Tests**: `tests/` directory (where applicable)

## 📄 License

This project is proprietary software for HealMatch Easy platform.
