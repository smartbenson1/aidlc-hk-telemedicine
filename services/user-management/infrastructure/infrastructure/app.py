#!/usr/bin/env python3
"""
AWS CDK App for User Management Service

This is the main CDK application that creates the infrastructure stack
for the User Management Service.
"""

import aws_cdk as cdk
from user_management_service_stack import UserManagementServiceStack


app = cdk.App()

# Create the User Management Service stack
UserManagementServiceStack(
    app, 
    "UserManagementServiceStack",
    description="Infrastructure for User Management Service API",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    ),
    tags={
        "Project": "AIDLC",
        "Service": "UserManagementService",
        "Environment": app.node.try_get_context("environment") or "production",
        "Owner": "Development Team"
    }
)

app.synth()