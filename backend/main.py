from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import os
from datetime import datetime
import json
import asyncio

from database import Base, engine, SessionLocal
import models, schemas, crud
from alerts import trigger_alert

app = FastAPI(title="SentinAI Security Backend", version="2.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/snapshots", exist_ok=True)

# Serve static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Create database tables
Base.metadata.create_all(bind=engine)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"❌ Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== ROUTES ====================

@app.get("/")
def root():
    return {
        "message": "SentinAI Backend is running",
        "version": "2.0.0",
        "status": "active",
        "features": ["WebSocket", "AI Detection", "Video Upload", "Real-time Alerts"]
    }

# ==================== CAMERA ROUTES ====================

@app.get("/api/cameras", response_model=List[schemas.Camera])
def get_cameras(db: Session = Depends(get_db)):
    """Get all cameras"""
    return crud.get_all_cameras(db)

@app.get("/api/cameras/{camera_id}", response_model=schemas.Camera)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """Get single camera by ID"""
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@app.post("/api/cameras", response_model=schemas.Camera)
def create_camera(camera: schemas.CameraCreate, db: Session = Depends(get_db)):
    """Create new camera"""
    return crud.create_camera(db, camera)

@app.put("/api/cameras/{camera_id}", response_model=schemas.Camera)
async def update_camera(
    camera_id: int, 
    camera: schemas.CameraUpdate, 
    db: Session = Depends(get_db)
):
    """Update camera"""
    updated = crud.update_camera(db, camera_id, camera)
    if not updated:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Broadcast camera update
    await manager.broadcast({
        "type": "CAMERA_UPDATE",
        "data": schemas.Camera.from_orm(updated).dict()
    })
    
    return updated

# ==================== ALERT/INCIDENT ROUTES ====================

@app.post("/api/alerts")
async def create_alert(
    incident: schemas.IncidentCreate,
    db: Session = Depends(get_db)
):
    """Create new alert/incident"""
    # Save to database
    saved = crud.create_incident(db, incident)
    
    # Trigger alert notification
    trigger_alert(incident.type)
    
    # Create event
    event = crud.create_event(db, schemas.EventCreate(
        type=incident.type,
        description=incident.description,
        camera_id=incident.camera_id,
        severity=incident.severity
    ))
    
    # Prepare response data
    alert_data = schemas.Incident.from_orm(saved).dict()
    event_data = schemas.Event.from_orm(event).dict()
    
    # Broadcast to all WebSocket clients
    await manager.broadcast({
        "type": "NEW_ALERT",
        "data": {
            "alert": alert_data,
            "event": event_data
        }
    })
    
    return {
        "status": "Alert received",
        "incident_id": saved.id,
        "alert": alert_data,
        "event": event_data
    }

