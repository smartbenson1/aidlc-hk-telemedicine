# User Management Service Deployment Guide

This guide provides comprehensive instructions for deploying the User Management Service API to AWS using serverless architecture.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Pre-Deployment Setup](#pre-deployment-setup)
4. [Deployment Process](#deployment-process)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Testing and Validation](#testing-and-validation)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- **AWS CLI** (v2.0 or later)
- **AWS CDK** (v2.0 or later)
- **Python** (3.11 or later)
- **Node.js** (16.x or later) - for CDK
- **Git** - for version control

### AWS Account Requirements
- AWS account with appropriate permissions
- AWS CLI configured with credentials
- Sufficient service limits for:
  - Lambda functions
  - API Gateway
  - DynamoDB tables
  - CloudWatch logs

### Installation Commands
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install AWS CDK
npm install -g aws-cdk

# Verify installations
aws --version
cdk --version
python3 --version
```

## Architecture Overview

The User Management Service uses a serverless architecture with the following components:

```
Internet → API Gateway → Lambda → DynamoDB
              ↓            ↓
         CloudWatch ← X-Ray Tracing
              ↓
         Secrets Manager
```

### AWS Services Used
- **API Gateway**: REST API endpoints with CORS and throttling
- **Lambda**: Serverless compute with FastAPI via Mangum
- **DynamoDB**: NoSQL database with GSIs for efficient queries
- **CloudWatch**: Monitoring, logging, and alerting
- **X-Ray**: Distributed tracing and performance analysis
- **Secrets Manager**: Secure storage of JWT secrets
- **Parameter Store**: Configuration management
- **IAM**: Security roles and policies

## Pre-Deployment Setup

### 1. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

### 2. Clone and Setup Project
```bash
git clone <repository-url>
cd user-management-service
```

### 3. Install Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file with the following variables:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_EXPIRATION_HOURS=24
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# Database Configuration
DYNAMODB_ENDPOINT=https://dynamodb.us-east-1.amazonaws.com
```

## Deployment Process

### Option 1: Automated Deployment (Recommended)
```bash
# Make deployment script executable
chmod +x deploy.py

# Run automated deployment
python3 deploy.py --environment production --region us-east-1
```

### Option 2: Manual Deployment Steps

#### Step 1: Bootstrap CDK
```bash
cd infrastructure
cdk bootstrap aws://ACCOUNT-ID/REGION
```

#### Step 2: Prepare Lambda Layer
```bash
# Create Lambda layer directory
mkdir -p lambda_layer/python

# Install dependencies for Lambda layer
pip install -r lambda_layer/requirements.txt -t lambda_layer/python/
```

#### Step 3: Deploy Infrastructure
```bash
cd infrastructure
cdk deploy --require-approval never
```

#### Step 4: Verify Deployment
```bash
# Get stack outputs
aws cloudformation describe-stacks --stack-name UserManagementServiceStack --query 'Stacks[0].Outputs'
```

## Post-Deployment Configuration

### 1. Update JWT Secret
```bash
# Generate a secure JWT secret
aws secretsmanager update-secret \
  --secret-id user-management/jwt-secret \
  --secret-string '{"jwt_secret_key":"your-secure-random-key"}'
```

### 2. Configure Parameters
```bash
# Update configuration parameters
aws ssm put-parameter \
  --name "/user-management/config/log-level" \
  --value "INFO" \
  --type "String" \
  --overwrite

aws ssm put-parameter \
  --name "/user-management/config/jwt-expiration-hours" \
  --value "24" \
  --type "String" \
  --overwrite
```

### 3. Seed Database (Optional)
```bash
# Run database seeding script
python3 -c "
from user_management_service.main import UserManagementServiceDemo
service = UserManagementServiceDemo()
service.setup_sample_data()
print('Database seeded successfully')
"
```

## Testing and Validation

### 1. Health Check
```bash
# Get API Gateway URL from stack outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name UserManagementServiceStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

# Test health endpoint
curl "${API_URL}health"
```

### 2. API Documentation
Access the interactive API documentation at:
- Swagger UI: `${API_URL}docs`
- ReDoc: `${API_URL}redoc`

### 3. Sample API Calls
```bash
# Register a doctor
curl -X POST "${API_URL}api/doctors/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. John Smith",
    "email": "john.smith@example.com",
    "phone": "+1234567890",
    "location": "New York, NY",
    "specialties": ["cardiology"],
    "experience": "10 years of experience in cardiology"
  }'

# Check email availability
curl "${API_URL}api/doctors/email-availability?email=test@example.com"

# Get specialties
curl "${API_URL}api/specialties"
```

### 4. Load Testing
```bash
# Install Apache Bench for load testing
sudo apt-get install apache2-utils

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 "${API_URL}health"
```

## Monitoring and Maintenance

### 1. CloudWatch Dashboard
Access the monitoring dashboard:
```bash
# Get dashboard URL from stack outputs
DASHBOARD_URL=$(aws cloudformation describe-stacks \
  --stack-name UserManagementServiceStack \
  --query 'Stacks[0].Outputs[?OutputKey==`DashboardUrl`].OutputValue' \
  --output text)

echo "Dashboard URL: $DASHBOARD_URL"
```

### 2. Log Analysis
```bash
# View Lambda function logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/UserManagementServiceStack"

# Tail logs in real-time
aws logs tail /aws/lambda/UserManagementServiceStack-UserManagementFunction --follow
```

### 3. Performance Monitoring
- **Lambda Metrics**: Duration, errors, throttles
- **API Gateway Metrics**: Request count, latency, 4xx/5xx errors
- **DynamoDB Metrics**: Read/write capacity, throttling

### 4. Alerts and Notifications
The deployment includes CloudWatch alarms for:
- Lambda function error rate > 5%
- API Gateway 5xx error count > 10
- DynamoDB throttling events

## Troubleshooting

### Common Issues

#### 1. Deployment Failures
```bash
# Check CDK deployment logs
cdk deploy --verbose

# Validate CDK template
cdk synth

# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name UserManagementServiceStack
```

#### 2. Lambda Function Errors
```bash
# Check function configuration
aws lambda get-function --function-name UserManagementServiceStack-UserManagementFunction

# View recent errors
aws logs filter-log-events \
  --log-group-name "/aws/lambda/UserManagementServiceStack-UserManagementFunction" \
  --filter-pattern "ERROR"
```

#### 3. API Gateway Issues
```bash
# Test API Gateway directly
aws apigateway test-invoke-method \
  --rest-api-id YOUR_API_ID \
  --resource-id YOUR_RESOURCE_ID \
  --http-method GET
```

#### 4. DynamoDB Issues
```bash
# Check table status
aws dynamodb describe-table --table-name user-management-users

# Verify table data
aws dynamodb scan --table-name user-management-users --limit 5
```

### Performance Optimization

#### 1. Lambda Cold Starts
- Use provisioned concurrency for consistent performance
- Optimize package size and dependencies
- Implement connection pooling

#### 2. DynamoDB Performance
- Monitor read/write capacity utilization
- Use appropriate GSI design
- Implement caching where appropriate

#### 3. API Gateway Optimization
- Enable caching for read-heavy endpoints
- Configure appropriate throttling limits
- Use compression for large responses

### Security Best Practices

#### 1. Regular Security Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Scan for vulnerabilities
pip-audit

# Update CDK and AWS CLI
npm update -g aws-cdk
aws --version
```

#### 2. Access Control
- Regularly review IAM policies
- Use least privilege principle
- Enable CloudTrail for audit logging

#### 3. Data Protection
- Ensure encryption at rest and in transit
- Regularly rotate secrets
- Monitor for suspicious activity

## Rollback Procedures

### 1. Application Rollback
```bash
# Rollback to previous version
cdk deploy --rollback

# Or deploy specific version
git checkout previous-version-tag
cdk deploy
```

### 2. Database Rollback
```bash
# Restore from point-in-time backup
aws dynamodb restore-table-from-backup \
  --target-table-name user-management-users-restored \
  --backup-arn arn:aws:dynamodb:region:account:table/user-management-users/backup/backup-id
```

### 3. Emergency Procedures
- Disable API Gateway stage
- Update Lambda function to return maintenance mode
- Redirect traffic using Route 53

## Cost Optimization

### 1. Monitor Costs
```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### 2. Optimization Strategies
- Use DynamoDB on-demand billing for variable workloads
- Set up Lambda reserved concurrency appropriately
- Enable API Gateway caching for read-heavy endpoints
- Use CloudWatch log retention policies

## Support and Maintenance

### 1. Regular Maintenance Tasks
- Review and update dependencies monthly
- Monitor performance metrics weekly
- Review security logs daily
- Update documentation as needed

### 2. Backup and Recovery
- DynamoDB point-in-time recovery is enabled
- Lambda function code is version controlled
- Infrastructure is defined as code (CDK)

### 3. Disaster Recovery
- Multi-AZ deployment for high availability
- Automated backups and recovery procedures
- Documented incident response procedures

## Additional Resources

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

For additional support, please refer to the project documentation or contact the development team.