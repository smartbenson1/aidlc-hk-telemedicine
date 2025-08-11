#!/usr/bin/env python3
"""
CDK App for shared infrastructure components
"""

import aws_cdk as cdk
from eventbridge_stack import EventBridgeIntegrationStack

app = cdk.App()

# Deploy EventBridge integration stack
EventBridgeIntegrationStack(
    app, 
    "HealMatchEventBridgeStack",
    description="EventBridge integration for HealMatch services",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    ),
    tags={
        "Project": "HealMatch",
        "Component": "EventBridge",
        "Environment": "production"
    }
)

app.synth()