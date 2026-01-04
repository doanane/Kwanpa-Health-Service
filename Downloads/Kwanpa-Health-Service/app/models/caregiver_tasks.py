from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CaregiverTask(Base):
    __tablename__ = "caregiver_tasks"

    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String, default="general")
    priority = Column(String, default=TaskPriority.MEDIUM)
    status = Column(String, default=TaskStatus.PENDING)
    
    due_date = Column(DateTime(timezone=True), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)
    recurrence_days = Column(JSON, nullable=True)
    
    notes = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    caregiver = relationship("User", foreign_keys=[caregiver_id], backref="assigned_tasks")
    patient = relationship("User", foreign_keys=[patient_id], backref="patient_tasks")

    def is_overdue(self):
        if self.status == TaskStatus.COMPLETED:
            return False
        if self.due_date and self.due_date < datetime.utcnow():
            return True
        return False
    
    def to_dict(self):
        return {
            "id": self.id,
            "caregiver_id": self.caregiver_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "is_overdue": self.is_overdue(),
            "patient_name": self.patient.username if self.patient else "Unknown",
            "created_at": self.created_at
        }