from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn
import os
import asyncio
from datetime import datetime
import cv2
from ultralytics import YOLO

from database import Base, engine, SessionLocal
import schemas, crud
from alerts import trigger_alert

# =====================================================
# APP INIT
# =====================================================

app = FastAPI(title="SentinAI Security Backend", version="3.0.0")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= FOLDERS =================
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/snapshots", exist_ok=True)

if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

Base.metadata.create_all(bind=engine)

# =====================================================
# WEBSOCKET MANAGER
# =====================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("✅ Client connected")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print("❌ Client disconnected")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# =====================================================
# LOAD YOLO MODEL
# =====================================================

print("🚀 Loading YOLOv8 model...")
try:
    model = YOLO("yolov8n.pt")
    print("✅ YOLOv8 model loaded successfully")
except Exception as e:
    print("❌ YOLO failed to load:", e)
    model = None

# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():
    return {
        "message": "SentinAI Backend Running",
        "ai_model": "YOLOv8",
        "status": "active"
    }

# =====================================================
# YOLO CAMERA LOOP
# =====================================================

async def yolo_camera_loop():
    if model is None:
        print("⚠ YOLO not loaded. Skipping AI detection.")
        return

    print("🎥 Starting webcam detection...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Could not open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            await asyncio.sleep(0.1)
            continue

        results = model(frame)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                confidence = float(box.conf[0])
                label = model.names[cls]

                # Only detect person (for intrusion demo)
                if label == "person" and confidence > 0.6:
                    print(f"🚨 PERSON DETECTED ({confidence:.2f})")

                    # Save snapshot
                    filename = f"{datetime.now().timestamp()}.jpg"
                    filepath = f"uploads/snapshots/{filename}"
                    cv2.imwrite(filepath, frame)

                    # Save to DB
                    db = SessionLocal()
                    incident = schemas.IncidentCreate(
                        type="intrusion",
                        camera_id="1",
                        description=f"Person detected ({confidence:.0%})",
                        severity="high",
                        confidence=confidence
                    )
                    crud.create_incident(db, incident)
                    db.close()

                    # Broadcast to frontend
                    await manager.broadcast({
                        "type": "AI_DETECTION",
                        "data": {
                            "label": label,
                            "confidence": confidence,
                            "snapshot": f"/uploads/snapshots/{filename}"
                        }
                    })

                    trigger_alert("intrusion")

        await asyncio.sleep(0.2)  # prevent CPU overload

# =====================================================
# STARTUP EVENT
# =====================================================

@app.on_event("startup")
async def startup_event():
    print("✅ Backend started with AI detection")
    asyncio.create_task(yolo_camera_loop())

# =====================================================
# WEBSOCKET
# =====================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════╗
    ║   SentinAI AI Detection Server    ║
    ╚════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)