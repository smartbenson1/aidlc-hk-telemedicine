# Administration Service API

A serverless REST API for the Doctor Appointment Platform's administration functions, built with FastAPI and deployed on AWS using serverless architecture.

## 🏗️ Architecture

### AWS Services Used
- **AWS Lambda**: Serverless compute for API logic
- **API Gateway**: REST API endpoint management
- **DynamoDB**: NoSQL database for data persistence
- **Cognito**: User authentication and authorization
- **CloudWatch**: Monitoring and logging
- **Systems Manager**: Configuration management
- **AWS CDK**: Infrastructure as Code

### Architecture Principles
- **Serverless**: Cost-effective, auto-scaling compute
- **Security**: JWT authentication, encrypted data
- **Monitoring**: CloudWatch alarms and logging
- **Operational Excellence**: Infrastructure as Code

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.11+
- Node.js (for AWS CDK)
- Git

### Deployment

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd administration-service-api
   ```

2. **Deploy to AWS**:
   ```bash
   ./deploy.sh
   ```

3. **Initialize sample data**:
   ```bash
   curl -X POST https://your-api-url/api/v1/admin/init-data
   ```

## 📚 API Documentation

### Base URL
```
https://your-api-gateway-url/
```

### Authentication
All endpoints require JWT authentication via AWS Cognito:
```bash
Authorization: Bearer <jwt-token>
```

### Core Endpoints

#### Doctor Management (US-A001)
- `GET /api/v1/doctors` - Get all doctors
- `GET /api/v1/doctors/{id}` - Get doctor with statistics
- `PUT /api/v1/doctors/{id}/status` - Update doctor status

#### Patient Management (US-A002)
- `GET /api/v1/patients` - Get all patients (excluding sensitive data)
- `GET /api/v1/patients/{id}` - Get patient with statistics
- `PUT /api/v1/patients/{id}/status` - Update patient status

#### Medical Specialty Management (US-A003)
- `GET /api/v1/specialties` - Get all medical specialties
- `POST /api/v1/specialties` - Create new specialty
- `PUT /api/v1/specialties/{id}` - Update specialty
- `PUT /api/v1/specialties/{id}/status` - Update specialty status

#### Analytics (US-A004)
- `GET /api/v1/analytics/users` - Get user analytics
- `GET /api/v1/analytics/appointments` - Get appointment statistics
- `GET /api/v1/analytics/specialties` - Get specialty usage stats

#### Reports (US-A005)
- `GET /api/v1/reports` - Get all reports
- `POST /api/v1/reports` - Generate new report
- `GET /api/v1/reports/{id}` - Get specific report

### Interactive Documentation
- **Swagger UI**: `https://your-api-url/docs`
- **ReDoc**: `https://your-api-url/redoc`

## 🔐 Authentication Setup

### Create Admin User
```python
import boto3

cognito = boto3.client('cognito-idp', region_name='us-east-1')

# Create user
cognito.admin_create_user(
    UserPoolId='your-user-pool-id',
    Username='admin',
    UserAttributes=[
        {'Name': 'email', 'Value': 'admin@hospital.com'},
        {'Name': 'email_verified', 'Value': 'true'}
    ],
    TemporaryPassword='TempPass123!',
    MessageAction='SUPPRESS'
)

# Set permanent password
cognito.admin_set_user_password(
    UserPoolId='your-user-pool-id',
    Username='admin',
    Password='AdminPass123!',
    Permanent=True
)

# Add to admin group
cognito.admin_add_user_to_group(
    UserPoolId='your-user-pool-id',
    Username='admin',
    GroupName='admin'
)
```

### Get JWT Token
```bash
aws cognito-idp admin-initiate-auth \
  --user-pool-id your-user-pool-id \
  --client-id your-client-id \
  --auth-flow ADMIN_NO_SRP_AUTH \
  --auth-parameters USERNAME=admin,PASSWORD=AdminPass123!
```

## 🧪 Testing

### Health Check
```bash
curl https://your-api-url/health
```

### Example API Calls

#### Get All Doctors
```bash
curl -H "Authorization: Bearer <jwt-token>" \
     https://your-api-url/api/v1/doctors
```

#### Create Medical Specialty
```bash
curl -X POST \
     -H "Authorization: Bearer <jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Neurology", "description": "Brain and nervous system"}' \
     https://your-api-url/api/v1/specialties
```

#### Generate Report
```bash
curl -X POST \
     -H "Authorization: Bearer <jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "report_name": "Daily Operations",
       "report_type": "operational",
       "report_template": "daily_ops",
       "date_range_start": "2024-01-01T00:00:00Z",
       "date_range_end": "2024-01-02T00:00:00Z",
       "export_format": "PDF"
     }' \
     https://your-api-url/api/v1/reports
```

## 📊 Monitoring

### CloudWatch Dashboards
- Lambda function metrics (duration, errors, invocations)
- API Gateway metrics (latency, 4XX/5XX errors)
- DynamoDB metrics (read/write capacity, throttles)

