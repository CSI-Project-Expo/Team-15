import { useEffect, useRef, useState } from 'react';

const WS_URL = 'ws://localhost:8000/ws';

function useWebSocket(onMessage) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('✅ WebSocket connected to FastAPI backend');
        setConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📨 Received:', message.type);
          if (onMessage) {
            onMessage(message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('❌ WebSocket disconnected - Reconnecting...');
        setConnected(false);
        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnected(false);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnected(false);
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
    }
  };

  const sendMessage = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return { connected, sendMessage };
}

export default useWebSocket;