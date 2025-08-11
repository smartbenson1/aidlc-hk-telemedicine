#!/usr/bin/env python3
"""
AWS CDK App for Appointment Matching Service Infrastructure
"""

import aws_cdk as cdk
from constructs import Construct

from stacks.appointment_matching_stack import AppointmentMatchingStack


class AppointmentMatchingApp(cdk.App):
    """Main CDK Application for Appointment Matching Service"""
    
    def __init__(self):
        super().__init__()
        
        # Environment configuration
        env = cdk.Environment(
            account=self.node.try_get_context("account"),
            region=self.node.try_get_context("region") or "us-east-1"
        )
        
        # Main stack
        AppointmentMatchingStack(
            self, 
            "AppointmentMatchingStack",
            env=env,
            description="Infrastructure for Appointment Matching Service"
        )


if __name__ == "__main__":
    app = AppointmentMatchingApp()
    app.synth()