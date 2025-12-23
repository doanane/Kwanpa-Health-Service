import logging
import requests
from typing import Optional
from app.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.api_key = getattr(settings, 'INFOBIP_API_KEY', '')
        self.base_url = getattr(settings, 'INFOBIP_BASE_URL', '')
        self.sender_number = getattr(settings, 'INFOBIP_SENDER_NUMBER', '+447491163443')
        
        # if self.api_key and self.base_url:
        #     logger.info(f"✅ Infobip SMS service initialized with sender: {self.sender_number}")
        # else:
        #     logger.warning("Infobip credentials not fully configured in .env file")
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Demo mode - always return success without sending"""
        logger.info(f"📱 [DEMO MODE] SMS would be sent to {to_phone}: {message[:100]}...")
        logger.info(f"💡 For demo: Use /auth/login/otp/request for email OTP")
        return True  
        
    def send_otp_sms(self, to_phone: str, otp: str):
        """Send OTP for login"""
        message = f"""HEWAL3 Verification Code: {otp}

This code expires in 10 minutes.
Use it to verify your login.

If you didn't request this, please ignore.

HEWAL3 Health System"""
        return self.send_sms(to_phone, message)
    
    def send_emergency_alert_sms(self, to_phone: str, patient_name: str, alert_type: str, vitals: dict = None, location: Optional[str] = None):
        """Send emergency alert SMS to caregivers"""
        vital_text = ""
        if vitals:
            vital_text = "\n".join([f"{k}: {v}" for k, v in vitals.items()])
        
        message = f"""🚨 EMERGENCY ALERT 🚨

Patient: {patient_name}
Alert Type: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{vital_text}

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

# ⚠️ CRITICAL: This line MUST be at the bottom of the file
# This creates the singleton instance that other files import
sms_service = SMSService()