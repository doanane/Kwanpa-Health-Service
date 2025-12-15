from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(8), unique=True, index=True)  # 8-digit ID
    hashed_password = Column(String)
    full_name = Column(String)
    specialization = Column(String)
    hospital = Column(String)
    is_active = Column(Boolean, default=True)
    created_by = Column(String)  # Superuser who created this doctor
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    patients = relationship("UserProfile", backref="doctor")

class CaregiverRelationship(Base):
    __tablename__ = "caregiver_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))
    relationship_type = Column(String)  # family, volunteer, professional
    status = Column(String, default="pending")  # pending, active, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    caregiver = relationship("User", foreign_keys=[caregiver_id], back_populates="caregiving_relationships")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="caregiver_relationships")