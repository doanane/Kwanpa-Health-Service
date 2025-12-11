from app.database import Base

# Import in order to avoid circular dependencies
from .auth import PasswordResetToken, EmailVerificationToken, LoginOTP, RefreshToken, UserSession
from .admin import Admin
from .caregiver import Doctor, CaregiverRelationship
from .user import User, UserProfile, UserDevice
from .health import HealthData, FoodLog, WeeklyProgress, HealthInsight
from .notification import Notification
from .emergency import EmergencyContact, EmergencyEvent
from .iot_device import IoTDevice, VitalReading

__all__ = [
    # Auth models
    "PasswordResetToken", "EmailVerificationToken", "LoginOTP", "RefreshToken", "UserSession",
    # User models
    "User", "UserProfile", "UserDevice",
    # Admin models
    "Admin",
    # Caregiver models
    "Doctor", "CaregiverRelationship",
    # Health models
    "HealthData", "FoodLog", "WeeklyProgress", "HealthInsight",
    # Notification models
    "Notification", 
    # Emergency models
    "EmergencyContact", "EmergencyEvent",
    # IoT models
    "IoTDevice", "VitalReading"
]