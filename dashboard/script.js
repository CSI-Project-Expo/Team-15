// ==================== CONFIGURATION ====================
const API_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws';

// ==================== STATE MANAGEMENT ====================
let ws = null;
let webcamStream = null;
let alertTimeout = null;
let reconnectTimeout = null;

// ==================== WEBSOCKET CONNECTION ====================
function connectWebSocket() {
    try {
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            console.log('✅ WebSocket connected to FastAPI backend');
            updateSystemStatus(true);
            if (reconnectTimeout) {
                clearTimeout(reconnectTimeout);
                reconnectTimeout = null;
            }
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        };

        ws.onclose = () => {
            console.log('❌ WebSocket disconnected - Reconnecting...');
            updateSystemStatus(false);
            reconnectTimeout = setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateSystemStatus(false);
        };
    } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        updateSystemStatus(false);
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
    }
}

// ==================== WEBSOCKET MESSAGE HANDLER ====================
function handleWebSocketMessage(message) {
    console.log('📨 Received:', message.type);

    switch (message.type) {
        case 'INITIAL_STATE':
            loadInitialState(message.data);
            break;
        case 'NEW_ALERT':
            addNewAlert(message.data.alert);
            addNewEvent(message.data.event);
            if (message.data.alert.severity === 'critical' || message.data.alert.severity === 'high') {
                triggerAlertAnimation(message.data.alert);
            }
            break;
        case 'CAMERA_UPDATE':
            updateCameraCount(message.data);
            break;
        case 'ALERTS_CLEARED':
            clearAllUI();
            break;
    }
}

// ==================== INITIAL STATE LOADING ====================
function loadInitialState(data) {
    console.log('📊 Loading initial state...');
    
    if (data.cameras && data.cameras.length > 0) {
        updateCameraCount({ count: data.cameras.length });
    }

    // Load alerts
    const alertsContainer = document.querySelector('.panel-content');
    if (data.alerts && data.alerts.length > 0) {
        alertsContainer.innerHTML = '';
        data.alerts.forEach(alert => addNewAlert(alert, false));
    }

    // Load events
    const eventsContainer = document.querySelector('.event-scroll');
    if (data.events && data.events.length > 0) {
        eventsContainer.innerHTML = '';
        data.events.forEach(event => addNewEvent(event, false));
    }
}

// ==================== UI UPDATE FUNCTIONS ====================
function updateSystemStatus(active) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-item strong');
    
    if (active) {
        statusIndicator.classList.add('active');
        statusText.textContent = 'ACTIVE';
        statusText.style.color = 'var(--accent-success)';
    } else {
        statusIndicator.classList.remove('active');
        statusText.textContent = 'OFFLINE';
        statusText.style.color = 'var(--accent-danger)';
    }
}

function updateCameraCount(data) {
    const cameraCount = document.getElementById('cameraCount');
    const count = data.count || data.total || 1;
    cameraCount.textContent = `${count} Connected`;
}

// ==================== ALERT FUNCTIONS ====================
function addNewAlert(alert, animate = true) {
    const container = document.querySelector('.panel-content');
    
    // Create alert element
    const alertEl = document.createElement('div');
    alertEl.className = `alert-item ${alert.severity}`;
    if (animate) {
        alertEl.style.animation = 'slideIn 0.3s ease-out';
    }

    const severityClass = getSeverityClass(alert.severity);
    
    alertEl.innerHTML = `
        <div class="alert-icon ${severityClass}"></div>
        <div class="alert-info">
            <div class="alert-type">${alert.description || alert.type}</div>
        </div>
    `;

    // Insert at top
    const firstAlert = container.querySelector('.alert-item');
    if (firstAlert) {
        container.insertBefore(alertEl, firstAlert);
    } else {
        container.appendChild(alertEl);
    }

    // Keep only last 10 alerts
    const alerts = container.querySelectorAll('.alert-item');
    if (alerts.length > 10) {
        alerts[alerts.length - 1].remove();
    }
}

function getSeverityClass(severity) {
    const map = {
        'critical': 'danger',
        'high': 'danger',
        'medium': 'warning',
        'low': 'caution',
        'normal': 'normal'
    };
    return map[severity] || 'normal';
}

