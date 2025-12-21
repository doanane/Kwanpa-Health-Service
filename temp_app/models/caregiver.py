from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(8), unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    specialization = Column(String)
    hospital = Column(String)
    email = Column(String, nullable=True)  
    is_active = Column(Boolean, default=True)
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
    patients = relationship("UserProfile", back_populates="assigned_doctor", cascade="all, delete-orphan")

class CaregiverRelationship(Base):
    __tablename__ = "caregiver_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))
    relationship_type = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
    caregiver = relationship("User", foreign_keys=[caregiver_id], backref="caregiving_for")
    patient = relationship("User", foreign_keys=[patient_id], backref="caregivers")