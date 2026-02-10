from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ==================== INCIDENT/ALERT SCHEMAS ====================

class IncidentCreate(BaseModel):
    type: str           # fire, accident, sos, tamper, intrusion, motion, suspicious
    camera_id: str
    description: str
    severity: str = "medium"  # critical, high, medium, low, normal
    confidence: Optional[float] = None

class Incident(BaseModel):
    id: int
    type: str
    camera_id: str
    description: str
    severity: str
    confidence: Optional[float] = None
    timestamp: datetime
    acknowledged: int
    metadata_json: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


# ==================== CAMERA SCHEMAS ====================

class CameraCreate(BaseModel):
    name: str
    location: str
    status: str = "active"
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None

class Camera(BaseModel):
    id: int
    name: str
    location: str
    status: str
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    created_at: datetime
    last_ping: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


# ==================== EVENT SCHEMAS ====================

class EventCreate(BaseModel):
    type: str
    description: str
    camera_id: Optional[str] = None
    severity: str = "normal"
    details: Optional[str] = None

class Event(BaseModel):
    id: int
    type: str
    description: str
    camera_id: Optional[str] = None
    severity: str
    timestamp: datetime
    details: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


# ==================== DETECTION SCHEMAS ====================

class DetectionRequest(BaseModel):
    camera_id: str
    frame: Optional[str] = None  # Base64 encoded frame


class DetectionResponse(BaseModel):
    detected: bool
    detections: list


# ==================== RECORDING SCHEMAS ====================

class RecordingCreate(BaseModel):
    camera_id: int
    filename: str
    filepath: str
    start_time: datetime
    duration: Optional[int] = None
    file_size: Optional[int] = None

class Recording(BaseModel):
    id: int
    camera_id: int
    filename: str
    filepath: str
    duration: Optional[int]
    file_size: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    thumbnail: Optional[str]
    has_alerts: int

    class Config:
        orm_mode = True
        from_attributes = True
