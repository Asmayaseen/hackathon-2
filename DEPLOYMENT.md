# Deployment Guide - Evolution Todo

Complete deployment guide for Evolution Todo full-stack application.

## ✅ Deployment Status

| Component | Platform | Status | URL |
|-----------|----------|--------|-----|
| **Frontend** | Vercel | ✅ Deployed | https://hackathon-2-chi-one.vercel.app |
| **Backend** | Hugging Face Spaces | ✅ Deployed | https://asma-yaseen-evolution-todo-api.hf.space |
| **Database** | Neon/Supabase | ✅ Connected | (configured in HF secrets) |

---

## 🚀 Frontend Deployment (Vercel)

### Configuration

**Project:** `hackathon-2`
**Framework:** Next.js 16
**Root Directory:** `phase-2/frontend`
**Production Branch:** `main`

### Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables:

```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-todo-api.hf.space
```

**Apply to:** ✅ Production ✅ Preview ✅ Development

### Manual Setup Steps

1. Go to: https://vercel.com/asmayaseens-projects/hackathon-2/settings/environment-variables
2. Click "Add New" → "Environment Variable"
3. Enter:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://asma-yaseen-evolution-todo-api.hf.space`
   - **Environments:** Select all three
4. Click "Save"
5. Go to "Deployments" tab → Click "Redeploy" on latest deployment

---

## 🔧 Backend Deployment (Hugging Face Spaces)

### Configuration

**Space Name:** `evolution-todo-api`
**SDK:** Docker
**Port:** 7860
**Username:** `Asma-yaseen`

### Repository Secrets

Set in Space Settings → Repository secrets:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname?sslmode=require
JWT_SECRET=your_secure_random_32_char_secret_key_here
CORS_ORIGINS=https://hackathon-2-chi-one.vercel.app,http://localhost:3000
```

### Database Setup (Neon.tech - Recommended)

1. Visit: https://neon.tech
2. Create new project: `evolution-todo-db`
3. Copy connection string
4. Add to Hugging Face Space secrets as `DATABASE_URL`

### Generate JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🧪 Testing Full Stack

### 1. Test Backend

```bash
# Health check
curl https://asma-yaseen-evolution-todo-api.hf.space/

# Should return:
# {"message":"Evolution Todo API","status":"running","version":"1.0.0"}
```

### 2. Test Frontend

1. Visit: https://hackathon-2-chi-one.vercel.app
2. Click "Initialize Account" (Sign Up)
3. Create test account:
   - Name: Test User
   - Email: test@example.com
   - Password: testpass123
4. Sign in with credentials
5. Create a task
6. Test: Complete, Edit, Delete

### 3. Verify Integration

Open browser DevTools → Network tab → Check API calls:

```
POST https://asma-yaseen-evolution-todo-api.hf.space/api/auth/signup
POST https://asma-yaseen-evolution-todo-api.hf.space/api/auth/signin
GET  https://asma-yaseen-evolution-todo-api.hf.space/api/{user_id}/tasks
```

All should return `200 OK`

---

## 🔄 Redeployment

### Frontend (Vercel)

**Automatic:** Push to `main` branch triggers deployment

**Manual:**
```bash
git commit --allow-empty -m "Redeploy frontend"
git push origin main
```

### Backend (Hugging Face)

**Automatic:** Push to Space repository triggers rebuild

**Manual:** Space Settings → Factory reboot

---

## 📋 Environment Variables Summary

### Frontend (.env.production or Vercel)

```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-todo-api.hf.space
```

### Backend (Hugging Face Secrets)

```env
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require
JWT_SECRET=<generated-secret-32-chars>
CORS_ORIGINS=https://hackathon-2-chi-one.vercel.app,http://localhost:3000
```

---

## 🐛 Troubleshooting

### Frontend shows "Network Error"

- ✅ Check `NEXT_PUBLIC_API_URL` is set in Vercel
- ✅ Verify backend is running on HF Space
- ✅ Check CORS settings in backend secrets

### Backend "Database connection error"

- ✅ Verify `DATABASE_URL` in HF Space secrets
- ✅ Check database is running (Neon dashboard)
- ✅ Ensure `?sslmode=require` in connection string

### "Invalid token" or "Unauthorized" errors

- ✅ Check `JWT_SECRET` is set in backend
- ✅ Clear browser localStorage and re-login
- ✅ Verify token is being sent in Authorization header

---

## 📊 Monitoring

### Vercel Dashboard
- **Analytics:** Track visitors and page views
- **Logs:** Runtime logs for errors
- **Performance:** Speed insights

### Hugging Face Space
- **Logs:** Container logs tab
- **Metrics:** CPU/Memory usage
- **Status:** Build status and health

---

## 🎉 Success Criteria

- ✅ Frontend loads without errors
- ✅ Sign up creates user in database
- ✅ Sign in returns JWT token
- ✅ Tasks page shows empty state
- ✅ Create task adds to database
- ✅ Toggle complete updates task
- ✅ Delete removes task
- ✅ No CORS errors in console

---

Built with ❤️ using Next.js 16, FastAPI, and PostgreSQL
