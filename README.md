<<<<<<< HEAD
# SentinAI Security Dashboard - Complete Setup Guide

## 🎯 What You Have

A **complete security monitoring system** with:
- ✅ Beautiful web dashboard (your custom design)
- ✅ Python FastAPI backend with WebSocket
- ✅ SQLite database
- ✅ Real-time alerts and events
- ✅ Video upload support
- ✅ AI detection simulation
- ✅ Network status monitoring

---

## 📁 Project Structure

```
sentinai/
├── backend/               # Python FastAPI Server
│   ├── main.py           # Main server file
│   ├── models.py         # Database models
│   ├── schemas.py        # Data validation
│   ├── crud.py           # Database operations
│   ├── database.py       # DB configuration
│   ├── alerts.py         # Alert system
│   ├── requirements.txt  # Python dependencies
│   └── sentinai.db      # SQLite database (auto-created)
│
└── dashboard/            # Frontend Dashboard
    ├── index.html       # Main HTML (your design)
    ├── style.css        # Styles (your design)
    ├── script.js        # Enhanced with backend integration
    └── README.md        # This file
```

---

## 🚀 Quick Start (2 Steps!)

### Step 1: Start the Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server runs on: **http://localhost:8000**

Important: always run the backend from the `backend` directory so the SQLite file is created and used at `backend/sentinai.db`. Running `python backend/main.py` from the project root can create a separate `sentinai.db` in the root folder.

### Step 2: Open Dashboard

```bash
cd dashboard

# Open index.html in your browser
# Or use a local server:
python -m http.server 3000
```

Dashboard: **http://localhost:3000**

**That's it!** Your dashboard is now connected to the backend!

---

## 🎮 Using the Dashboard

### Features:

1. **🎥 Webcam** - Start live camera feed
2. **📁 Upload** - Upload video files
3. **🚨 Test** - Trigger test alert
4. **🗑️ Clear** - Clear all alerts
5. **🔄 Refresh** - Reload data from backend
6. **📶 Network** - Check network status

### Keyboard Shortcuts:

- `Ctrl+R` - Refresh data
- `Ctrl+T` - Test alert
- `Ctrl+D` - Clear alerts

### Panels:

- **Alerts** - Live security alerts (collapsible)
- **Event History** - Complete event log (collapsible)

---

## 🔌 How It Works

### Real-Time Flow:

```
1. Backend generates/receives alert
   ↓
2. WebSocket broadcasts to dashboard
   ↓
3. Dashboard updates UI instantly
   ↓
4. Alert appears with animation
```

### API Flow:

```
Dashboard → API Request → Backend → Database → Response → Dashboard
```

---

## 📡 Backend API

### Key Endpoints:

```bash
# Get system status
GET http://localhost:8000/api/status

# Get all alerts
GET http://localhost:8000/api/alerts

# Create new alert
POST http://localhost:8000/api/alerts
{
  "type": "intrusion",
  "camera_id": "1",
  "description": "Person detected",
  "severity": "high",
  "confidence": 0.95
}

# Get all events
GET http://localhost:8000/api/events

# Upload video
POST http://localhost:8000/api/upload/video

# WebSocket connection
WS ws://localhost:8000/ws
```

### Interactive Docs:

**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

---

## 🎯 Demo Mode

The backend **automatically generates demo alerts** every 30 seconds.

To disable demo mode, edit `backend/main.py`:

```python
# Comment out this line in startup_event():
# asyncio.create_task(generate_demo_data())
```

---

## 🧪 Testing

### Test 1: Check Backend
```bash
curl http://localhost:8000/api/status
```

Expected: System status JSON

### Test 2: Create Alert
```bash
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "intrusion",
    "camera_id": "1",
    "description": "Test alert",
    "severity": "high",
    "confidence": 0.95
  }'
```

Expected: Alert appears in dashboard instantly!

### Test 3: WebSocket
Open browser console on dashboard:
```javascript
// Should see:
// ✅ WebSocket connected to FastAPI backend
// 📨 Received: INITIAL_STATE
```

---

## 🎨 Customization

