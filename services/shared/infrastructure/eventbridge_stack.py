"""
CDK Stack for EventBridge integration between services
"""

from aws_cdk import (
    Stack,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration,
    CfnOutput
)
from constructs import Construct


class EventBridgeIntegrationStack(Stack):
    """CDK Stack for EventBridge-based service integration"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create custom event bus for HealMatch services
        self.event_bus = events.EventBus(
            self, "HealMatchEventBus",
            event_bus_name="healmatch-events",
            description="Event bus for HealMatch service integration"
        )

        # Create Lambda function for appointment matching event consumer
        self.event_consumer_lambda = _lambda.Function(
            self, "AppointmentMatchingEventConsumer",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="event_consumer.lambda_handler",
            code=_lambda.Code.from_asset("../appointment-matching/lambda"),
            timeout=Duration.minutes(5),
            memory_size=256,
            environment={
                'APPOINTMENT_MATCHING_DOCTORS_TABLE': 'appointment-matching-doctors'
            }
        )

        # Grant DynamoDB permissions to the Lambda
        self.event_consumer_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:GetItem"
                ],
                resources=[
                    f"arn:aws:dynamodb:{self.region}:{self.account}:table/appointment-matching-doctors"
                ]
            )
        )

        # Create EventBridge rule for doctor registration events
        doctor_registration_rule = events.Rule(
            self, "DoctorRegistrationRule",
            event_bus=self.event_bus,
            event_pattern=events.EventPattern(
                source=["user-management-service"],
                detail_type=["Doctor Registered", "Doctor Updated"]
            ),
            description="Route doctor events to appointment matching service"
        )

        # Add Lambda target to the rule
        doctor_registration_rule.add_target(
            targets.LambdaFunction(self.event_consumer_lambda)
        )

        # Grant EventBridge permissions to User Management Service Lambda
        self.user_management_eventbridge_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "events:PutEvents"
            ],
            resources=[
                self.event_bus.event_bus_arn
            ]
        )

        # Create outputs
        CfnOutput(
            self, "EventBusName",
            value=self.event_bus.event_bus_name,
            description="Name of the HealMatch event bus",
            export_name="HealMatch-EventBusName"
        )

        CfnOutput(
            self, "EventBusArn",
            value=self.event_bus.event_bus_arn,
            description="ARN of the HealMatch event bus",
            export_name="HealMatch-EventBusArn"
        )

        CfnOutput(
            self, "EventConsumerLambdaArn",
            value=self.event_consumer_lambda.function_arn,
            description="ARN of the appointment matching event consumer Lambda",
            export_name="HealMatch-EventConsumerLambdaArn"
        )