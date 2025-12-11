import logging
from typing import Optional
from app.config import settings
import os

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.client = None
        self.twilio_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        
        # Check if Twilio credentials are configured
        if (hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID and
            hasattr(settings, 'TWILIO_AUTH_TOKEN') and settings.TWILIO_AUTH_TOKEN):
            
            # Try to import twilio
            try:
                from twilio.rest import Client
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("✅ Twilio SMS service initialized")
                
                # Test the connection
                try:
                    account = self.client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
                    logger.info(f"Twilio account status: {account.status}")
                except Exception as e:
                    logger.warning(f"Twilio connection test failed: {e}")
                    
            except ImportError:
                logger.warning("Twilio not installed. Run: pip install twilio")
                self.client = None
            except Exception as e:
                logger.error(f"Error initializing Twilio: {e}")
                self.client = None
        else:
            logger.warning("Twilio credentials not configured in .env file")
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS message using Twilio"""
        if not self.client or not self.twilio_phone:
            logger.error("Twilio not configured. Cannot send SMS.")
            logger.info(f"📱 SMS would be sent to {to_phone}: {message[:50]}...")
            return False
        
        try:
            # Format phone number (ensure it starts with +)
            if not to_phone.startswith('+'):
                if to_phone.startswith('0'):
                    # Assume Ghana number: +233XXXXXXXXX
                    to_phone = f'+233{to_phone[1:]}'
                elif to_phone.startswith('233'):
                    to_phone = f'+{to_phone}'
                else:
                    to_phone = f'+{to_phone}'
            
            # Validate phone number format
            if not to_phone.startswith('+'):
                logger.error(f"Invalid phone number format: {to_phone}")
                return False
            
            # Send SMS
            sms = self.client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            logger.info(f"✅ SMS sent to {to_phone}: {sms.sid}")
            logger.info(f"Message: {message[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending SMS: {e}")
            
            # More detailed error logging
            if hasattr(e, 'code'):
                logger.error(f"Twilio error code: {e.code}")
            if hasattr(e, 'message'):
                logger.error(f"Twilio error message: {e.message}")
            
            return False
    
    def send_otp_sms(self, to_phone: str, otp: str):
        """Send OTP for login"""
        message = f"""HEWAL3 Verification Code: {otp}

This code expires in 10 minutes. Use it to verify your login.

If you didn't request this, please ignore this message.

HEWAL3 Health System
support@hewal3.com"""
        
        return self.send_sms(to_phone, message)
    
    def send_emergency_alert_sms(self, to_phone: str, patient_name: str, alert_type: str, vitals: dict = None, location: Optional[str] = None):
        """Send emergency alert SMS to caregivers"""
        message = f"""🚨 EMERGENCY ALERT 🚨

Patient: {patient_name}
Alert Type: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{vitals}

Emergency services have been notified.

Location: {location if location else 'Unknown'}

HEWAL3 Emergency Response System
This is an automated alert."""
        
        return self.send_sms(to_phone, message)
    
    def send_appointment_reminder(self, to_phone: str, patient_name: str, appointment_time: str, doctor_name: str, location: str):
        """Send appointment reminder"""
        message = f"""📅 Appointment Reminder

Hello {patient_name},

You have an appointment with Dr. {doctor_name}
Date: {appointment_time}
Location: {location}

Please arrive 15 minutes early.
Bring your medical records and medications.

HEWAL3 Health System"""
        
        return self.send_sms(to_phone, message)

# Singleton instance
sms_service = SMSService()