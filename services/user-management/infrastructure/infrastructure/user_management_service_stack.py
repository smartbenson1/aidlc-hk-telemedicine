#!/usr/bin/env python3
"""
AWS CDK Stack for User Management Service

This stack creates the infrastructure for the User Management Service API including:
- API Gateway for REST API endpoints
- Lambda functions for serverless compute
- DynamoDB tables for data persistence
- CloudWatch for monitoring and logging
- IAM roles and policies for security
"""

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
    CfnOutput
)
from constructs import Construct
from typing import Dict, Any


class UserManagementServiceStack(Stack):
    """CDK Stack for User Management Service infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB tables
        self.create_dynamodb_tables()
        
        # Create Lambda execution role
        self.create_lambda_role()
        
        # Create Lambda function
        self.create_lambda_function()
        
        # Create API Gateway
        self.create_api_gateway()
        
        # Create CloudWatch resources
        self.create_monitoring()
        
        # Create configuration parameters
        self.create_configuration()
        
        # Create outputs
        self.create_outputs()

    def create_dynamodb_tables(self):
        """Create DynamoDB tables for the User Management Service."""
        
        # Users table (for both doctors and patients)
        self.users_table = dynamodb.Table(
            self, "UsersTable",
            table_name="user-management-users",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # Change to RETAIN for production
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )
        
        # Add GSI for email lookups
        self.users_table.add_global_secondary_index(
            index_name="email-index",
            partition_key=dynamodb.Attribute(
                name="email",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
        
        # Add GSI for user type queries
        self.users_table.add_global_secondary_index(
            index_name="user-type-index",
            partition_key=dynamodb.Attribute(
                name="user_type",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Specialties table
        self.specialties_table = dynamodb.Table(
            self, "SpecialtiesTable",
            table_name="user-management-specialties",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            )
        )
        
        # Add GSI for name lookups
        self.specialties_table.add_global_secondary_index(
            index_name="name-index",
            partition_key=dynamodb.Attribute(
                name="name",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Availability table
        self.availability_table = dynamodb.Table(
            self, "AvailabilityTable",
            table_name="user-management-availability",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            )
        )
        
        # Add GSI for doctor queries
        self.availability_table.add_global_secondary_index(
            index_name="doctor-date-index",
            partition_key=dynamodb.Attribute(
                name="doctor_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
        
        # Add GSI for specialty queries
        self.availability_table.add_global_secondary_index(
            index_name="specialty-date-index",
            partition_key=dynamodb.Attribute(
                name="specialty_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Sessions table
        self.sessions_table = dynamodb.Table(
            self, "SessionsTable",
            table_name="user-management-sessions",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="expires_at"  # Automatic cleanup of expired sessions
        )
        
        # Add GSI for user queries
        self.sessions_table.add_global_secondary_index(
            index_name="user-index",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Events table for audit logging
        self.events_table = dynamodb.Table(
            self, "EventsTable",
            table_name="user-management-events",
            partition_key=dynamodb.Attribute(
                name="event_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for event type queries
        self.events_table.add_global_secondary_index(
            index_name="event-type-index",
            partition_key=dynamodb.Attribute(
                name="event_type",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

    def create_lambda_role(self):
        """Create IAM role for Lambda function."""
        
        self.lambda_role = iam.Role(
            self, "UserManagementLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
            ]
        )
        
        # Add DynamoDB permissions
        dynamodb_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem"
            ],
            resources=[
                self.users_table.table_arn,
                f"{self.users_table.table_arn}/index/*",
                self.specialties_table.table_arn,
                f"{self.specialties_table.table_arn}/index/*",
                self.availability_table.table_arn,
                f"{self.availability_table.table_arn}/index/*",
                self.sessions_table.table_arn,
                f"{self.sessions_table.table_arn}/index/*",
                self.events_table.table_arn,
                f"{self.events_table.table_arn}/index/*",
                # Add permission for appointment matching table for auto-sync
                "arn:aws:dynamodb:us-east-1:*:table/appointment-matching-doctors",
                "arn:aws:dynamodb:us-east-1:*:table/appointment-matching-doctors/index/*"
            ]
        )
        
        self.lambda_role.add_to_policy(dynamodb_policy)
        
        # Add Secrets Manager permissions
        secrets_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            resources=[
                f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:user-management/*"
            ]
        )
        
        self.lambda_role.add_to_policy(secrets_policy)
        
        # Add SSM Parameter Store permissions
        ssm_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:GetParametersByPath"
            ],
            resources=[
                f"arn:aws:ssm:{self.region}:{self.account}:parameter/user-management/*"
            ]
        )
        
        self.lambda_role.add_to_policy(ssm_policy)

    def create_lambda_function(self):
        """Create Lambda function for the User Management Service."""
        
        # Create main Lambda function (without layer for now)
        self.lambda_function = _lambda.Function(
            self, "UserManagementFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="user_management_service.flask_lambda_handler.lambda_handler",
            code=_lambda.Code.from_asset("../../src"),
            role=self.lambda_role,
            # layers=[self.lambda_layer],  # Removed for now
            timeout=Duration.seconds(30),
            memory_size=512,
            architecture=_lambda.Architecture.ARM_64,  # Use ARM architecture
            environment={
                "USERS_TABLE_NAME": self.users_table.table_name,
                "DYNAMODB_TABLE_NAME": self.users_table.table_name,  # For compatibility
                "SPECIALTIES_TABLE_NAME": self.specialties_table.table_name,
                "AVAILABILITY_TABLE_NAME": self.availability_table.table_name,
                "SESSIONS_TABLE_NAME": self.sessions_table.table_name,
                "EVENTS_TABLE_NAME": self.events_table.table_name,
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "production",
                "USE_DYNAMODB": "true"
            },
            tracing=_lambda.Tracing.ACTIVE,  # Enable X-Ray tracing
            dead_letter_queue_enabled=True,
            reserved_concurrent_executions=50  # Limit concurrent executions
        )
        
        # Create CloudWatch log group with retention
        self.lambda_log_group = logs.LogGroup(
            self, "UserManagementLambdaLogGroup",
            log_group_name=f"/aws/lambda/{self.lambda_function.function_name}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

    def create_api_gateway(self):
        """Create API Gateway for the User Management Service."""
        
        # Create API Gateway
        self.api = apigateway.RestApi(
            self, "UserManagementApi",
            rest_api_name="User Management Service API",
            description="REST API for user registration, profile management, session management, and doctor availability",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["*"]
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,  # 100 requests per second
                throttling_burst_limit=200,
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True
            )
        )
        
        # Create Lambda integration
        lambda_integration = apigateway.LambdaIntegration(
            self.lambda_function,
            proxy=True
        )
        
        # Add proxy resource to handle all paths
        proxy_resource = self.api.root.add_proxy(
            default_integration=lambda_integration,
            any_method=True
        )
        
        # Create usage plan for rate limiting
        self.usage_plan = self.api.add_usage_plan(
            "UserManagementUsagePlan",
            name="User Management API Usage Plan",
            throttle=apigateway.ThrottleSettings(
                rate_limit=100,  # 100 requests per second
                burst_limit=200
            ),
            quota=apigateway.QuotaSettings(
                limit=10000,  # 10,000 requests per day
                period=apigateway.Period.DAY
            )
        )
        
        # Add API stage to usage plan
        self.usage_plan.add_api_stage(
            stage=self.api.deployment_stage
        )

    def create_monitoring(self):
        """Create CloudWatch monitoring resources."""
        
        # Create CloudWatch dashboard
        self.dashboard = cloudwatch.Dashboard(
            self, "UserManagementDashboard",
            dashboard_name="UserManagementService"
        )
        
        # Lambda metrics
        lambda_error_rate = cloudwatch.Metric(
            namespace="AWS/Lambda",
            metric_name="ErrorRate",
            dimensions_map={
                "FunctionName": self.lambda_function.function_name
            },
            statistic="Average"
        )
        
        lambda_duration = cloudwatch.Metric(
            namespace="AWS/Lambda",
            metric_name="Duration",
            dimensions_map={
                "FunctionName": self.lambda_function.function_name
            },
            statistic="Average"
        )
        
        lambda_invocations = cloudwatch.Metric(
            namespace="AWS/Lambda",
            metric_name="Invocations",
            dimensions_map={
                "FunctionName": self.lambda_function.function_name
            },
            statistic="Sum"
        )
        
        # API Gateway metrics
        api_4xx_errors = cloudwatch.Metric(
            namespace="AWS/ApiGateway",
            metric_name="4XXError",
            dimensions_map={
                "ApiName": self.api.rest_api_name
            },
            statistic="Sum"
        )
        
        api_5xx_errors = cloudwatch.Metric(
            namespace="AWS/ApiGateway",
            metric_name="5XXError",
            dimensions_map={
                "ApiName": self.api.rest_api_name
            },
            statistic="Sum"
        )
        
        api_latency = cloudwatch.Metric(
            namespace="AWS/ApiGateway",
            metric_name="Latency",
            dimensions_map={
                "ApiName": self.api.rest_api_name
            },
            statistic="Average"
        )
        
        # Add widgets to dashboard
        self.dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Function Metrics",
                left=[lambda_invocations],
                right=[lambda_error_rate, lambda_duration]
            ),
            cloudwatch.GraphWidget(
                title="API Gateway Metrics",
                left=[api_4xx_errors, api_5xx_errors],
                right=[api_latency]
            )
        )
        
        # Create alarms
        self.lambda_error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorAlarm",
            metric=lambda_error_rate,
            threshold=5,  # 5% error rate
            evaluation_periods=2,
            datapoints_to_alarm=2,
            alarm_description="Lambda function error rate is too high"
        )
        
        self.api_5xx_alarm = cloudwatch.Alarm(
            self, "Api5xxErrorAlarm",
            metric=api_5xx_errors,
            threshold=10,  # 10 5xx errors in 5 minutes
            evaluation_periods=1,
            alarm_description="API Gateway 5xx error rate is too high"
        )

    def create_configuration(self):
        """Create configuration parameters and secrets."""
        
        # Create JWT secret in Secrets Manager
        self.jwt_secret = secretsmanager.Secret(
            self, "JwtSecret",
            secret_name="user-management/jwt-secret",
            description="JWT secret key for User Management Service",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"jwt_secret_key": ""}',
                generate_string_key="jwt_secret_key",
                exclude_characters='"@/\\'
            )
        )
        
        # Create configuration parameters
        self.config_parameters = {
            "log_level": ssm.StringParameter(
                self, "LogLevelParameter",
                parameter_name="/user-management/config/log-level",
                string_value="INFO",
                description="Log level for User Management Service"
            ),
            "jwt_expiration_hours": ssm.StringParameter(
                self, "JwtExpirationParameter",
                parameter_name="/user-management/config/jwt-expiration-hours",
                string_value="24",
                description="JWT token expiration time in hours"
            ),
            "session_timeout_minutes": ssm.StringParameter(
                self, "SessionTimeoutParameter",
                parameter_name="/user-management/config/session-timeout-minutes",
                string_value="1440",  # 24 hours
                description="Session timeout in minutes"
            ),
            "max_login_attempts": ssm.StringParameter(
                self, "MaxLoginAttemptsParameter",
                parameter_name="/user-management/config/max-login-attempts",
                string_value="5",
                description="Maximum login attempts before lockout"
            )
        }

    def create_outputs(self):
        """Create CloudFormation outputs."""
        
        CfnOutput(
            self, "ApiGatewayUrl",
            value=self.api.url,
            description="API Gateway URL for User Management Service"
        )
        
        CfnOutput(
            self, "LambdaFunctionName",
            value=self.lambda_function.function_name,
            description="Lambda function name"
        )
        
        CfnOutput(
            self, "UsersTableName",
            value=self.users_table.table_name,
            description="DynamoDB Users table name"
        )
        
        CfnOutput(
            self, "SpecialtiesTableName",
            value=self.specialties_table.table_name,
            description="DynamoDB Specialties table name"
        )
        
        CfnOutput(
            self, "AvailabilityTableName",
            value=self.availability_table.table_name,
            description="DynamoDB Availability table name"
        )
        
        CfnOutput(
            self, "SessionsTableName",
            value=self.sessions_table.table_name,
            description="DynamoDB Sessions table name"
        )
        
        CfnOutput(
            self, "EventsTableName",
            value=self.events_table.table_name,
            description="DynamoDB Events table name"
        )
        
        CfnOutput(
            self, "DashboardUrl",
            value=f"https://console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name={self.dashboard.dashboard_name}",
            description="CloudWatch Dashboard URL"
        )