import cv2
import requests
import time
import numpy as np
from ultralytics import YOLO

# ---------------- CONFIG ----------------
BACKEND_URL = "http://localhost:8000/alert"
ALERT_COOLDOWN = 5  # seconds between same alert type
CONFIDENCE_THRESHOLD = 0.6

# ---------------- LOAD MODEL ----------------
model = YOLO("yolov8n.pt")  # lightweight model

# ---------------- ALERT CONTROL ----------------
last_alert_time = {}

def send_alert_once(alert_type, description):
    current_time = time.time()

    if alert_type not in last_alert_time or \
       current_time - last_alert_time[alert_type] > ALERT_COOLDOWN:

        data = {
            "type": alert_type,
            "camera_id": "CAM_01",
            "description": description
        }

        try:
            requests.post(BACKEND_URL, json=data)
            print(f"🚨 Alert Sent: {alert_type}")
            last_alert_time[alert_type] = current_time
        except Exception as e:
            print("Backend unreachable:", e)

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)
print("🎥 SentinAI YOLO Detector Started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # =========================
    # 🔐 TAMPER DETECTION
    # =========================
    if np.mean(frame) < 10:  # frame almost black
        send_alert_once("tamper", "Camera black screen detected")

    # =========================
    # 🧠 YOLO OBJECT DETECTION
    # =========================
    results = model(frame)

    for result in results:
        for box in result.boxes:
            confidence = float(box.conf[0])

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            class_id = int(box.cls[0])
            label = model.names[class_id].lower()

            # 🔴 Intrusion Detection
            if label == "person":
                send_alert_once("intrusion", "Unauthorized person detected")

            # 🔥 Fire Detection (ONLY if using custom trained model)
            if label == "fire":
                send_alert_once("fire", "Fire detected")

    # Display video
    cv2.imshow("SentinAI YOLO Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()