### Change Backend URL

Edit `dashboard/script.js`:
```javascript
const API_URL = 'http://localhost:8000/api';  // Change this
const WS_URL = 'ws://localhost:8000/ws';      // And this
```

### Add Camera

```python
# In Python:
import requests

requests.post('http://localhost:8000/api/cameras', json={
    'name': 'Camera 02 - Parking',
    'location': 'Parking Lot',
    'status': 'active'
})
```

### Modify Alert Types

Edit `backend/schemas.py` and `backend/models.py`

---

## 🔧 Configuration

### Backend Port

Edit `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change 8000
```

### Database

Currently using SQLite (`sentinai.db`).

To use PostgreSQL:
```python
# In database.py:
DATABASE_URL = "postgresql://user:pass@localhost/sentinai"
```

---

## 🐛 Troubleshooting

### Dashboard Not Connecting?

1. Check backend is running: `curl http://localhost:8000`
2. Check browser console for errors
3. Verify URLs in `script.js` match backend

### No Alerts Appearing?

1. Check WebSocket connection in console
2. Test alert: Click "🚨 Test" button
3. Check backend logs for errors

### Video Not Playing?

1. Ensure video format is supported (MP4, WebM)
2. Check browser console for errors
3. Try webcam instead

### Port Already in Use?

```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or change port in main.py
```

---

## 📊 Database Schema

### Tables:

**incidents** (alerts)
- id, type, camera_id, description
- severity, confidence, timestamp
- acknowledged, metadata

**cameras**
- id, name, location, status
- ip_address, rtsp_url
- created_at, last_ping

**events**
- id, type, description
- camera_id, severity, timestamp, details

**recordings**
- id, camera_id, filename, filepath
- duration, file_size, start_time, end_time

---

## 🚀 Production Deployment

### 1. Use Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

### 2. Set Up Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
```

### 3. Enable HTTPS

```bash
sudo certbot --nginx -d your-domain.com
```

### 4. Environment Variables

Create `.env`:
```env
DATABASE_URL=postgresql://user:pass@localhost/sentinai
DEBUG=False
SECRET_KEY=your-secret-key
```

---

## 🎯 Next Steps

1. ✅ **System Running** - Backend + Dashboard working
2. 🎥 **Add Real Cameras** - Connect IP cameras via RTSP
3. 🤖 **Add Real AI** - Integrate TensorFlow.js or YOLO
4. 📧 **Email Alerts** - Add SMTP notifications
5. 📱 **Mobile App** - Build React Native app
6. ☁️ **Cloud Deploy** - Deploy to AWS/Azure
7. 📊 **Analytics** - Add charts and reports
8. 🔐 **Authentication** - Add user login

---

## 💡 Tips

- **Demo alerts stop**: Restart backend
- **Clean database**: Delete `sentinai.db` and restart
- **Test without backend**: Dashboard works offline (no real-time updates)
- **Multiple cameras**: Just add more camera entries
- **Custom alerts**: Modify severity levels in code

---

## 📞 Quick Commands

```bash
# Start backend
cd backend && python main.py

# Start dashboard
cd dashboard && python -m http.server 3000

# Test backend
curl http://localhost:8000/api/status

# View logs
tail -f backend/logs.txt  # if logging enabled

