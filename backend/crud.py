from sqlalchemy.orm import Session
from typing import Optional
from models import Incident, Camera, Event, Recording
import schemas

# ==================== INCIDENT/ALERT CRUD ====================

def create_incident(db: Session, incident: schemas.IncidentCreate):
    """Create new incident/alert"""
    db_incident = Incident(
        type=incident.type,
        camera_id=incident.camera_id,
        description=incident.description,
        severity=incident.severity,
        confidence=incident.confidence
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

def get_all_incidents(db: Session, limit: int = 50):
    """Get all incidents ordered by timestamp descending"""
    return db.query(Incident).order_by(Incident.timestamp.desc()).limit(limit).all()

def get_incident(db: Session, incident_id: int):
    """Get single incident by ID"""
    return db.query(Incident).filter(Incident.id == incident_id).first()

def clear_all_incidents(db: Session):
    """Delete all incidents"""
    db.query(Incident).delete()
    db.commit()
    return True


# ==================== CAMERA CRUD ====================

def create_camera(db: Session, camera: schemas.CameraCreate):
    """Create new camera"""
    db_camera = Camera(
        name=camera.name,
        location=camera.location,
        status=camera.status,
        ip_address=camera.ip_address,
        rtsp_url=camera.rtsp_url
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

def get_all_cameras(db: Session):
    """Get all cameras"""
    return db.query(Camera).all()

def get_camera(db: Session, camera_id: int):
    """Get single camera by ID"""
    return db.query(Camera).filter(Camera.id == camera_id).first()

def update_camera(db: Session, camera_id: int, camera: schemas.CameraUpdate):
    """Update camera"""
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        return None
    
    update_data = camera.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_camera, key, value)
    
    db.commit()
    db.refresh(db_camera)
    return db_camera

def delete_camera(db: Session, camera_id: int):
    """Delete camera"""
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera:
        db.delete(db_camera)
        db.commit()
        return True
    return False


# ==================== EVENT CRUD ====================

def create_event(db: Session, event: schemas.EventCreate):
    """Create new event"""
    db_event = Event(
        type=event.type,
        description=event.description,
        camera_id=event.camera_id,
        severity=event.severity,
        details=event.details
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_all_events(db: Session, limit: int = 50):
    """Get all events ordered by timestamp descending"""
    return db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()

def get_event(db: Session, event_id: int):
    """Get single event by ID"""
    return db.query(Event).filter(Event.id == event_id).first()

def clear_all_events(db: Session):
    """Delete all events"""
    db.query(Event).delete()
    db.commit()
    return True


# ==================== RECORDING CRUD ====================

def create_recording(db: Session, recording: schemas.RecordingCreate):
    """Create new recording"""
    db_recording = Recording(
        camera_id=recording.camera_id,
        filename=recording.filename,
        filepath=recording.filepath,
        start_time=recording.start_time,
        duration=recording.duration,
        file_size=recording.file_size
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording

def get_all_recordings(db: Session, camera_id: Optional[int] = None, limit: int = 50):
    """Get all recordings, optionally filtered by camera"""
    query = db.query(Recording)
    if camera_id is not None:  # Also add explicit None check here
        query = query.filter(Recording.camera_id == camera_id)
    return query.order_by(Recording.start_time.desc()).limit(limit).all()

def get_recording(db: Session, recording_id: int):
    """Get single recording by ID"""
    return db.query(Recording).filter(Recording.id == recording_id).first()

def delete_recording(db: Session, recording_id: int):
    """Delete recording"""
    db_recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if db_recording:
        db.delete(db_recording)
        db.commit()
        return True
    return False
