import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.client = None
        self.twilio_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        
        # Try to import twilio, but don't fail if not available
        try:
            from twilio.rest import Client
            if (hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID and
                hasattr(settings, 'TWILIO_AUTH_TOKEN') and settings.TWILIO_AUTH_TOKEN):
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("Twilio SMS service initialized")
            else:
                logger.warning("Twilio credentials not configured")
        except ImportError:
            logger.warning("Twilio not installed, SMS service will log only")
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS message or log if not configured"""
        if not self.client or not self.twilio_phone:
            logger.info(f"📱 SMS would be sent to {to_phone}: {message[:50]}...")
            return True  # Return True for development
        
        try:
            # Format phone number
            if not to_phone.startswith('+'):
                to_phone = f'+{to_phone}' if not to_phone.startswith('00') else f'+{to_phone[2:]}'
            
            sms = self.client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            logger.info(f"SMS sent to {to_phone}: {sms.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    
    def send_emergency_alert_sms(self, to_phone: str, patient_name: str, alert_type: str, location: Optional[str] = None):
        """Send emergency alert SMS"""
        message = f"🚨 EMERGENCY ALERT for {patient_name}\n"
        message += f"Alert: {alert_type}\n"
        message += "HEWAL3 detected critical vitals. "
        message += "Emergency services have been notified."
        
        if location:
            message += f"\nLocation: {location}"
        
        message += "\n\nHEWAL3 Emergency Response"
        
        return self.send_sms(to_phone, message)
    
    def send_otp_sms(self, to_phone: str, otp: str):
        """Send OTP for login"""
        message = f"Your HEWAL3 verification code is: {otp}\n"
        message += "This code expires in 10 minutes.\n"
        message += "If you didn't request this, please ignore."
        
        return self.send_sms(to_phone, message)
    
    def send_appointment_reminder(self, to_phone: str, patient_name: str, appointment_time: str, doctor_name: str, location: str):
        """Send appointment reminder"""
        message = f"📅 Appointment Reminder\n"
        message += f"Hello {patient_name},\n"
        message += f"You have an appointment with Dr. {doctor_name}\n"
        message += f"Time: {appointment_time}\n"
        message += f"Location: {location}\n"
        message += "\nPlease arrive 15 minutes early.\n"
        message += "HEWAL3 Health System"
        
        return self.send_sms(to_phone, message)

# Singleton instance
sms_service = SMSService()