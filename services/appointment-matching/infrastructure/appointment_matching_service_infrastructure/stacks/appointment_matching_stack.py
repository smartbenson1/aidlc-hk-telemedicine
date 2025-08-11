"""
Main CDK Stack for Appointment Matching Service
"""

from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_logs as logs,
    RemovalPolicy,
    Duration
)
from constructs import Construct


class AppointmentMatchingStack(Stack):
    """CDK Stack for Appointment Matching Service Infrastructure"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Tables
        self.create_dynamodb_tables()
        
        # Lambda Functions
        self.create_lambda_functions()
        
        # API Gateway
        self.create_api_gateway()
        
        # CloudWatch Resources
        self.create_monitoring()

    def create_dynamodb_tables(self):
        """Create DynamoDB tables for the service"""
        
        # Doctors Table
        self.doctors_table = dynamodb.Table(
            self, "DoctorsTable",
            table_name="appointment-matching-doctors",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,  # For development
            point_in_time_recovery=True
        )
        
        # Add GSI for email lookup
        self.doctors_table.add_global_secondary_index(
            index_name="email-index",
            partition_key=dynamodb.Attribute(
                name="email",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Patients Table
        self.patients_table = dynamodb.Table(
            self, "PatientsTable",
            table_name="appointment-matching-patients",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )
        
        # Add GSI for email lookup
        self.patients_table.add_global_secondary_index(
            index_name="email-index",
            partition_key=dynamodb.Attribute(
                name="email",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Appointments Table
        self.appointments_table = dynamodb.Table(
            self, "AppointmentsTable",
            table_name="appointment-matching-appointments",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )
        
        # Add GSI for patient appointments
        self.appointments_table.add_global_secondary_index(
            index_name="patient-index",
            partition_key=dynamodb.Attribute(
                name="patient_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="datetime",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Add GSI for doctor appointments
        self.appointments_table.add_global_secondary_index(
            index_name="doctor-index",
            partition_key=dynamodb.Attribute(
                name="doctor_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="datetime",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Symptom Descriptions Table
        self.symptoms_table = dynamodb.Table(
            self, "SymptomsTable",
            table_name="appointment-matching-symptoms",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )
        
        # Add GSI for patient symptoms
        self.symptoms_table.add_global_secondary_index(
            index_name="patient-index",
            partition_key=dynamodb.Attribute(
                name="patient_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Medical Specialties Table
        self.specialties_table = dynamodb.Table(
            self, "SpecialtiesTable",
            table_name="appointment-matching-specialties",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )

        # Doctor Recommendations Table
        self.recommendations_table = dynamodb.Table(
            self, "RecommendationsTable",
            table_name="appointment-matching-recommendations",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )

    def create_lambda_functions(self):
        """Create Lambda functions for the service"""
        
        # Create Lambda execution role
        lambda_role = iam.Role(
            self, "AppointmentMatchingLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Grant DynamoDB permissions
        for table in [self.doctors_table, self.patients_table, self.appointments_table, 
                     self.symptoms_table, self.specialties_table, self.recommendations_table]:
            table.grant_read_write_data(lambda_role)

        # Main Lambda function
        self.main_lambda = _lambda.Function(
            self, "AppointmentMatchingFunction",
            function_name="appointment-matching-service",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("../../lambda"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "DOCTORS_TABLE": self.doctors_table.table_name,
                "PATIENTS_TABLE": self.patients_table.table_name,
                "APPOINTMENTS_TABLE": self.appointments_table.table_name,
                "SYMPTOMS_TABLE": self.symptoms_table.table_name,
                "SPECIALTIES_TABLE": self.specialties_table.table_name,
                "RECOMMENDATIONS_TABLE": self.recommendations_table.table_name
            }
        )

    def create_api_gateway(self):
        """Create API Gateway for public API exposure"""
        
        # Create API Gateway
        self.api = apigateway.RestApi(
            self, "AppointmentMatchingApi",
            rest_api_name="appointment-matching-service",
            description="API for Appointment Matching Service",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,  # 100 RPS as requested
                throttling_burst_limit=200,
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True
            )
        )

        # Lambda integration
        lambda_integration = apigateway.LambdaIntegration(
            self.main_lambda,
            proxy=True
        )

        # API Resources and Methods
        # Health check
        health = self.api.root.add_resource("health")
        health.add_method("GET", lambda_integration)

        # Symptoms endpoints
        symptoms = self.api.root.add_resource("symptoms")
        symptoms.add_method("POST", lambda_integration)  # Describe symptoms
        
        symptom_id = symptoms.add_resource("{symptom_id}")
        symptom_id.add_method("GET", lambda_integration)  # Get symptom details

        # Recommendations endpoints
        recommendations = self.api.root.add_resource("recommendations")
        recommendations.add_method("POST", lambda_integration)  # Get recommendations
        
        recommendation_id = recommendations.add_resource("{recommendation_id}")
        recommendation_id.add_method("GET", lambda_integration)

        # Appointments endpoints
        appointments = self.api.root.add_resource("appointments")
        appointments.add_method("POST", lambda_integration)  # Book appointment
        appointments.add_method("GET", lambda_integration)   # List appointments
        
        appointment_id = appointments.add_resource("{appointment_id}")
        appointment_id.add_method("GET", lambda_integration)    # Get appointment
        appointment_id.add_method("PUT", lambda_integration)    # Update appointment
        
        reschedule = appointment_id.add_resource("reschedule")
        reschedule.add_method("POST", lambda_integration)  # Reschedule appointment

        # Doctors endpoints (for viewing appointments)
        doctors = self.api.root.add_resource("doctors")
        doctor_id = doctors.add_resource("{doctor_id}")
        doctor_appointments = doctor_id.add_resource("appointments")
        doctor_appointments.add_method("GET", lambda_integration)

        # Patients endpoints
        patients = self.api.root.add_resource("patients")
        patient_id = patients.add_resource("{patient_id}")
        patient_appointments = patient_id.add_resource("appointments")
        patient_appointments.add_method("GET", lambda_integration)

    def create_monitoring(self):
        """Create CloudWatch monitoring resources"""
        
        # Log groups
        self.api_log_group = logs.LogGroup(
            self, "ApiGatewayLogGroup",
            log_group_name=f"/aws/apigateway/{self.api.rest_api_name}",
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.lambda_log_group = logs.LogGroup(
            self, "LambdaLogGroup", 
            log_group_name=f"/aws/lambda/{self.main_lambda.function_name}",
            removal_policy=RemovalPolicy.DESTROY
        )