// ==================== EVENT FUNCTIONS ====================
function addNewEvent(event, animate = true) {
    const container = document.querySelector('.event-scroll');
    
    const eventEl = document.createElement('div');
    eventEl.className = 'event-item';
    if (animate) {
        eventEl.style.animation = 'slideIn 0.3s ease-out';
    }

    const severityClass = getSeverityClass(event.severity);
    const iconColor = {
        'danger': 'var(--accent-danger)',
        'warning': 'var(--accent-warning)',
        'caution': 'var(--accent-caution)',
        'normal': 'var(--accent-success)'
    }[severityClass];

    eventEl.innerHTML = `
        <div class="event-icon" style="background: ${iconColor};"></div>
        <div class="event-details">
            <div class="event-description">${event.description || event.type}</div>
        </div>
        <div class="event-severity severity-${event.severity}">${event.severity.toUpperCase()}</div>
    `;

    // Insert at top
    const firstEvent = container.querySelector('.event-item');
    if (firstEvent) {
        container.insertBefore(eventEl, firstEvent);
    } else {
        container.appendChild(eventEl);
    }

    // Keep only last 20 events
    const events = container.querySelectorAll('.event-item');
    if (events.length > 20) {
        events[events.length - 1].remove();
    }
}

// ==================== ALERT ANIMATION ====================
function triggerAlertAnimation(alert) {
    const videoContainer = document.getElementById('mainVideo');
    
    // Add alert class
    videoContainer.classList.add('alert');
    
    // Create alert overlay if it doesn't exist
    let overlay = videoContainer.querySelector('.alert-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'alert-overlay';
        overlay.innerHTML = '<div class="alert-text"></div>';
        videoContainer.appendChild(overlay);
    }
    
    const alertText = overlay.querySelector('.alert-text');
    alertText.textContent = `⚠ ${alert.description.toUpperCase()}!`;

    // Remove alert after 5 seconds
    if (alertTimeout) clearTimeout(alertTimeout);
    alertTimeout = setTimeout(() => {
        videoContainer.classList.remove('alert');
    }, 5000);
}

// ==================== PANEL TOGGLE ====================
function togglePanel(header) {
    const panel = header.parentElement;
    panel.classList.toggle('collapsed');
}

// ==================== NETWORK STATUS ====================
const wifiBtn = document.getElementById("wifiBtn");
const wifiPopup = document.getElementById("wifiPopup");
const wifiDetails = document.getElementById("wifiDetails");

function getSignalQuality(downlink) {
    if (downlink >= 10) return "Excellent 📶📶📶📶";
    if (downlink >= 5) return "Good 📶📶📶";
    if (downlink >= 1) return "Fair 📶📶";
    return "Poor 📶";
}

function updateNetworkStatus() {
    if (!navigator.onLine) {
        wifiBtn.textContent = "❌";
        wifiBtn.title = "Disconnected";
        wifiDetails.innerHTML = "<span style='color:red'>Offline</span>";
        return;
    }

    const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const type = conn?.effectiveType || "unknown";
    const speed = conn?.downlink || "N/A";
    const rtt = conn?.rtt || "N/A";

    wifiBtn.textContent = "📶";
    wifiBtn.title = "Connected";

    wifiDetails.innerHTML = `
        <div><strong>Network:</strong> Wi-Fi</div>
        <div><strong>Quality:</strong> ${getSignalQuality(speed)}</div>
        <div><strong>Speed:</strong> ${speed} Mbps</div>
        <div><strong>Latency:</strong> ${rtt} ms</div>
        <div><strong>Type:</strong> ${type}</div>
    `;
}

wifiBtn.addEventListener("click", () => {
    wifiPopup.classList.toggle("hidden");
    updateNetworkStatus();
});

window.addEventListener("online", updateNetworkStatus);
window.addEventListener("offline", updateNetworkStatus);

// ==================== VIDEO FUNCTIONS ====================
async function startWebcam() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 1920, height: 1080 } 
        });
        const videoElement = document.getElementById('mainVideoElement');
        videoElement.srcObject = webcamStream;
        videoElement.play();
        console.log('✅ Webcam started');
    } catch (error) {
        console.error('Webcam error:', error);
        alert('Error accessing webcam: ' + error.message);
    }
}

