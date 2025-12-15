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
        """Send an email using SendGrid"""
        
        
        logger.info(f"DEBUG: SendGrid client exists: {self.sendgrid_client is not None}")
        logger.info(f"DEBUG: API Key configured: {hasattr(settings, 'SENDGRID_API_KEY')}")
        
        if not self.sendgrid_client:
            logger.error("❌ SendGrid client not initialized. Check SENDGRID_API_KEY in .env")
            logger.info(f"📧 Email WOULD be sent to {to_email}: {subject}")
            logger.info(f"HTML preview: {html_content[:200]}...")
            return False  
        
        try:
            from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, Content
            
            
            message = Mail(
                from_email=From(self.from_email, "HEWAL3 Health System"),
                to_emails=To(to_email),
                subject=Subject(subject),
                html_content=HtmlContent(html_content)
            )
            
            
            if text_content:
                message.content = Content("text/plain", text_content)
            
            
            response = self.sendgrid_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Email ACTUALLY sent to {to_email}")
                return True
            else:
                logger.error(f"❌ Failed to send email: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False    

    def send_welcome_email(self, user_email: str, user_name: str, verification_token: str):
        """Send welcome email with verification link"""
        verification_link = f"{self.base_url}/auth/verify-email-page/{verification_token}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: 
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: 
                .content {{ padding: 30px; background-color: 
                .button {{ display: inline-block; padding: 12px 24px; background-color: 
                .footer {{ text-align: center; padding: 20px; color: 
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
                    <p style="word-break: break-all; color: 
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


    def send_otp_email(self, user_email: str, user_name: str, otp: str):
        """Send OTP code via email"""
        subject = f"Your HEWAL3 Verification Code: {otp}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: 
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: 
                .content {{ padding: 30px; background-color: 
                .otp-box {{ 
                    font-size: 32px; 
                    font-weight: bold; 
                    text-align: center; 
                    padding: 20px; 
                    background: white; 
                    border: 3px dashed 
                    margin: 20px 0; 
                    letter-spacing: 5px;
                }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
                .footer {{ text-align: center; padding: 20px; color: 
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>HEWAL3 Login Verification</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>You requested a login verification code for your HEWAL3 account.</p>
                    
                    <div class="otp-box">
                        {otp}
                    </div>
                    
                    <p><strong>This code will expire in 10 minutes.</strong></p>
                    
                    <p>Enter this code in the HEWAL3 app to complete your login.</p>
                    
                    <p>If you didn't request this code, please ignore this email or contact support if you're concerned about your account security.</p>
                </div>
                <div class="footer">
                    <p>© 2025 HEWAL3 Health System. All rights reserved.</p>
                    <p>For support, contact: {self.support_email}</p>
                    <p>This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        HEWAL3 Login Verification
        
        Hello {user_name},
        
        You requested a login verification code for your HEWAL3 account.
        
        Your verification code is: {otp}
        
        This code will expire in 10 minutes.
        
        Enter this code in the HEWAL3 app to complete your login.
        
        If you didn't request this code, please ignore this email.
        
        © 2025 HEWAL3 Health System
        """
        
        return self.send_email(user_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, user_email: str, reset_token: str):
        """Send password reset email"""
        reset_link = f"{self.base_url}/auth/reset-password-page?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: 
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: 
                .content {{ padding: 30px; background-color: 
                .button {{ display: inline-block; padding: 12px 24px; background-color: 
                .footer {{ text-align: center; padding: 20px; color: 
                .warning {{ color: 
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
                    <p style="word-break: break-all; color: 
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


email_service = EmailService()