@app.get("/api/alerts", response_model=List[schemas.Incident])
def get_alerts(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all alerts/incidents"""
    return crud.get_all_incidents(db, limit)

@app.delete("/api/alerts")
async def clear_alerts(db: Session = Depends(get_db)):
    """Clear all alerts"""
    crud.clear_all_incidents(db)
    crud.clear_all_events(db)
    
    # Broadcast to clients
    await manager.broadcast({
        "type": "ALERTS_CLEARED"
    })
    
    return {"status": "success", "message": "All alerts cleared"}

# ==================== EVENT ROUTES ====================

@app.get("/api/events", response_model=List[schemas.Event])
def get_events(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all events"""
    return crud.get_all_events(db, limit)

# ==================== DETECTION ROUTES ====================

@app.post("/api/detect")
async def detect_objects(
    detection: schemas.DetectionRequest,
    db: Session = Depends(get_db)
):
    """AI Detection endpoint"""
    # Simulate AI detection (replace with real AI model)
    import random
    
    has_detection = random.random() > 0.7
    
    if has_detection:
        detection_types = [
            {"type": "person", "confidence": 0.95},
            {"type": "vehicle", "confidence": 0.88},
            {"type": "unknown", "confidence": 0.65}
        ]
        
        detected = random.choice(detection_types)
        
        # Create alert if confidence is high
        if detected["confidence"] > 0.85:
            severity = "high" if detected["confidence"] > 0.9 else "medium"
            
            incident = schemas.IncidentCreate(
                type="intrusion" if detected["type"] == "person" else "motion",
                camera_id=detection.camera_id,
                description=f"{detected['type']} detected with {detected['confidence']:.0%} confidence",
                severity=severity,
                confidence=detected["confidence"]
            )
            
            # Create alert
            await create_alert(incident, db)
        
        return {
            "detected": True,
            "detections": [detected]
        }
    
    return {"detected": False, "detections": []}

# ==================== VIDEO UPLOAD ====================

@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file"""
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are allowed")
    
    # Save file
    filename = f"{datetime.now().timestamp()}_{file.filename}"
    filepath = os.path.join("uploads/videos", filename)
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {
        "success": True,
        "filename": filename,
        "url": f"/uploads/videos/{filename}",
        "size": len(content)
    }

# ==================== SYSTEM STATUS ====================

@app.get("/api/status")
def get_status(db: Session = Depends(get_db)):
    """Get system status"""
    cameras = crud.get_all_cameras(db)
    incidents = crud.get_all_incidents(db, limit=1000)
    
    # Count incidents in last 24 hours
    from datetime import timedelta
    day_ago = datetime.utcnow() - timedelta(days=1)
    
    # Use list() to ensure we have actual objects, not query results
    cameras_list = list(cameras)
    incidents_list = list(incidents)
    
    # Count recent incidents
    recent_count = sum(
        1 for incident in incidents_list 
        if getattr(incident, 'timestamp', datetime.min) > day_ago
    )
    
    # Count cameras by status
    active_count = sum(1 for camera in cameras_list if str(camera.status) == "active")
    inactive_count = sum(1 for camera in cameras_list if str(camera.status) == "inactive")
    
    return {
        "status": "active",
        "aiModel": "running",
        "cameras": {
            "total": len(cameras_list),
            "active": active_count,
            "inactive": inactive_count
        },
        "alerts": {
            "total": len(incidents_list),
            "last24h": recent_count
        },
        "websocket_connections": len(manager.active_connections)
    }

# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        cameras = crud.get_all_cameras(db)
        incidents = crud.get_all_incidents(db, limit=10)
        events = crud.get_all_events(db, limit=20)
        
        await websocket.send_json({
            "type": "INITIAL_STATE",
            "data": {
                "cameras": [schemas.Camera.from_orm(c).dict() for c in cameras],
                "alerts": [schemas.Incident.from_orm(i).dict() for i in incidents],
                "events": [schemas.Event.from_orm(e).dict() for e in events]
            }
        })
        
        # Keep connection alive
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            # Echo back or handle client messages
            await websocket.send_text(f"Message received: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ==================== DEMO DATA GENERATOR ====================

async def generate_demo_data():
    """Generate demo incidents every 30 seconds"""
    while True:
        await asyncio.sleep(30)
        
        try:
            db = SessionLocal()
            
            import random
            incident_types = [
                {"type": "motion", "description": "Motion Detected", "severity": "low"},
                {"type": "intrusion", "description": "Intrusion Detected", "severity": "high"},
                {"type": "suspicious", "description": "Suspicious Activity", "severity": "medium"},
                {"type": "system", "description": "System Check", "severity": "normal"}
            ]
            
            cameras = crud.get_all_cameras(db)
            if not cameras:
                # Create default cameras if none exist
                for i in range(1, 4):
                    crud.create_camera(db, schemas.CameraCreate(
                        name=f"Camera {i:02d}",
                        location=f"Location {i}",
                        status="active"
                    ))
                cameras = crud.get_all_cameras(db)
            
            random_incident = random.choice(incident_types)
            random_camera = random.choice(cameras)
            
            incident = schemas.IncidentCreate(
                type=random_incident["type"],
                camera_id=str(random_camera.id),
                description=random_incident["description"],
                severity=random_incident["severity"],
                confidence=random.random() * 0.3 + 0.7
            )
            
            # Create alert without awaiting (since this is background task)
            saved = crud.create_incident(db, incident)
            event = crud.create_event(db, schemas.EventCreate(
                type=incident.type,
                description=incident.description,
                camera_id=incident.camera_id,
                severity=incident.severity
            ))
            
            # Broadcast
            asyncio.create_task(manager.broadcast({
                "type": "NEW_ALERT",
                "data": {
                    "alert": schemas.Incident.from_orm(saved).dict(),
                    "event": schemas.Event.from_orm(event).dict()
                }
            }))
            
            print(f"📊 Generated demo incident: {random_incident['description']}")
            
            db.close()
            
        except Exception as e:
            print(f"Error generating demo data: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Create default cameras if none exist
    db = SessionLocal()
    cameras = crud.get_all_cameras(db)
    if not cameras:
        default_cameras = [
            {"name": "Camera 01 - Entrance", "location": "Main Entrance"},
            {"name": "Camera 02 - Parking", "location": "Parking Lot"},
            {"name": "Camera 03 - Back Exit", "location": "Rear Exit"}
        ]
        for cam in default_cameras:
            crud.create_camera(db, schemas.CameraCreate(**cam, status="active"))
        print("✅ Default cameras created")
    db.close()
    
    # Start demo data generator (comment out in production)
    asyncio.create_task(generate_demo_data())
    print("✅ Demo data generator started")

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║   SentinAI Backend Server Starting    ║
    ║   FastAPI + WebSocket + SQLite        ║
    ╚════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
