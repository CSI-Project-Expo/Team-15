import React, { useRef } from 'react';

function VideoFeed() {
  const videoRef = useRef(null);

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file && videoRef.current) {
      const url = URL.createObjectURL(file);
      videoRef.current.src = url;
      videoRef.current.play();
    }
  };

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
        
        <div className="video-container alert" id="mainVideo">
          <video ref={videoRef} autoPlay muted loop>
            <source src="" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <div className="alert-overlay">
            {/* <div className="alert-text">⚠ INTRUSION DETECTED!</div> */}
          </div>
        </div>
        
        <div className="panel-content">
          <input 
            type="file" 
            accept="video/*" 
            onChange={handleVideoUpload}
            style={{ display: 'none' }}
            id="videoUpload"
          />
        </div>
      </div>
    </div>
  );
}

export default VideoFeed;