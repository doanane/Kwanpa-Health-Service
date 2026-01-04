from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class AppointmentType(str, enum.Enum):
    CHECKUP = "checkup"
    MEDICATION = "medication"
    THERAPY = "therapy"
    CONSULTATION = "consultation"
    EMERGENCY = "emergency"
    OTHER = "other"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class CaregiverSchedule(Base):
    __tablename__ = "caregiver_schedule"

    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    appointment_type = Column(String, default=AppointmentType.CHECKUP)
    status = Column(String, default=AppointmentStatus.SCHEDULED)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    
    location = Column(String, nullable=True)
    is_virtual = Column(Boolean, default=False)
    meeting_link = Column(String, nullable=True)
    meeting_platform = Column(String, nullable=True)
    
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    other_caregivers = Column(JSON, nullable=True)
    
    participant_notes = Column(Text, nullable=True)
    send_reminder = Column(Boolean, default=True)
    reminder_minutes_before = Column(Integer, default=30)
    
    notes = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    caregiver = relationship("User", foreign_keys=[caregiver_id], backref="schedule_entries")
    patient = relationship("User", foreign_keys=[patient_id], backref="appointments")
    doctor = relationship("Doctor", backref="appointments")

    def get_color(self):
        colors = {
            AppointmentType.CHECKUP: "#3B82F6",
            AppointmentType.MEDICATION: "#F59E0B",
            AppointmentType.THERAPY: "#10B981",
            AppointmentType.CONSULTATION: "#8B5CF6",
            AppointmentType.EMERGENCY: "#EF4444",
            AppointmentType.OTHER: "#6B7280"
        }
        return colors.get(self.appointment_type, "#6B7280")
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "patient_id": self.patient_id,
            "patient_name": self.patient.username if self.patient else "Unknown",
            "appointment_type": self.appointment_type,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "location": self.location,
            "is_virtual": self.is_virtual,
            "created_at": self.created_at
        }