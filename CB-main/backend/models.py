from sqlalchemy import Column, Integer, String, DateTime, Float
from database import Base
from datetime import datetime

class Incident(Base):
    """Incident/Alert model"""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)  # fire, accident, sos, tamper, intrusion, motion, suspicious
    camera_id = Column(String, index=True)
    description = Column(String)
    severity = Column(String, default="medium")  # critical, high, medium, low, normal
    confidence = Column(Float, nullable=True)  # AI confidence score
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged = Column(Integer, default=0)  # 0 = false, 1 = true
    metadata_json = Column(String, nullable=True)  # JSON string for additional data


class Camera(Base):
    """Camera model"""
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    status = Column(String, default="active")  # active, inactive, maintenance
    ip_address = Column(String, nullable=True)
    rtsp_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_ping = Column(DateTime, nullable=True)


class Event(Base):
    """Event log model"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    description = Column(String)
    camera_id = Column(String, index=True, nullable=True)
    severity = Column(String, default="normal")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(String, nullable=True)  # JSON string


class Recording(Base):
    """Video recording model"""
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, index=True)
    filename = Column(String)
    filepath = Column(String)
    duration = Column(Integer, nullable=True)  # seconds
    file_size = Column(Integer, nullable=True)  # bytes
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    thumbnail = Column(String, nullable=True)
    has_alerts = Column(Integer, default=0)
