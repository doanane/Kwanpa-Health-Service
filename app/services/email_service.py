import os
import logging
from typing import List, Optional, Dict, Any
from jinja2 import Template
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sendgrid_client = None
        self.base_url = settings.BASE_URL
        self.frontend_url = settings.FRONTEND_URL

        try:
            from sendgrid import SendGridAPIClient
            if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
                self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
                logger.info("SendGrid email service initialized")
            else:
                logger.warning("SendGrid API key not configured")
        except ImportError:
            logger.warning("SendGrid not installed, email service will log only")
        
        self.from_email = getattr(settings, 'FROM_EMAIL', "noreply@hewal3.com")
        self.support_email = getattr(settings, 'HEWAL3_SUPPORT_EMAIL', "support@hewal3.com")
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """Send an email using SendGrid or log if not configured"""
        if not self.sendgrid_client:
            logger.info(f"📧 Email would be sent to {to_email}: {subject}")
            logger.info(f"HTML content preview: {html_content[:200]}...")
            return True  # Return True for development
        
        try:
            from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent
            
            message = Mail(
                from_email=From(self.from_email, "HEWAL3 Health System"),
                to_emails=To(to_email),
                subject=Subject(subject),
                html_content=HtmlContent(html_content)
            )
            
            response = self.sendgrid_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    
    def send_welcome_email(self, user_email: str, user_name: str, verification_token: str):
        """Send welcome email with verification link"""
        verification_link = f"{self.base_url}/auth/verify-email-page/{verification_token}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to HEWAL3!</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Thank you for joining HEWAL3 Health Management System. We're excited to help you take control of your health.</p>
                    <p>To get started, please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </p>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #4CAF50;">{verification_link}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't create an account with HEWAL3, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2025 HEWAL3 Health System. All rights reserved.</p>
                    <p>For support, contact: {self.support_email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to HEWAL3!
        
        Hello {user_name},
        
        Thank you for joining HEWAL3 Health Management System.
        
        Please verify your email address by visiting:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create an account with HEWAL3, please ignore this email.
        
        © 2025 HEWAL3 Health System
        """
        
        return self.send_email(user_email, "Verify Your HEWAL3 Account", html_content, text_content)
    
    def send_password_reset_email(self, user_email: str, reset_token: str):
        """Send password reset email"""
        reset_link = f"{self.base_url}/auth/reset-password-page?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ff6b6b; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #ff6b6b; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .warning {{ color: #ff6b6b; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your password for your HEWAL3 account.</p>
                    <p>Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>
                    <p>If the button doesn't work, copy and paste this link:</p>
                    <p style="word-break: break-all; color: #ff6b6b;">{reset_link}</p>
                    <p class="warning">This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.</p>
                    <p>For your security, never share your password or this reset link with anyone.</p>
                </div>
                <div class="footer">
                    <p>© 2025 HEWAL3 Health System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        We received a request to reset your password for your HEWAL3 account.
        
        Reset your password here:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request a password reset, please ignore this email.
        
        © 2025 HEWAL3 Health System
        """
        
        return self.send_email(user_email, "Reset Your HEWAL3 Password", html_content, text_content)
    
    def send_emergency_alert(self, patient_email: str, patient_name: str, alert_type: str, vitals: Dict[str, Any], doctor_name: str = None):
        """Send emergency alert email"""
        subject = f"🚨 EMERGENCY ALERT: {alert_type} detected"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #fff3cd; }}
                .vital {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #dc3545; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .action {{ background-color: #dc3545; color: white; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 EMERGENCY HEALTH ALERT</h1>
                </div>
                <div class="content">
                    <h2>Patient: {patient_name}</h2>
                    <p><strong>Alert Type:</strong> {alert_type}</p>
                    <p><strong>Time Detected:</strong> {vitals.get('timestamp', 'Just now')}</p>
                    
                    <h3>Vital Signs:</h3>
                    {"".join([f'<div class="vital"><strong>{k}:</strong> {v}</div>' for k, v in vitals.items() if k != 'timestamp'])}
                    
                    <div class="action">
                        <h3>IMMEDIATE ACTION REQUIRED</h3>
                        <p>1. Contact the patient immediately</p>
                        <p>2. Check if emergency services have been notified</p>
                        <p>3. Review patient's location and medical history</p>
                    </div>
                    
                    {f'<p><strong>Assigned Doctor:</strong> {doctor_name}</p>' if doctor_name else ''}
                    
                    <p>This is an automated alert from HEWAL3 Emergency Response System.</p>
                </div>
                <div class="footer">
                    <p>© 2025 HEWAL3 Emergency Response System</p>
                    <p>This is an automated message. Do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(patient_email, subject, html_content)
    
    def send_weekly_report(self, user_email: str, user_name: str, report_data: Dict[str, Any]):
        """Send weekly health report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .metric {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .good {{ border-left: 4px solid #4CAF50; }}
                .warning {{ border-left: 4px solid #ff9800; }}
                .danger {{ border-left: 4px solid #f44336; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Weekly Health Report</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Here's your weekly health summary for {report_data.get('week_range', 'this week')}:</p>
                    
                    <div class="metric good">
                        <h3>Progress Score: {report_data.get('progress_score', 0)}/100</h3>
                        <p>{report_data.get('progress_message', 'Keep up the good work!')}</p>
                    </div>
                    
                    {report_data.get('metrics_html', '')}
                    
                    <h3>Recommendations:</h3>
                    <ul>
                        {"".join([f'<li>{rec}</li>' for rec in report_data.get('recommendations', [])])}
                    </ul>
                    
                    <p>View your complete dashboard for more details and historical data.</p>
                </div>
                <div class="footer">
                    <p>© 2025 HEWAL3 Health System</p>
                    <p>Stay healthy, stay happy! 💚</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, "Your Weekly HEWAL3 Health Report", html_content)

# Singleton instance
email_service = EmailService()