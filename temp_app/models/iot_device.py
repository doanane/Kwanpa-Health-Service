from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class IoTDevice(Base):
    __tablename__ = "iot_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String, unique=True)  
    device_type = Column(String)  
    device_name = Column(String)
    manufacturer = Column(String)
    model = Column(String)
    connection_status = Column(String)  
    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="iot_devices")
    vital_readings = relationship("VitalReading", back_populates="device")

class VitalReading(Base):
    __tablename__ = "vital_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("iot_devices.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate = Column(Integer)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    blood_oxygen = Column(Float)
    temperature = Column(Float)
    glucose_level = Column(Float)
    movement = Column(Integer)  
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_emergency = Column(Boolean, default=False)
    
    device = relationship("IoTDevice", back_populates="vital_readings")
    user = relationship("User")