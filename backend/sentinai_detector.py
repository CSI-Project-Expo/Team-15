import cv2
import requests
import time
import os
from ultralytics import YOLO

# =============================
# CONFIG
# =============================
BACKEND_URL = "http://localhost:8000/api/fire/alert"
ALERT_COOLDOWN = 5
CONFIDENCE = 0.25
CAMERA_ID = "CAM_01"

# =============================
# LOAD MODEL
# =============================
if os.path.exists("fire.pt"):
    model = YOLO("fire.pt")
    print("✅ Loaded fire.pt")
else:
    model = YOLO("yolov8n.pt")
    print("⚠ Using yolov8n.pt")

print("Model classes:", model.names)

# =============================
# ALERT CONTROL
# =============================
last_alert = {}

def send_alert(alert_type, description):
    now = time.time()

    if alert_type not in last_alert or now - last_alert[alert_type] > ALERT_COOLDOWN:
        payload = {
            "type": alert_type,
            "camera_id": CAMERA_ID,
            "description": description,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            requests.post(BACKEND_URL, json=payload, timeout=2)
            print("🚨 Alert sent:", alert_type)
        except:
            print("⚠ Backend not reachable")

        last_alert[alert_type] = now

# =============================
# CAMERA
# =============================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not opening")
    exit()

print("🎥 Running... Press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=CONFIDENCE, verbose=False)
    annotated = results[0].plot()

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls].lower()

            if label == "person":
                send_alert("intrusion", "Person detected")

            if label == "fire":
                send_alert("fire", "Fire detected")

            if label == "smoke":
                send_alert("smoke", "Smoke detected")

    cv2.imshow("SentinAI Camera", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()