# Reset database
rm backend/sentinai.db && cd backend && python main.py
```

---

## 🎉 You're Ready!

Your security dashboard is **fully functional** with:
- Real-time WebSocket updates
- Beautiful custom UI
- Working backend API
- Demo data generator
- Video support
- Network monitoring

**Enjoy your SentinAI Security System!** 🚀
=======
# 🏆 SentinAI

### *Edge-Based, Tamper-Resistant Smart Surveillance System*

> **Built for CSI Core Projects Initiative 2026**
> **Domain:** Cybersecurity + AI + Full Stack
> **Duration:** 25 Days | **Team Size:** 4

---

**SentinAI converts passive CCTV cameras into active, tamper-resistant safety systems that detect threats in real time and raise alerts even during network or camera attacks.**

---

## ❗ Problem We Address

* Traditional CCTV systems **only record incidents**; they don’t prevent them.
* Many cameras are **easily disabled** via:

  * Feed looping
  * Black screen attacks
  * Network cable cuts
* This leads to **delayed response**, lost evidence, and unsafe environments.

Cities today have thousands of cameras that **witness tragedies but do nothing to stop them**.

---

## 💡 Our Solution (What We Built)

**SentinAI** is an **edge-based smart surveillance system** that:

* Detects **fire, accidents, and SOS gestures** using AI
* Detects **camera tampering and feed manipulation**
* Triggers **local alarms instantly**, even if the internet is cut
* Displays alerts and logs on a **simple live dashboard**

> The system works **independently of the network**, making it reliable in real-world attack scenarios.

---

## 🔐 Why This Is a Cybersecurity Project 

SentinAI focuses on **securing surveillance infrastructure**, not just AI detection.

It ensures:

* **Availability** → Works even during network failure
* **Integrity** → Detects feed manipulation and looping
* **Resilience** → Edge-based processing prevents single-point failure

This places the project under **Cyber-Physical Security & Surveillance Security**, a modern cybersecurity domain.

---

## ⚙️ Core Features (MVP – Fully Implemented)

### 🧠 AI Detection

* Fire & accident detection (YOLO – pre-trained)
* SOS / distress gesture detection (MediaPipe)

### 🛡️ Security & Tamper Detection

* Black screen detection
* Looped / frozen feed detection
* Camera heartbeat monitoring

### 🚨 Alert System

* Local buzzer / siren (works without internet)
* Dashboard alerts
* Time-stamped incident logging

### 🖥️ Dashboard

* Live camera feed
* Real-time alerts
* Event history log

---

## 🔄 System Workflow (Simple)

1. Camera captures live video
2. Edge device processes feed locally
3. AI detects anomalies (fire / accident / SOS)
4. Security module checks feed integrity
5. Alerts triggered instantly
6. Events logged and shown on dashboard

---

## 🛠️ Tech Stack (Practical & Industry-Relevant)

| Layer         | Technology                 |
| ------------- | -------------------------- |
| Edge Device   | Raspberry Pi / Jetson Nano |
| AI Models     | YOLO, MediaPipe            |
| CV Processing | OpenCV                     |
| Backend       | Python, Flask / FastAPI    |
| Frontend      | React.js / Flutter         |
| Storage       | SQLite / Local Storage     |
| Alerts        | Buzzer, Notifications      |

---

## 👥 Team Structure & Accountability

| Member      | Responsibility                |
| ----------- | ----------------------------- |
| **Anusha**  | AI & Computer Vision          |
| **Shravya** | Cybersecurity & Edge Security |
| **Sujesh**  | Backend Development           |
| **Bhuvan**  | Frontend & Dashboard          |

> Roles were clearly defined to ensure **accountability**, with planned role rotation for cross-learning.

---

## ⏳ Execution Timeline (25 Days)

* **Week 1:** Setup & planning
* **Week 2:** AI model integration
* **Week 3:** Security & tamper detection
* **Week 4:** Dashboard & alerts
* **Week 5:** Testing, attack simulation, demo prep

Focus was on **working software**, not slides.

---

## 🎯 What Makes This Project Stand Out

✔ Real-world problem with social impact
✔ Strong cybersecurity alignment
✔ Edge-based (not cloud-dependent)
✔ Live demo-ready
✔ Clear execution within 25 days

---

## 🚀 Outcome & Impact

SentinAI shows how **AI + Cybersecurity** can:

* Prevent incidents instead of just recording them
* Protect surveillance systems from attacks
* Improve emergency response during the critical **Golden Hour**

---

## 🏅 CSI Core Projects Initiative 2026

This project was built under the **CSI Core Projects Initiative 2026**, emphasizing:

* Real execution
* Weekly accountability
* Industry-relevant outcomes

---

> **SentinAI is not just a model or a dashboard — it is a working, secure surveillance system designed for real-world deployment.**

---
>>>>>>> origin/frontend-module
