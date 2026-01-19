# 🚀 Evolution Todo - Quick Start Guide

**Date:** 2026-01-13
**Status:** ✅ All services running

---

## 📍 Access URLs (Copy & Paste)

### Frontend (Next.js)
```
http://localhost:3000
```

### Login Page
```
http://localhost:3000/login
```

### Chat Page (AI Assistant)
```
http://localhost:3000/chat
```

### Dashboard
```
http://localhost:3000/dashboard
```

### Backend API (Health Check)
```
http://localhost:8000
```

### API Documentation (Swagger)
```
http://localhost:8000/docs
```

---

## ✅ Current Status

| Service | Status | Port | URL |
|---------|--------|------|-----|
| **Frontend** | ✅ Running | 3000 | http://localhost:3000 |
| **Backend** | ✅ Running | 8000 | http://localhost:8000 |
| **Database** | ✅ Connected | - | Neon PostgreSQL |

---

## 🔧 Fix 401 Errors

### Quick Fix (2 Steps):

**Step 1: Clear Browser Storage**
```javascript
// Open browser console (F12 → Console tab)
localStorage.clear();
```

**Step 2: Login Again**
1. Go to: http://localhost:3000/login
2. Login with your credentials
3. Navigate to: http://localhost:3000/chat

---

## 🐛 Troubleshooting

### Frontend Not Loading?
```bash
# Check if running
ps aux | grep "next dev" | grep -v grep

# If not running, start it:
cd /mnt/d/hackathon-2/phase-3/frontend
npm run dev
```

### Backend Not Responding?
```bash
# Check if running
ps aux | grep uvicorn | grep -v grep

# If not running, start it:
cd /mnt/d/hackathon-2/phase-3/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### JWT Token Errors?
See detailed guide: `/mnt/d/hackathon-2/phase-3/backend/FIX_401_ERRORS_FINAL.md`

---

## 📊 Monitor Backend Logs

### Real-time JWT Authentication Logs:
```bash
cd /mnt/d/hackathon-2/phase-3/backend
./monitor_jwt.sh
```

### All Backend Logs:
```bash
tail -f /tmp/backend_jwt_debug.log
```

---

## 🎯 Testing Checklist

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend health check returns JSON at http://localhost:8000
- [ ] Can login at /login page
- [ ] Dashboard shows tasks at /dashboard
- [ ] Chat page works at /chat
- [ ] No 401 errors in console
- [ ] Backend logs show `✅ JWT Valid`

---

## 📞 Quick Commands

```bash
# Check all services
ps aux | grep -E "(uvicorn|next dev)" | grep -v grep

# Test backend health
curl http://localhost:8000/

# Test frontend (should return HTML)
curl http://localhost:3000/ | head -5

# Monitor logs
tail -f /tmp/backend_jwt_debug.log
```

---

## 🔐 Default Credentials

If you need to create a test user:
```bash
# Register via API:
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Or use the frontend signup page:
http://localhost:3000/login
```

---

## 🎨 Features Overview

### Phase 3 Features:
- ✅ AI Chatbot (English + Urdu)
- ✅ Voice Input (Whisper STT)
- ✅ Task Management (CRUD)
- ✅ Smart Reminders
- ✅ Recurring Tasks
- ✅ Task History
- ✅ User Preferences
- ✅ Notifications
- ✅ JWT Authentication

---

**Last Updated:** 2026-01-13 09:00
**All Services:** ✅ Running
**Ready to Test:** http://localhost:3000
