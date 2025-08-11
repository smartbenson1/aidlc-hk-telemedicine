# CDK Deployment Guide for Administration Service API

## Prerequisites

### 1. AWS CLI Configuration
Ensure AWS CLI is installed and configured with appropriate credentials:

```bash
# Check if AWS CLI is installed
aws --version

# Configure AWS credentials (if not already done)
aws configure

# Verify credentials
aws sts get-caller-identity
```

### 2. Python Environment
Ensure you have Python 3.8+ installed:

```bash
# Check Python version
python3 --version

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
Install required Python packages:

```bash
# Install CDK dependencies
pip install aws-cdk-lib constructs

# Install application dependencies
pip install -r requirements.txt
```

### 4. Install AWS CDK CLI
Install the AWS CDK CLI globally:

```bash
# Install CDK CLI
npm install -g aws-cdk

# Verify installation
cdk --version
```

## Deployment Steps

### Step 1: Bootstrap CDK (First Time Only)
If this is your first time using CDK in this AWS account/region:

```bash
# Bootstrap CDK in your account/region
cdk bootstrap

# This creates necessary S3 buckets and IAM roles for CDK deployments
```

### Step 2: Synthesize CloudFormation Template
Generate the CloudFormation template to verify everything is correct:

```bash
# Synthesize the stack
cdk synth

# This will show you the CloudFormation template that will be deployed
```

### Step 3: Deploy the Stack
Deploy the infrastructure:

```bash
# Deploy the stack
cdk deploy

# You'll be prompted to confirm the deployment
# Type 'y' to proceed
```

### Step 4: Verify Deployment
After successful deployment, you should see outputs including:
- API Gateway URL
- Lambda Function ARN
- DynamoDB table names

## Expected Deployment Output

```
✅  AdministrationServiceStack

Outputs:
AdministrationServiceStack.APIGatewayURL = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
AdministrationServiceStack.APIGatewayId = xxxxxxxxxx
AdministrationServiceStack.LambdaFunctionArn = arn:aws:lambda:us-east-1:xxxxxxxxxxxx:function:administration-service-api

Stack ARN:
arn:aws:cloudformation:us-east-1:xxxxxxxxxxxx:stack/AdministrationServiceStack/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## Post-Deployment Testing

### 1. Test Health Endpoint
```bash
# Replace with your actual API Gateway URL
curl https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "dynamodb": "connected"
  }
}
```

### 2. Initialize Sample Data
```bash
# Initialize sample data
curl -X POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/api/v1/admin/init-data
```

### 3. Test API Endpoints
```bash
# Get all doctors
curl https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/api/v1/doctors

# Get all specialties
curl https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/api/v1/specialties

# Get user analytics
curl https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/api/v1/analytics/users
```

## Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Required
**Error**: `Need to perform AWS CDK bootstrap`
**Solution**: Run `cdk bootstrap`

#### 2. Insufficient Permissions
**Error**: `User: arn:aws:iam::xxx:user/xxx is not authorized to perform: xxx`
**Solution**: Ensure your AWS user has sufficient permissions for:
- CloudFormation
- Lambda
- API Gateway
- DynamoDB
- IAM
- CloudWatch
- SSM

#### 3. Region Mismatch
**Error**: Stack deployed in wrong region
**Solution**: Set AWS region explicitly:
```bash
export AWS_DEFAULT_REGION=us-east-1
cdk deploy
```

#### 4. Lambda Package Too Large
**Error**: `Unzipped size must be smaller than xxx bytes`
**Solution**: The CDK automatically handles packaging, but if issues occur:
- Remove unnecessary files from the directory
- Check `.gitignore` patterns

### Debugging Commands

```bash
# Check CDK context
cdk context

# List all stacks
cdk list

# Show differences before deployment
cdk diff

# View stack events
aws cloudformation describe-stack-events --stack-name AdministrationServiceStack

# Check Lambda function logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/administration-service"
```

## Stack Resources Created

The CDK deployment creates the following AWS resources:

### DynamoDB Tables
- `admin-users` - Admin user data
- `doctors` - Doctor information
- `patients` - Patient information  
- `medical-specialties` - Medical specialties
- `audit-logs` - Audit trail
- `reports` - Generated reports
- `system-metrics` - System metrics

### Lambda Function
- `administration-service-api` - Main API handler
- Runtime: Python 3.11
- Memory: 512 MB
- Timeout: 30 seconds

### API Gateway
- REST API with structured resources
- CORS enabled
- Throttling: 100 req/sec, 200 burst
- Access logging enabled

### IAM Roles
- Lambda execution role with minimal permissions
- DynamoDB read/write access
- CloudWatch logging permissions

### CloudWatch
- Log groups for Lambda and API Gateway
- Basic alarms for errors and duration

## Cost Estimation

### Monthly Costs (Approximate)
- **DynamoDB**: $0-5 (pay per request, depends on usage)
- **Lambda**: $0-10 (first 1M requests free)
- **API Gateway**: $3.50 per million requests
- **CloudWatch**: $0-5 (basic logging)

**Total estimated monthly cost**: $5-25 (for moderate usage)

## Cleanup

To remove all resources and avoid charges:

```bash
# Delete the stack
cdk destroy

# Confirm deletion when prompted
```

**Note**: This will delete all data in DynamoDB tables. Make sure to backup any important data first.

## Next Steps

After successful deployment:

1. **Update API Documentation**: The API is available at `/docs` endpoint
2. **Set up Monitoring**: Configure CloudWatch dashboards
3. **Configure Custom Domain**: If needed, set up custom domain
4. **Add Authentication**: When ready, uncomment Cognito configuration
5. **Set up CI/CD**: Implement automated deployments

## Support

If you encounter issues:
1. Check CloudWatch logs for Lambda function
2. Review API Gateway execution logs
3. Verify DynamoDB table creation
4. Check IAM permissions

The API will be accessible immediately after deployment and ready for testing!