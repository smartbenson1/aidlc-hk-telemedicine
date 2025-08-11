# Appointment Matching Service - AWS Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the Appointment Matching Service to AWS using serverless architecture with Lambda, API Gateway, and DynamoDB.

## Architecture
- **Compute**: AWS Lambda (Python 3.9)
- **API**: API Gateway REST API
- **Database**: DynamoDB with GSIs
- **Monitoring**: CloudWatch Logs and Metrics
- **Infrastructure**: AWS CDK for Infrastructure as Code

## Prerequisites

### Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install AWS CDK
npm install -g aws-cdk

# Install Python dependencies
pip install aws-cdk-lib boto3 constructs
```

### AWS Configuration
```bash
# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format

# Verify configuration
aws sts get-caller-identity
```

## Deployment Steps

### Step 1: Prepare the Lambda Package
```bash
# Navigate to the Lambda package directory
cd appointment_matching_service_lambda

# Copy the service code
cp -r ../appointment_matching_service ./

# Install dependencies (if any additional ones needed)
pip install -r requirements.txt -t .

# Create deployment package
zip -r appointment_matching_service.zip . -x "*.pyc" "__pycache__/*" "tests/*"
```

### Step 2: Deploy Infrastructure
```bash
# Navigate to infrastructure directory
cd ../appointment_matching_service_infrastructure

# Install CDK dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy AppointmentMatchingStack

# Note the API Gateway URL from the output
```

### Step 3: Verify Deployment
```bash
# Test the health endpoint
curl https://YOUR_API_GATEWAY_URL/prod/health

# Expected response:
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "appointment-matching-service",
    "timestamp": "2023-12-01T10:00:00Z",
    "version": "1.0.0"
  },
  "timestamp": "2023-12-01T10:00:00Z"
}
```

## API Usage Examples

### 1. Describe Symptoms (US-P003)
```bash
curl -X POST https://YOUR_API_GATEWAY_URL/prod/symptoms \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-123",
    "symptoms_text": "I have chest pain and shortness of breath"
  }'
```

### 2. Get Doctor Recommendations (US-P004)
```bash
curl -X POST https://YOUR_API_GATEWAY_URL/prod/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "symptom_description_id": "symptom-456"
  }'
```

### 3. Book Appointment (US-P006)
```bash
curl -X POST https://YOUR_API_GATEWAY_URL/prod/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-123",
    "doctor_id": "doctor-789",
    "appointment_datetime": "2023-12-15T14:00:00Z",
    "symptoms": "Chest pain and shortness of breath",
    "appointment_type": "in_person"
  }'
```

### 4. Get Patient Appointments (US-P007)
```bash
curl https://YOUR_API_GATEWAY_URL/prod/patients/patient-123/appointments
```

### 5. Reschedule Appointment (US-P008)
```bash
curl -X POST https://YOUR_API_GATEWAY_URL/prod/appointments/appointment-456/reschedule \
  -H "Content-Type: application/json" \
  -d '{
    "new_datetime": "2023-12-16T14:00:00Z",
    "reason": "Schedule conflict"
  }'
```

### 6. Get Doctor Appointments (US-D005)
```bash
curl https://YOUR_API_GATEWAY_URL/prod/doctors/doctor-789/appointments
```

## Client SDK Examples

### Python Client
```python
import requests
import json
from datetime import datetime, timedelta

class AppointmentMatchingClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def describe_symptoms(self, patient_id, symptoms_text):
        """Describe symptoms for analysis"""
        response = requests.post(
            f"{self.base_url}/symptoms",
            json={
                "patient_id": patient_id,
                "symptoms_text": symptoms_text
            }
        )
        return response.json()
    
    def get_recommendations(self, symptom_description_id):
        """Get doctor recommendations"""
        response = requests.post(
            f"{self.base_url}/recommendations",
            json={
                "symptom_description_id": symptom_description_id
            }
        )
        return response.json()
    
    def book_appointment(self, patient_id, doctor_id, appointment_datetime, symptoms):
        """Book an appointment"""
        response = requests.post(
            f"{self.base_url}/appointments",
            json={
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "appointment_datetime": appointment_datetime,
                "symptoms": symptoms
            }
        )
        return response.json()

# Usage example
client = AppointmentMatchingClient("https://YOUR_API_GATEWAY_URL/prod")

# Describe symptoms
symptoms = client.describe_symptoms(
    "patient-123", 
    "I have chest pain and shortness of breath"
)

# Get recommendations
recommendations = client.get_recommendations(symptoms['data']['id'])

