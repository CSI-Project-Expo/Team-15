import cv2
import requests
import time
import numpy as np
from ultralytics import YOLO

# ---------------- CONFIG ----------------
BACKEND_URL = "http://localhost:8000/alert"
ALERT_COOLDOWN = 5
CONFIDENCE_THRESHOLD = 0.25  # lowered for better detection

# ---------------- LOAD MODEL ----------------
# Uses YOUR trained fire model; falls back to base model if not found
import os
if os.path.exists("fire.pt"):
    model = YOLO("fire.pt")
    print("✅ Loaded YOUR trained fire detection model")
else:
    model = YOLO("yolov8n.pt")
    print("⚠️  best.pt not found — using base model (no fire detection)")

print(f"📋 Model classes: {model.names}")

# ---------------- ALERT CONTROL ----------------
last_alert_time = {}

def send_alert_once(alert_type, description):
    current_time = time.time()
    if alert_type not in last_alert_time or \
       current_time - last_alert_time[alert_type] > ALERT_COOLDOWN:
        data = {
            "type": alert_type,
            "camera_id": "CAM_01",
            "description": description,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            requests.post(BACKEND_URL, json=data, timeout=2)
            print(f"🚨 Alert Sent: [{alert_type}] {description}")
        except Exception:
            # Backend offline — just log locally
            print(f"🚨 LOCAL ALERT: [{alert_type}] {description}")
        last_alert_time[alert_type] = current_time

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("❌ Could not open webcam!")
    exit()

print("🎥 SentinAI YOLO Detector Started — Press Q to quit\n")

frame_count = 0
skip_frames = 2  # process every 2nd frame for speed
annotated = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # =========================
    # 🔐 TAMPER DETECTION
    # =========================
    mean_brightness = np.mean(frame)
    if mean_brightness < 10:
        send_alert_once("tamper", "Camera black screen detected")
        cv2.putText(frame, "⚠ TAMPER DETECTED", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    # =========================
    # 🧠 YOLO DETECTION (every Nth frame)
    # =========================
    if frame_count % skip_frames == 0:
        results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        annotated = results[0].plot()

        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = model.names[class_id].lower()

                # 🔴 Intrusion
                if label == "person":
                    send_alert_once("intrusion",
                        f"Person detected ({confidence:.0%} confidence)")

                # 🔥 Fire
                if label == "fire":
                    send_alert_once("fire",
                        f"Fire detected ({confidence:.0%} confidence)")

                # 💨 Smoke
                if label == "smoke":
                    send_alert_once("smoke",
                        f"Smoke detected ({confidence:.0%} confidence)")

    # Show annotated frame (or raw if not yet processed)
    display = annotated if annotated is not None else frame

    # Status overlay
    status = f"Frames: {frame_count} | Brightness: {mean_brightness:.0f}"
    cv2.putText(display, status, (10, display.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    cv2.imshow("SentinAI YOLO Feed", display)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("\n✅ SentinAI stopped.")