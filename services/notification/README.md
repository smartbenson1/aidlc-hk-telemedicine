# Notification Service

Email, SMS, and push notification system for the platform.

## Features
- Email notifications (appointment confirmations, reminders)
- SMS alerts (future implementation)
- Push notifications (future implementation)
- Template management
- Delivery status tracking
- Notification queuing

## Architecture
- Python backend
- AWS SES for email delivery
- DynamoDB for notification tracking
- Queue-based processing

## Deployment
```bash
cd infrastructure
# CDK infrastructure to be implemented
```

## Local Development
```bash
cd src
python examples/basic_usage.py
```

## Components
- **Models**: Notification data structures
- **Repositories**: Data access layer
- **Utils**: Validation and helper functions
- **Exceptions**: Custom exception handling
- **Enums**: Notification types and statuses