# Book appointment
appointment = client.book_appointment(
    "patient-123",
    recommendations['data']['recommended_doctors'][0],
    (datetime.now() + timedelta(days=1)).isoformat(),
    "Chest pain and shortness of breath"
)
```

### JavaScript Client
```javascript
class AppointmentMatchingClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }

    async describeSymptoms(patientId, symptomsText) {
        const response = await fetch(`${this.baseUrl}/symptoms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                patient_id: patientId,
                symptoms_text: symptomsText
            })
        });
        return response.json();
    }

    async getRecommendations(symptomDescriptionId) {
        const response = await fetch(`${this.baseUrl}/recommendations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symptom_description_id: symptomDescriptionId
            })
        });
        return response.json();
    }

    async bookAppointment(patientId, doctorId, appointmentDatetime, symptoms) {
        const response = await fetch(`${this.baseUrl}/appointments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                patient_id: patientId,
                doctor_id: doctorId,
                appointment_datetime: appointmentDatetime,
                symptoms: symptoms
            })
        });
        return response.json();
    }
}

// Usage example
const client = new AppointmentMatchingClient('https://YOUR_API_GATEWAY_URL/prod');

// Describe symptoms
const symptoms = await client.describeSymptoms(
    'patient-123',
    'I have chest pain and shortness of breath'
);

// Get recommendations
const recommendations = await client.getRecommendations(symptoms.data.id);

// Book appointment
const appointment = await client.bookAppointment(
    'patient-123',
    recommendations.data.recommended_doctors[0],
    new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    'Chest pain and shortness of breath'
);
```

## Monitoring and Logging

### CloudWatch Logs
- Lambda logs: `/aws/lambda/appointment-matching-service`
- API Gateway logs: `/aws/apigateway/appointment-matching-service`

### CloudWatch Metrics
- Lambda: Duration, Errors, Invocations
- API Gateway: Count, Latency, 4XXError, 5XXError
- DynamoDB: ConsumedReadCapacityUnits, ConsumedWriteCapacityUnits

### Viewing Logs
```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/appointment-matching"

# Tail logs in real-time
aws logs tail /aws/lambda/appointment-matching-service --follow
```

## Cost Optimization

### Current Configuration
- **Lambda**: Pay per invocation (100 RPS = ~$10-20/month)
- **API Gateway**: Pay per request (~$3.50 per million requests)
- **DynamoDB**: Pay per request (On-demand pricing)
- **CloudWatch**: Basic monitoring included

### Cost Monitoring
```bash
# Set up billing alerts
aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget '{
  "BudgetName": "AppointmentMatchingService",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}'
```

## Troubleshooting

### Common Issues

1. **Lambda Timeout**
   - Increase timeout in CDK stack (currently 30 seconds)
   - Optimize database queries

2. **DynamoDB Throttling**
   - Check CloudWatch metrics
   - Consider switching to provisioned capacity if needed

3. **API Gateway 429 Errors**
   - Current limit: 100 RPS
   - Increase throttling limits in CDK stack if needed

4. **Cold Start Issues**
   - Lambda cold starts ~1-2 seconds
   - Consider provisioned concurrency for critical endpoints

### Debug Commands
```bash
# Check Lambda function
aws lambda get-function --function-name appointment-matching-service

# Check API Gateway
aws apigateway get-rest-apis

# Check DynamoDB tables
aws dynamodb list-tables
aws dynamodb describe-table --table-name appointment-matching-doctors
```

## Security Considerations

### Current Security
- HTTPS encryption in transit
- DynamoDB encryption at rest
- IAM roles with least privilege
- API Gateway throttling

### Future Enhancements
- Add authentication (AWS Cognito)
- Implement WAF rules
- Add request signing
- Enable VPC endpoints

## Cleanup

### Remove All Resources
```bash
# Delete CDK stack
cd appointment_matching_service_infrastructure
cdk destroy AppointmentMatchingStack

# Confirm deletion
# This will remove all AWS resources created by the stack
```

## Support

For issues or questions:
1. Check CloudWatch logs for error details
2. Review API documentation in `api_documentation.yaml`
3. Contact the development team

## Next Steps

1. **Add Authentication**: Implement AWS Cognito for user management
2. **Add Caching**: Implement ElastiCache for frequently accessed data
3. **Add Monitoring**: Set up custom dashboards and alerts
4. **Add Testing**: Implement automated testing pipeline
5. **Add Analytics**: Implement data analytics for appointment patterns