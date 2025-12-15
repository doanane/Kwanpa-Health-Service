from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    apple_id = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    health_data = relationship("HealthData", back_populates="user", cascade="all, delete-orphan")
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    weekly_progress = relationship("WeeklyProgress", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    salt = Column(String, nullable=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String)
    caregiver_id = Column(String, nullable=True)
    doctor_id = Column(String, nullable=True)
    gender = Column(String)
    age = Column(Integer)
    chronic_conditions = Column(JSONB, default=list)
    family_history = Column(JSONB, default=list)
    weight = Column(Integer)
    height = Column(Integer)
    bmi = Column(Integer)
    blood_pressure = Column(String)
    heart_rate = Column(Integer)
    blood_glucose = Column(Integer)
    daily_habits = Column(JSONB, default=list)
    
    user = relationship("User", back_populates="profile")

class UserDevice(Base):
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_type = Column(String)
    device_name = Column(String)
    device_id = Column(String)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="devices")