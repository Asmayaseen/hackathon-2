# Phase 2 vs Phase 3 - URLs and Configuration

## 🚨 CRITICAL: Do NOT Mix URLs Between Phases!

This document clearly separates Phase 2 and Phase 3 configurations to avoid URL mixing.

---

## 📦 Phase 2: Basic Todo App

### Phase 2 Architecture:
- **Features**: Task CRUD, Authentication, Filtering, Advanced features
- **NO AI**: No chatbot, no voice input
- **Technology**: Next.js + FastAPI + PostgreSQL

### Phase 2 URLs:

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend (Vercel)** | `https://hackathon-2-chi-one.vercel.app` | ✅ Deployed |
| **Backend (HF Space)** | `https://asma-yaseen-evolution-todo-api.hf.space` | ✅ Running |

### Phase 2 Configuration:

#### Frontend (.env.production):
```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-todo-api.hf.space
```

#### Backend (HF Secrets):
```env
DATABASE_URL=postgresql://...
JWT_SECRET=...
CORS_ORIGINS=https://hackathon-2-chi-one.vercel.app,http://localhost:3000
```

#### Vercel Settings (Phase 2):
- **Root Directory**: `phase-2/frontend`
- **Environment Variable**:
  - `NEXT_PUBLIC_API_URL` = `https://asma-yaseen-evolution-todo-api.hf.space`

---

## 🤖 Phase 3: AI-Powered Todo App (Chatbot)

### Phase 3 Architecture:
- **Features**: Everything from Phase 2 + AI Chatbot + Voice Input
- **AI**: Groq API (FREE) for chat and voice transcription
- **Technology**: Next.js + FastAPI + PostgreSQL + OpenAI Agents SDK

### Phase 3 URLs:

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend (Vercel)** | `https://your-phase3-app.vercel.app` | 🔄 To Deploy |
| **Backend (HF Space)** | `https://asma-yaseen-evolution-chatbot.hf.space` | ✅ Running |

### Phase 3 Configuration:

#### Frontend (.env.local for local dev):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Frontend (Vercel Production):
Set in Vercel Dashboard:
```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-chatbot.hf.space
```

#### Backend (HF Secrets):
```env
DATABASE_URL=postgresql://...
JWT_SECRET=...
GROQ_API_KEY=gsk_...
AI_MODEL=openai/gpt-oss-20b
CORS_ORIGINS=https://your-phase3-app.vercel.app,http://localhost:3000
```

⚠️ **IMPORTANT**: CORS_ORIGINS should list the FRONTEND URLs that can access the backend!

#### Vercel Settings (Phase 3):
- **Root Directory**: `phase-3/frontend`
- **Environment Variable**:
  - `NEXT_PUBLIC_API_URL` = `https://asma-yaseen-evolution-chatbot.hf.space`

---

## 🔍 Quick Reference Table

| Phase | Frontend Code | Backend Code | Frontend URL | Backend URL |
|-------|---------------|--------------|--------------|-------------|
| **Phase 2** | `phase-2/frontend/` | `phase-2/backend/` | hackathon-2-chi-one.vercel.app | asma-yaseen-evolution-**todo-api**.hf.space |
| **Phase 3** | `phase-3/frontend/` | `phase-3/backend/` | your-phase3-app.vercel.app | asma-yaseen-evolution-**chatbot**.hf.space |

---

## ⚠️ Common Mistakes to Avoid

### ❌ WRONG: Mixing URLs

```env
# Phase 3 frontend pointing to Phase 2 backend - WRONG!
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-todo-api.hf.space
```

```env
# Phase 2 frontend pointing to Phase 3 backend - WRONG!
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-chatbot.hf.space
```

### ✅ CORRECT: Separate URLs

**Phase 2 Frontend** → **Phase 2 Backend** (todo-api)
```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-todo-api.hf.space
```

**Phase 3 Frontend** → **Phase 3 Backend** (chatbot)
```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-chatbot.hf.space
```

---

## 🔧 How to Deploy Both Phases Separately

### Option 1: Two Separate Vercel Projects (Recommended)

**Phase 2 Project:**
- Name: `hackathon-2` (existing)
- Root Directory: `phase-2/frontend`
- Git Branch: `main`
- URL: https://hackathon-2-chi-one.vercel.app

**Phase 3 Project:**
- Name: `hackathon-2-phase3` (new project)
- Root Directory: `phase-3/frontend`
- Git Branch: `phase-3`
- URL: https://hackathon-2-phase3.vercel.app

### Option 2: Same Project, Different Branches

Keep existing project but:
- **Production Branch**: `main` (deploys Phase 2)
- **Preview Branch**: `phase-3` (deploys Phase 3)
- Update Root Directory setting when switching

---

## 🎯 Current Status

### ✅ What's Correct:

1. **Phase 2 Backend**:
   - ✅ Deployed at correct URL: `asma-yaseen-evolution-todo-api.hf.space`
   - ✅ No AI features

2. **Phase 3 Backend**:
   - ✅ Deployed at correct URL: `asma-yaseen-evolution-chatbot.hf.space`
   - ✅ Has AI features (Groq)

3. **Local Configuration**:
   - ✅ Phase 2 uses correct production URL
   - ✅ Phase 3 uses localhost for development

### ⚠️ Action Required:

1. **Phase 3 Backend CORS**: Currently has backend URL in CORS
   ```env
   # Current (WRONG):
   CORS_ORIGINS=...,https://asma-yaseen-evolution-chatbot.hf.space

   # Should be (CORRECT):
   CORS_ORIGINS=...,https://your-phase3-frontend.vercel.app
   ```

2. **Vercel Project**: Update Root Directory to `phase-3/frontend`

3. **Environment Variable**: Set in Vercel Dashboard

---

## 🧪 Testing URLs

### Phase 2 Testing:
```bash
# Backend health check
curl https://asma-yaseen-evolution-todo-api.hf.space/

# Frontend
open https://hackathon-2-chi-one.vercel.app
```

### Phase 3 Testing:
```bash
# Backend health check
curl https://asma-yaseen-evolution-chatbot.hf.space/

# Frontend (after deployment)
open https://your-phase3-app.vercel.app
```

---

## 📋 Deployment Checklist

When deploying Phase 3:

- [ ] ✅ Backend deployed to HF Space: `evolution-chatbot`
- [ ] ✅ Backend URL is: `asma-yaseen-evolution-chatbot.hf.space`
- [ ] Update backend CORS with actual frontend URL
- [ ] Configure Vercel Root Directory: `phase-3/frontend`
- [ ] Set Vercel env: `NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-chatbot.hf.space`
- [ ] Deploy frontend to Vercel
- [ ] Test that frontend connects to correct backend
- [ ] Verify Phase 2 still works independently

---

## 🔗 Related Documentation

- Phase 2 Deployment: `DEPLOYMENT.md`
- Phase 3 Setup: `VERCEL_SETUP.md`
- Security Guidelines: `SECURITY.md`
- Environment Setup: `.env.example` files in each phase

---

**Remember**: Phase 2 and Phase 3 are COMPLETELY SEPARATE applications with DIFFERENT URLs!

**Last Updated**: 2026-01-12
