import React, { useRef, useEffect, useState } from "react";

function VideoFeed() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [detections, setDetections] = useState([]);

  // Start webcam automatically
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
      })
      .catch(err => console.error(err));
  }, []);

  // Send frame to backend
  const detectFrame = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (!video.videoWidth) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame
    ctx.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL("image/jpeg");

    try {
      const response = await fetch("http://127.0.0.1:5000/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imageData })
      });

      const data = await response.json();
      setDetections(data);

      drawBoxes(data);

    } catch (error) {
      console.error("Detection error:", error);
    }
  };

  // Draw bounding boxes
  const drawBoxes = (detections) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.lineWidth = 3;
    ctx.strokeStyle = "red";
    ctx.fillStyle = "red";
    ctx.font = "18px Arial";

    detections.forEach(det => {
      const width = det.x2 - det.x1;
      const height = det.y2 - det.y1;

      ctx.strokeRect(det.x1, det.y1, width, height);
      ctx.fillText(det.label, det.x1, det.y1 - 5);
    });
  };

  // Run detection every second
  useEffect(() => {
    const interval = setInterval(() => {
      detectFrame();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="video-section">
      <div className="camera-feed">
        <div className="camera-header">
          <span className="camera-title">Camera 01 - Entrance</span>
          <div className="live-badge">
            <div className="live-dot"></div>
            LIVE
          </div>
        </div>

        <div className="video-container alert" style={{ position: "relative" }}>
          
          <video
            ref={videoRef}
            autoPlay
            muted
            style={{ width: "100%" }}
          />

          {/* Overlay Canvas */}
          <canvas
            ref={canvasRef}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              pointerEvents: "none"
            }}
          />

          {detections.length > 0 && (
            <div className="alert-overlay">
              <div className="alert-text">⚠ INTRUSION DETECTED!</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default VideoFeed;