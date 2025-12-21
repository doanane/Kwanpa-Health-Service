# app/models/user.py - COMPLETE VERSION
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import event
from app.database import Base
import random

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    patient_id = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    apple_id = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_caregiver = Column(Boolean, default=False)
   
    is_email_verified = Column(Boolean, default=False)
    phone_number = Column(String, nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    emergency_contacts = relationship("EmergencyContact", back_populates="user_rel", cascade="all, delete-orphan")
    emergency_events = relationship("EmergencyEvent", back_populates="user_rel", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    iot_devices = relationship("IoTDevice", back_populates="user", cascade="all, delete-orphan")
    health_data = relationship("HealthData", back_populates="user", cascade="all, delete-orphan")
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    weekly_progress = relationship("WeeklyProgress", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    # Fix the relationship warnings by adding overlaps parameter
    caregiver_relationships = relationship(
        "CaregiverRelationship", 
        foreign_keys="CaregiverRelationship.patient_id", 
        back_populates="patient",
        overlaps="caregivers"
    )
    caregiving_relationships = relationship(
        "CaregiverRelationship", 
        foreign_keys="CaregiverRelationship.caregiver_id", 
        back_populates="caregiver",
        overlaps="caregiving_for"
    )

    def generate_patient_id(self):
        """Generate patient ID: username + 5 random digits"""
        base = self.username if self.username else (self.email.split('@')[0] if self.email else "user")
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        return f"{base}{random_digits}"

# Event to set patient_id before insert if it's None
@event.listens_for(User, 'before_insert')
def set_patient_id_before_insert(mapper, connection, target):
    if target.patient_id is None:
        target.patient_id = target.generate_patient_id()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String)
    doctor_id = Column(String, ForeignKey("doctors.doctor_id", ondelete="SET NULL"), nullable=True)
    gender = Column(String)
    age = Column(Integer)
    chronic_conditions = Column(JSONB, default=list)
    family_history = Column(JSONB, default=list)
    weight = Column(Integer)
    height = Column(Integer)
    bmi = Column(Integer, nullable=True)
    blood_pressure = Column(String)
    heart_rate = Column(Integer)
    blood_glucose = Column(Integer)
    daily_habits = Column(JSONB, default=list)
    profile_completed = Column(Boolean, default=False)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    emergency_contact_relationship = Column(String, nullable=True)
    
    user = relationship("User", back_populates="profile")
    assigned_doctor = relationship("Doctor", back_populates="patients")

class UserDevice(Base):
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_type = Column(String)
    device_name = Column(String)
    device_id = Column(String)
    fcm_token = Column(String, nullable=True)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="devices")