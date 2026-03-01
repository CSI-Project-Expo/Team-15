from utils.video_stream import VideoStream
from modules.yolo_detector import YOLODetector
from modules.gesture_detector import GestureDetector
from modules.decision_engine import DecisionEngine
import cv2

stream = VideoStream(0)
yolo = YOLODetector("models/yolov8n.pt")
gesture = GestureDetector()
engine = DecisionEngine()

while True:
    ret, frame = stream.read()
    if not ret:
        break

    detections = yolo.detect(frame)
    sos = gesture.detect_sos(frame)
    alerts = engine.analyze(detections, sos)

    y = 40
    for alert in alerts:
        cv2.putText(frame, alert, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        y += 40

    cv2.imshow("SentinAI AI Module", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()
