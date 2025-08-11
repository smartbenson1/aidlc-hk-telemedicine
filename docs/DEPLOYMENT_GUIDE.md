# HealMatch Easy - Deployment Guide

This guide covers the modern CDK-based deployment approach for all services.

## 🏗️ Architecture Overview

The platform uses AWS CDK (Cloud Development Kit) for infrastructure as code:

- **User Management Service**: `infrastructure/` directory
- **Appointment Matching Service**: `appointment_matching_service_infrastructure/` directory  
- **Frontend**: React app (can be deployed to S3/CloudFront)
- **Other Services**: Will have their own CDK infrastructure

## 📋 Prerequisites

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **AWS CDK** installed globally
   ```bash
   npm install -g aws-cdk
   ```

3. **Python 3.8+** with pip
   ```bash
   python3 --version
   pip3 --version
   ```

4. **Node.js 14+** (for CDK)
   ```bash
   node --version
   npm --version
   ```

## 🚀 Service Deployment

### User Management Service

```bash
# Navigate to infrastructure directory
cd infrastructure

# Install Python dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy UserManagementServiceStack
```

### Appointment Matching Service

```bash
# Navigate to service infrastructure directory
cd appointment_matching_service_infrastructure

# Install Python dependencies  
pip install -r requirements.txt

# Bootstrap CDK (if not done already)
cdk bootstrap

# Deploy the stack
cdk deploy AppointmentMatchingStack
```

### Frontend Application

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Deploy to S3/CloudFront (manual or via CDK)
# See frontend deployment documentation
```

## 🔧 Development Workflow

### Local Development

1. **Start Backend Services Locally**:
   ```bash
   # User Management Service
   cd user_management_service
   python -m uvicorn api.main:app --reload --port 8000
   
   # Appointment Matching Service  
   cd appointment_matching_service
   python main.py
   ```

2. **Start Frontend Locally**:
   ```bash
   cd frontend
   npm run dev
   ```

### Testing Deployment

After deployment, test your services:

```bash
# Get API Gateway URLs from CDK outputs
cdk list
aws cloudformation describe-stacks --stack-name UserManagementServiceStack

# Test health endpoints
curl https://your-api-url/health
```

## 📊 Monitoring & Logs

- **CloudWatch Logs**: Automatic logging for Lambda functions
- **CloudWatch Metrics**: API Gateway and Lambda metrics
- **X-Ray Tracing**: Distributed tracing (if enabled)

## 🔄 Updates & Rollbacks

### Updating Services

```bash
# Make code changes, then redeploy
cd infrastructure
cdk deploy UserManagementServiceStack

# Or deploy with approval
cdk deploy --require-approval never
```

### Rolling Back

```bash
# Rollback to previous version
cdk deploy --rollback

# Or destroy and redeploy
cdk destroy UserManagementServiceStack
cdk deploy UserManagementServiceStack
```

## 🛡️ Security Best Practices

1. **IAM Roles**: CDK creates least-privilege IAM roles
2. **API Gateway**: Built-in throttling and authentication
3. **VPC**: Services can be deployed in VPC for isolation
4. **Secrets**: Use AWS Secrets Manager for sensitive data

## 💰 Cost Optimization

- **Lambda**: Pay per request, automatic scaling
- **DynamoDB**: On-demand billing or provisioned capacity
- **API Gateway**: Pay per API call
- **CloudWatch**: Monitor costs in AWS Cost Explorer

## 🆘 Troubleshooting

### Common Issues

1. **CDK Bootstrap Failed**:
   ```bash
   cdk bootstrap --force
   ```

2. **Deployment Timeout**:
   ```bash
   cdk deploy --timeout 30
   ```

3. **Permission Errors**:
   - Check AWS credentials
   - Verify IAM permissions
   - Ensure CDK bootstrap was successful

4. **Stack Already Exists**:
   ```bash
   cdk destroy StackName
   cdk deploy StackName
   ```

### Getting Help

- Check CloudFormation events in AWS Console
- Review CloudWatch logs for Lambda functions
- Use `cdk diff` to see what will change before deployment

## 📚 Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)

---

This modern CDK approach provides:
- ✅ Infrastructure as Code
- ✅ Version Control for Infrastructure  
- ✅ Automated Rollbacks
- ✅ Consistent Deployments
- ✅ Easy Environment Management