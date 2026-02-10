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
