```markdown
# 🔧 SentinAI – Setup & Installation Guide

This guide explains how to run the SentinAI Security Dashboard locally.

SentinAI consists of:
- A FastAPI backend
- A real-time WebSocket connection
- A SQLite database
- A browser-based dashboard

---

## 📁 Project Structure

```

sentinai/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
│   ├── alerts.py
│   ├── requirements.txt
│   └── sentinai.db (auto-created)
│
└── dashboard/
├── index.html
├── style.css
└── script.js

````

---

## ⚙️ Prerequisites

Before starting, ensure you have:

- Python 3.9 or above
- pip (Python package manager)
- Git (optional, for cloning repository)

Check Python version:

```bash
python --version
````

---

# 🚀 Quick Start (2 Steps)

---

## ✅ Step 1 – Start Backend Server

Navigate to the backend folder:

```bash
cd backend
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
python main.py
```

Backend will start at:

```
http://localhost:8000
```

⚠ Important:
Always run the backend from inside the `backend` folder.
This ensures the SQLite database is created correctly at:

```
backend/sentinai.db
```

---

## ✅ Step 2 – Start Dashboard

Open a new terminal and navigate to dashboard:

```bash
cd dashboard
```

Start a local server:

```bash
python -m http.server 3000
```

Open your browser and visit:

```
http://localhost:3000
```

Your dashboard is now connected to the backend.

---

# 🔌 Backend API Endpoints

### 🔹 System Status

```
GET http://localhost:8000/api/status
```

### 🔹 Get All Alerts

```
GET http://localhost:8000/api/alerts
```

### 🔹 Create New Alert

```
POST http://localhost:8000/api/alerts
```

Example JSON body:

```json
{
  "type": "intrusion",
  "camera_id": "1",
  "description": "Test alert",
  "severity": "high",
  "confidence": 0.95
}
```

### 🔹 WebSocket Connection

```
ws://localhost:8000/ws
```

---

# 🧪 Testing the System

## Test 1 – Check Backend

```bash
curl http://localhost:8000/api/status
```

Expected: JSON response with system status.

---

## Test 2 – Trigger Test Alert

```bash
curl -X POST http://localhost:8000/api/alerts \
-H "Content-Type: application/json" \
-d '{"type":"intrusion","camera_id":"1","description":"Test Alert","severity":"high","confidence":0.95}'
```

Expected: Alert appears instantly on dashboard.

---

## Test 3 – WebSocket Check

Open browser console on dashboard.

You should see:

```
WebSocket connected
Received: INITIAL_STATE
```

---

# ⚙️ Configuration

## Change Backend Port

Edit `backend/main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Change port if needed.

---

## Change API URL (Frontend)

Edit `dashboard/script.js`:

```javascript
const API_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws';
```

Update URLs if backend port changes.

---

# 🗄 Database Information

Database used: **SQLite**

File location:

```
backend/sentinai.db
```

To reset database:

```bash
rm backend/sentinai.db
cd backend
python main.py
```

Database will auto-create on restart.

---

# 🐛 Troubleshooting

## Backend Not Starting?

* Check Python version
* Reinstall dependencies
* Ensure port 8000 is free

---

## Dashboard Not Connecting?

* Confirm backend is running
* Check browser console for errors
* Verify API and WebSocket URLs

---

## Port Already in Use?

Change port in `main.py` or stop the existing process.

---

# 🚀 Basic Production Deployment (Optional)

Install Gunicorn:

```bash
pip install gunicorn
```

Run server:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

Use Nginx as reverse proxy for production deployments.

---

# ✅ System Ready

After completing setup:

* Backend API running
* WebSocket connected
* Dashboard displaying real-time alerts
* SQLite database logging events

SentinAI MVP is now fully operational.

```
