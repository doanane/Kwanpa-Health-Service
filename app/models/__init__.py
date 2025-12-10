
from app.database import Base

# Then import models (order matters)
from .user import User, UserProfile, UserDevice
from .admin import Admin
from .caregiver import Doctor, CaregiverRelationship
from .health import HealthData, FoodLog, WeeklyProgress, HealthInsight
from .notification import Notification
from .emergency import EmergencyContact, EmergencyEvent
from .iot_device import IoTDevice, VitalReading


__all__ = [
    "User", "UserProfile", "UserDevice", "Admin",
    "Doctor", "CaregiverRelationship",
    "HealthData", "FoodLog", "WeeklyProgress", "HealthInsight",
    "Notification", 
    "EmergencyContact", "EmergencyEvent",
    "IoTDevice", "VitalReading"
]