function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        document.getElementById('mainVideoElement').srcObject = null;
        webcamStream = null;
        console.log('⏹ Webcam stopped');
    }
}

async function uploadVideo(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/upload/video`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (result.success) {
            const videoElement = document.getElementById('mainVideoElement');
            videoElement.src = `http://localhost:8000${result.url}`;
            videoElement.play();
            console.log('✅ Video uploaded successfully');
            return true;
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload video');
        return false;
    }
}

// ==================== API FUNCTIONS ====================
async function testAlert() {
    try {
        await fetch(`${API_URL}/alerts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'intrusion',
                camera_id: '1',
                description: 'Test Alert - Person Detected',
                severity: 'high',
                confidence: 0.95
            })
        });
        console.log('🚨 Test alert sent');
    } catch (error) {
        console.error('Test alert error:', error);
    }
}

async function clearAllAlerts() {
    if (confirm('Clear all alerts and events?')) {
        try {
            await fetch(`${API_URL}/alerts`, { method: 'DELETE' });
            console.log('🗑️ All alerts cleared');
        } catch (error) {
            console.error('Clear error:', error);
        }
    }
}

function clearAllUI() {
    // Clear alerts
    const alertsContainer = document.querySelector('.panel-content');
    alertsContainer.innerHTML = `
        <div class="alert-item normal">
            <div class="alert-icon normal"></div>
            <div class="alert-info">
                <div class="alert-type">No alerts - System monitoring...</div>
            </div>
        </div>
    `;

    // Clear events
    const eventsContainer = document.querySelector('.event-scroll');
    eventsContainer.innerHTML = `
        <div class="event-item">
            <div class="event-icon" style="background: var(--accent-success);"></div>
            <div class="event-details">
                <div class="event-description">No events recorded</div>
            </div>
            <div class="event-severity severity-normal">NORMAL</div>
        </div>
    `;
}

async function refreshData() {
    try {
        const [alertsRes, eventsRes, statusRes] = await Promise.all([
            fetch(`${API_URL}/alerts?limit=10`),
            fetch(`${API_URL}/events?limit=20`),
            fetch(`${API_URL}/status`)
        ]);

        const alerts = await alertsRes.json();
        const events = await eventsRes.json();
        const status = await statusRes.json();

        // Update alerts
        const alertsContainer = document.querySelector('.panel-content');
        alertsContainer.innerHTML = '';
        if (alerts.length > 0) {
            alerts.forEach(alert => addNewAlert(alert, false));
        }

        // Update events
        const eventsContainer = document.querySelector('.event-scroll');
        eventsContainer.innerHTML = '';
        if (events.length > 0) {
            events.forEach(event => addNewEvent(event, false));
        }

        // Update camera count
        if (status.cameras) {
            updateCameraCount({ count: status.cameras.total });
        }

        console.log('🔄 Data refreshed');
    } catch (error) {
        console.error('Refresh error:', error);
    }
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', (e) => {
    // Ctrl+R: Refresh data
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        refreshData();
    }
    
    // Ctrl+T: Test alert
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        testAlert();
    }
    
    // Ctrl+D: Clear alerts
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        clearAllAlerts();
    }
});

// ==================== INITIALIZATION ====================
function initialize() {
    console.log('🚀 SentinAI Dashboard Initializing...');
    console.log('📡 Connecting to:', API_URL);
    console.log('🔌 WebSocket:', WS_URL);
    
    // Connect WebSocket
    connectWebSocket();
    
    // Update network status
    updateNetworkStatus();
    
    // Load initial data via REST API
    refreshData();
    
    // Set up periodic refresh (every 30 seconds)
    setInterval(refreshData, 30000);
    
    console.log('✅ Dashboard initialized');
    console.log('💡 Keyboard shortcuts:');
    console.log('   Ctrl+R: Refresh data');
    console.log('   Ctrl+T: Test alert');
    console.log('   Ctrl+D: Clear alerts');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// ==================== GLOBAL FUNCTIONS (for HTML onclick) ====================
window.togglePanel = togglePanel;
window.startWebcam = startWebcam;
window.stopWebcam = stopWebcam;
window.testAlert = testAlert;
window.clearAllAlerts = clearAllAlerts;
window.refreshData = refreshData;
window.uploadVideo = uploadVideo;
