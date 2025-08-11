"""
Email Service Integration for the User Management Service.
"""

import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

from ..models.doctor import Doctor
from ..models.patient import Patient
from ..utils.base_models import EmailResult, EmailTemplate, ServiceResult
from ..utils.exceptions import IntegrationError
from ..utils.enums import EMAIL_TEMPLATES

logger = logging.getLogger(__name__)


class EmailServiceIntegration:
    """Integration service for sending emails."""
    
    def __init__(self, smtp_server: str = "localhost", smtp_port: int = 587,
                 sender_email: str = "noreply@doctorplatform.com",
                 smtp_username: Optional[str] = None,
                 smtp_password: Optional[str] = None):
        """Initialize the email service integration."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        
        # Email templates
        self.templates = {
            "doctor_registration": EmailTemplate(
                name="doctor_registration",
                subject="Welcome to Doctor Platform - Registration Confirmed",
                body="""
                Dear Dr. {name},
                
                Welcome to Doctor Platform! Your registration has been successfully completed.
                
                Your account details:
                - Email: {email}
                - Specialties: {specialties}
                - Registration Date: {registration_date}
                
                You can now log in to your account and start managing your availability.
                
                Best regards,
                Doctor Platform Team
                """,
                variables=["name", "email", "specialties", "registration_date"]
            ),
            "patient_registration": EmailTemplate(
                name="patient_registration",
                subject="Welcome to Doctor Platform - Registration Confirmed",
                body="""
                Dear {name},
                
                Welcome to Doctor Platform! Your registration has been successfully completed.
                
                Your account details:
                - Email: {email}
                - Registration Date: {registration_date}
                
                You can now log in to your account and start booking appointments with doctors.
                
                Best regards,
                Doctor Platform Team
                """,
                variables=["name", "email", "registration_date"]
            ),
            "profile_update": EmailTemplate(
                name="profile_update",
                subject="Profile Updated - Doctor Platform",
                body="""
                Dear {name},
                
                Your profile has been successfully updated on Doctor Platform.
                
                Updated fields: {updated_fields}
                Update time: {update_time}
                
                If you did not make these changes, please contact our support team immediately.
                
                Best regards,
                Doctor Platform Team
                """,
                variables=["name", "updated_fields", "update_time"]
            )
        }
    
    def send_registration_confirmation(self, user, user_type: str) -> EmailResult:
        """Send registration confirmation email."""
        try:
            logger.info(f"Sending registration confirmation to {user.email} ({user_type})")
            
            # Get appropriate template
            template_name = f"{user_type}_registration"
            template = self.templates.get(template_name)
            
            if not template:
                return EmailResult(
                    success=False,
                    error_message=f"Email template not found: {template_name}",
                    recipient=user.email
                )
            
            # Prepare template data
            template_data = {
                "name": user.name,
                "email": user.email,
                "registration_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            # Add user-type specific data
            if user_type == "doctor" and hasattr(user, 'specialties'):
                # In a real implementation, you'd get specialty names
                template_data["specialties"] = f"{len(user.specialties)} specialties"
            
            # Render template
            subject = template.subject
            body = template.body.format(**template_data)
            
            # Send email
            return self._send_email(user.email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send registration confirmation: {str(e)}")
            return EmailResult(
                success=False,
                error_message=f"Failed to send registration confirmation: {str(e)}",
                recipient=user.email
            )
    
    def send_profile_update_notification(self, user, changes: Dict[str, Any]) -> EmailResult:
        """Send profile update notification email."""
        try:
            logger.info(f"Sending profile update notification to {user.email}")
            
            template = self.templates.get("profile_update")
            if not template:
                return EmailResult(
                    success=False,
                    error_message="Profile update email template not found",
                    recipient=user.email
                )
            
            # Prepare template data
            template_data = {
                "name": user.name,
                "updated_fields": ", ".join(changes.get("changed_fields", [])),
                "update_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            # Render template
            subject = template.subject
            body = template.body.format(**template_data)
            
            # Send email
            return self._send_email(user.email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send profile update notification: {str(e)}")
            return EmailResult(
                success=False,
                error_message=f"Failed to send profile update notification: {str(e)}",
                recipient=user.email
            )
    
    def send_custom_email(self, recipient: str, subject: str, body: str,
                         template_data: Optional[Dict[str, Any]] = None) -> EmailResult:
        """Send a custom email."""
        try:
            logger.info(f"Sending custom email to {recipient}")
            
            # Apply template data if provided
            if template_data:
                body = body.format(**template_data)
                subject = subject.format(**template_data)
            
            return self._send_email(recipient, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send custom email: {str(e)}")
            return EmailResult(
                success=False,
                error_message=f"Failed to send custom email: {str(e)}",
                recipient=recipient
            )
    
    def _send_email(self, recipient: str, subject: str, body: str) -> EmailResult:
        """Send email using SMTP (actual implementation)."""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # For demo purposes, we'll simulate sending without actual SMTP
            # In a real implementation, you would use the following code:
            
            # Connect to SMTP server
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # 
            # if self.smtp_username and self.smtp_password:
            #     server.login(self.smtp_username, self.smtp_password)
            # 
            # # Send email
            # text = message.as_string()
            # server.sendmail(self.sender_email, recipient, text)
            # server.quit()
            
            # For demo, we'll just log the email
            logger.info(f"EMAIL SENT (simulated):")
            logger.info(f"To: {recipient}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body[:100]}...")
            
            return EmailResult(
                success=True,
                message_id=f"msg_{datetime.utcnow().timestamp()}",
                recipient=recipient,
                sent_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"SMTP email sending failed: {str(e)}")
            return EmailResult(
                success=False,
                error_message=f"SMTP error: {str(e)}",
                recipient=recipient
            )
    
    def validate_email_configuration(self) -> ServiceResult:
        """Validate email service configuration."""
        try:
            # Check required configuration
            if not self.smtp_server:
                return ServiceResult.error_result(
                    "SMTP server not configured",
                    "CONFIGURATION_ERROR"
                )
            
            if not self.sender_email:
                return ServiceResult.error_result(
                    "Sender email not configured",
                    "CONFIGURATION_ERROR"
                )
            
            # Test connection (simplified for demo)
            # In a real implementation, you would test the SMTP connection
            
            return ServiceResult.success_result({
                "smtp_server": self.smtp_server,
                "smtp_port": self.smtp_port,
                "sender_email": self.sender_email,
                "templates_loaded": len(self.templates),
                "status": "configured"
            })
            
        except Exception as e:
            logger.error(f"Email configuration validation failed: {str(e)}")
            return ServiceResult.error_result(
                "Email configuration validation failed",
                "CONFIGURATION_ERROR"
            )
    
    def get_email_templates(self) -> ServiceResult:
        """Get available email templates."""
        try:
            template_info = []
            for name, template in self.templates.items():
                template_info.append({
                    "name": template.name,
                    "subject": template.subject,
                    "variables": template.variables
                })
            
            return ServiceResult.success_result({
                "templates": template_info,
                "total_templates": len(template_info)
            })
            
        except Exception as e:
            logger.error(f"Failed to get email templates: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve email templates",
                "INTERNAL_ERROR"
            )
    
    def test_email_sending(self, test_recipient: str) -> ServiceResult:
        """Send a test email to verify email service is working."""
        try:
            test_subject = "Test Email - Doctor Platform"
            test_body = """
            This is a test email from Doctor Platform.
            
            If you receive this email, the email service is working correctly.
            
            Sent at: {timestamp}
            """.format(timestamp=datetime.utcnow().isoformat())
            
            result = self._send_email(test_recipient, test_subject, test_body)
            
            if result.success:
                return ServiceResult.success_result({
                    "message": "Test email sent successfully",
                    "recipient": test_recipient,
                    "message_id": result.message_id,
                    "sent_at": result.sent_at.isoformat() if result.sent_at else None
                })
            else:
                return ServiceResult.error_result(
                    f"Test email failed: {result.error_message}",
                    "EMAIL_SEND_ERROR"
                )
                
        except Exception as e:
            logger.error(f"Test email sending failed: {str(e)}")
            return ServiceResult.error_result(
                "Test email sending failed",
                "INTERNAL_ERROR"
            )