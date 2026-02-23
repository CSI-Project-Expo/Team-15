import React, { useState, useEffect } from 'react';

function Header({ systemStatus, cameraCount }) {
  const [showWifiPopup, setShowWifiPopup] = useState(false);
  const [wifiDetails, setWifiDetails] = useState('');

  const updateNetworkStatus = () => {
    if (!navigator.onLine) {
      setWifiDetails("<span style='color:red'>Offline</span>");
      return;
    }

    const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const type = conn?.effectiveType || "unknown";
    const speed = conn?.downlink || "N/A";
    const rtt = conn?.rtt || "N/A";

    const getSignalQuality = (downlink) => {
      if (downlink >= 10) return "Excellent 📶📶📶📶";
      if (downlink >= 5) return "Good 📶📶📶";
      if (downlink >= 1) return "Fair 📶📶";
      return "Poor 📶";
    };

    setWifiDetails(`
      <div><strong>Network:</strong> Wi-Fi</div>
      <div><strong>Quality:</strong> ${getSignalQuality(speed)}</div>
      <div><strong>Speed:</strong> ${speed} Mbps</div>
      <div><strong>Latency:</strong> ${rtt} ms</div>
      <div><strong>Type:</strong> ${type}</div>
    `);
  };

  useEffect(() => {
    updateNetworkStatus();
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    
    return () => {
      window.removeEventListener('online', updateNetworkStatus);
      window.removeEventListener('offline', updateNetworkStatus);
    };
  }, []);

  return (
    <header>
      <div className="logo">
        SentinAI <span>Dashboard</span>
        <small style={{ fontSize: '0.5rem', display: 'block', color: 'var(--accent-success)', letterSpacing: '1px' }}>
          React + Python FastAPI
        </small>
      </div>

      <div className="status-bar">
        <div className="status-item">
          <span>System Status:</span>
          <div className={`status-indicator ${systemStatus === 'active' ? 'active' : ''}`}></div>
          <strong style={{ color: systemStatus === 'active' ? 'var(--accent-success)' : 'var(--accent-danger)' }}>
            {systemStatus.toUpperCase()}
          </strong>
        </div>
        <div className="status-item">
          <span>AI Model: <strong>Running</strong></span>
        </div>
        <div className="status-item">
          <span>Cameras: <strong>{cameraCount} Connected</strong></span>
        </div>
      </div>

      <div className="header-icons">
        <div 
          className={`wifi-popup ${showWifiPopup ? '' : 'hidden'}`}
        >
          <strong>Network Status</strong>
          <div dangerouslySetInnerHTML={{ __html: wifiDetails }} />
        </div>

        <button 
          className="icon-btn" 
          onClick={() => setShowWifiPopup(!showWifiPopup)}
          title="Network Status"
        >
          📶
        </button>
        <button className="icon-btn" title="Menu">☰</button>
      </div>
    </header>
  );
}

export default Header;