### Alarms
- Lambda error rate > 5 errors in 10 minutes
- Lambda duration > 25 seconds
- API Gateway 4XX error rate > 10 in 10 minutes
- API Gateway 5XX error rate > 5 in 10 minutes

### Logs
- Lambda function logs: `/aws/lambda/administration-service-api`
- API Gateway logs: Available in CloudWatch

## 🔧 Configuration

### Environment Variables
- `DYNAMODB_REGION`: AWS region for DynamoDB
- `COGNITO_REGION`: AWS region for Cognito
- `COGNITO_USER_POOL_ID`: Cognito User Pool ID
- `COGNITO_CLIENT_ID`: Cognito Client ID
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

### Systems Manager Parameters
- `/administration-service/cognito/user-pool-id`
- `/administration-service/cognito/client-id`
- `/administration-service/api/url`

## 🛠️ Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally with uvicorn
uvicorn main:app --reload --port 8000

# Access local API
open http://localhost:8000/docs
```

### Code Structure
```
├── main.py                    # FastAPI application
├── api_models.py             # Pydantic models
├── auth_middleware.py        # Authentication logic
├── error_handlers.py         # Error handling
├── dynamodb_repositories.py  # Data access layer
├── cdk_app.py               # AWS CDK infrastructure
├── deploy.sh                # Deployment script
└── requirements.txt         # Python dependencies
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Error: Invalid authentication credentials
```
**Solution**: Ensure JWT token is valid and user has proper permissions.

#### 2. DynamoDB Access Denied
```
Error: User is not authorized to perform: dynamodb:GetItem
```
**Solution**: Check Lambda execution role has DynamoDB permissions.

#### 3. Lambda Timeout
```
Error: Task timed out after 30.00 seconds
```
**Solution**: Increase Lambda timeout or optimize query performance.

### Debug Commands
```bash
# Check Lambda logs
aws logs tail /aws/lambda/administration-service-api --follow

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix API-Gateway-Execution-Logs

# Test Lambda function directly
aws lambda invoke --function-name administration-service-api response.json
```

## 🔒 Security

### Best Practices Implemented
- JWT authentication with AWS Cognito
- Role-based access control (RBAC)
- Data encryption at rest and in transit
- API rate limiting and throttling
- Comprehensive audit logging
- Least privilege IAM policies

### Security Checklist
- [ ] Cognito User Pool configured with strong password policy
- [ ] API Gateway has authentication enabled
- [ ] DynamoDB tables encrypted
- [ ] Lambda function has minimal IAM permissions
- [ ] CloudTrail enabled for audit logging
- [ ] VPC endpoints configured (if using VPC)

## 📈 Performance

### Optimization Features
- DynamoDB on-demand billing for cost optimization
- Lambda function optimized for cold starts
- API Gateway caching (can be enabled)
- Efficient data serialization/deserialization

### Performance Targets
- API response time: < 2 seconds (95th percentile)
- Lambda cold start: < 3 seconds
- Concurrent requests: 100 requests/second
- Availability: 99.9% uptime

## 🔄 Maintenance

### Regular Tasks
- Monitor CloudWatch alarms and metrics
- Review and rotate access keys
- Update dependencies and security patches
- Backup DynamoDB tables
- Review audit logs for suspicious activity

### Scaling Considerations
- Lambda automatically scales to handle traffic
- DynamoDB on-demand scaling handles load spikes
- API Gateway handles up to 10,000 requests/second by default
- Consider reserved capacity for predictable workloads

## 📞 Support

### Getting Help
1. Check CloudWatch logs for error details
2. Review API documentation at `/docs` endpoint
3. Verify authentication and permissions
4. Check AWS service status page
5. Contact system administrator

### Useful AWS CLI Commands
```bash
# Get stack outputs
aws cloudformation describe-stacks --stack-name AdministrationServiceStack

# Update Lambda function code
aws lambda update-function-code --function-name administration-service-api --zip-file fileb://deployment.zip

# Get Cognito user info
aws cognito-idp admin-get-user --user-pool-id <pool-id> --username <username>
```

## 📋 Production Readiness Checklist

### Pre-Deployment
- [ ] All environment variables configured
- [ ] AWS permissions properly set
- [ ] Cognito User Pool and groups created
- [ ] DynamoDB tables created with proper indexes
- [ ] CloudWatch alarms configured
- [ ] API documentation reviewed

### Post-Deployment
- [ ] Health check endpoint responding
- [ ] Sample data initialized
- [ ] Admin users created and tested
- [ ] All API endpoints tested
- [ ] Monitoring dashboards configured
- [ ] Backup and recovery procedures tested

### Ongoing Operations
- [ ] Regular security updates
- [ ] Performance monitoring
- [ ] Cost optimization reviews
- [ ] Disaster recovery testing
- [ ] Documentation updates

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Built with ❤️ using AWS Well-Architected Framework principles**