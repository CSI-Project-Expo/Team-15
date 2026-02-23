import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import VideoFeed from './components/VideoFeed';
import Sidebar from './components/Sidebar';
import useWebSocket from './hooks/useWebSocket';
import { getAlerts, getEvents, getCameras, getSystemStatus } from './services/api';

function App() {
  // State
  const [alerts, setAlerts] = useState([]);
  const [events, setEvents] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [systemStatus, setSystemStatus] = useState('active');

  // WebSocket connection
  const { connected } = useWebSocket(handleWebSocketMessage);

  // Handle WebSocket messages from backend
  function handleWebSocketMessage(message) {
    switch (message.type) {
      case 'INITIAL_STATE':
        // Backend sends initial data when connected
        if (message.data.cameras) setCameras(message.data.cameras);
        if (message.data.alerts) setAlerts(message.data.alerts);
        if (message.data.events) setEvents(message.data.events);
        break;

      case 'NEW_ALERT':
        // Backend sends new alert
        setAlerts(prev => [message.data.alert, ...prev].slice(0, 10));
        setEvents(prev => [message.data.event, ...prev].slice(0, 20));
        break;

      case 'CAMERA_UPDATE':
        // Backend sends camera update
        setCameras(prev =>
          prev.map(cam =>
            cam.id === message.data.id ? message.data : cam
          )
        );
        break;

      case 'ALERTS_CLEARED':
        // Backend cleared all alerts
        setAlerts([]);
        setEvents([]);
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  }

  // Load initial data from backend
  useEffect(() => {
    loadData();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Update system status based on WebSocket
  useEffect(() => {
    setSystemStatus(connected ? 'active' : 'offline');
  }, [connected]);

  async function loadData() {
    try {
      const [alertsData, eventsData, camerasData, statusData] = await Promise.all([
        getAlerts(10),
        getEvents(20),
        getCameras(),
        getSystemStatus()
      ]);

      setAlerts(alertsData);
      setEvents(eventsData);
      setCameras(camerasData);
      
      console.log('✅ Data loaded from backend');
    } catch (error) {
      console.error('❌ Error loading data:', error);
    }
  }

  return (
    <div className="container">
      <Header 
        systemStatus={systemStatus}
        cameraCount={cameras.length}
      />

      <div className="main-layout">
        <VideoFeed />
        <Sidebar 
          alerts={alerts}
          events={events}
          onRefresh={loadData}
        />
      </div>

      <div className="live-indicator">LIVE</div>
    </div>
  );
}

export default App;