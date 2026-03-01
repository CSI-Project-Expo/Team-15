from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import numpy as np
import cv2
import base64

app = Flask(__name__)
CORS(app)

# 🔥 LOAD MODEL ONCE (VERY IMPORTANT)
model = YOLO("yolov8n.pt")

@app.route("/detect", methods=["POST"])
def detect():
    data = request.json["image"]

    # Decode base64 image
    img_bytes = base64.b64decode(data.split(",")[1])
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Run YOLO
    results = model(img)

    detections = []

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]

            detections.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "label": label,
                "confidence": conf
            })

    return jsonify(detections)

if __name__ == "__main__":
    app.run(debug=True)