# Hugging Face Secrets Configuration - Phase 3 Backend

## 🔍 Current Status

**Backend URL**: https://asma-yaseen-evolution-chatbot.hf.space
**Status**: ✅ Running (API responds with version 1.0.0)
**Git Remote**: `hf https://huggingface.co/spaces/Asma-yaseen/evolution-chatbot`

---

## 🔑 Required Secrets (MUST be set in HF Space Settings)

Go to: https://huggingface.co/spaces/Asma-yaseen/evolution-chatbot/settings

Click **"Repository secrets"** tab and add these:

### 1. Database Connection
```
Name: DATABASE_URL
Value: postgresql://neondb_owner:npg_9o7LbiyKpwrN@ep-divine-union-ahlsszpq-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```
**Why**: Connects to Neon PostgreSQL database for storing tasks, users, conversations

---

### 2. JWT Authentication
```
Name: JWT_SECRET
Value: 5Uk7VYMMiWOxhfeU1LCCWey2qQcpp1PX4sxFMQzKhGk=
```
**Why**: Signs and verifies JWT tokens for user authentication

```
Name: JWT_ALGORITHM
Value: HS256
```
**Why**: Algorithm used for JWT signing

```
Name: JWT_EXPIRE_MINUTES
Value: 1440
```
**Why**: JWT token expiration time (1440 = 24 hours)

---

### 3. CORS Configuration
```
Name: CORS_ORIGINS
Value: http://localhost:3000,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3002,https://frontend-qnzzeug89-asma-yaseens-projects.vercel.app,https://frontend-umber-nine-80.vercel.app
```
**Why**: Allows frontend URLs to access backend API (prevents CORS errors)

**CRITICAL**: Make sure both Vercel URLs are included:
- `https://frontend-qnzzeug89-asma-yaseens-projects.vercel.app`
- `https://frontend-umber-nine-80.vercel.app` ✅ (This is your Phase 3 frontend)

---

### 4. AI Configuration (Groq API)
```
Name: GROQ_API_KEY
Value: <your-groq-api-key>
```
**Why**: FREE API for AI chatbot (GPT-compatible) and voice transcription

```
Name: GROQ_BASE_URL
Value: https://api.groq.com/openai/v1
```
**Why**: Groq API endpoint (OpenAI-compatible)

```
Name: AI_MODEL
Value: openai/gpt-oss-20b
```
**Why**: AI model to use for chatbot responses (FREE on Groq)

---

## 📋 Secrets Checklist

Copy this checklist to verify all secrets are set:

- [ ] **DATABASE_URL** - PostgreSQL connection string with Neon
- [ ] **JWT_SECRET** - 32+ character random string
- [ ] **JWT_ALGORITHM** - HS256
- [ ] **JWT_EXPIRE_MINUTES** - 1440 (24 hours)
- [ ] **CORS_ORIGINS** - Includes `frontend-umber-nine-80.vercel.app`
- [ ] **GROQ_API_KEY** - Your Groq API key (starts with `gsk_`)
- [ ] **GROQ_BASE_URL** - `https://api.groq.com/openai/v1`
- [ ] **AI_MODEL** - `openai/gpt-oss-20b`

---

## 🧪 Testing After Setting Secrets

### 1. Restart Space
After adding/updating secrets:
1. Go to Space settings
2. Click **"Factory reboot"** to restart with new secrets

### 2. Test Backend Health
```bash
curl https://asma-yaseen-evolution-chatbot.hf.space/
```

**Expected Response:**
```json
{
  "message": "Evolution Todo API",
  "status": "running",
  "version": "1.0.0"
}
```

### 3. Test AI Chat Endpoint
```bash
curl -X POST https://asma-yaseen-evolution-chatbot.hf.space/api/YOUR_USER_ID/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Add a task to buy milk",
    "conversation_id": null
  }'
```

**Expected**: Should return AI response with task creation

### 4. Test from Frontend
1. Go to: https://frontend-umber-nine-80.vercel.app/
2. Sign in or sign up
3. Go to: https://frontend-umber-nine-80.vercel.app/chat
4. Type: "Add a task to buy groceries tomorrow"
5. Should get AI response

---

## ⚠️ Common Issues

### Issue 1: CORS Error in Frontend
**Symptom**: Browser console shows CORS policy error
**Fix**: Verify `CORS_ORIGINS` includes your exact Vercel URL (including `https://`)

### Issue 2: "Database connection failed"
**Symptom**: API returns 500 error or "database error"
**Fix**:
- Check `DATABASE_URL` is correct
- Verify Neon database is running
- Ensure `?sslmode=require` is in connection string

### Issue 3: "Invalid token" errors
**Symptom**: API returns 401 Unauthorized
**Fix**:
- Check `JWT_SECRET` is set
- Verify `JWT_ALGORITHM` is `HS256`
- Frontend may need to re-login to get new token

### Issue 4: AI Chat not working
**Symptom**: Chat returns "Error" or "I'm having trouble..."
**Fix**:
- Verify `GROQ_API_KEY` is set
- Check `GROQ_BASE_URL` is correct
- Ensure `AI_MODEL` is `openai/gpt-oss-20b`
- Check Groq API quota/limits

---

## 🔒 Security Notes

1. **Never commit secrets to git**
   - `.env` is in `.gitignore`
   - Only commit `.env.example` with placeholder values

2. **Rotate secrets regularly**
   - JWT_SECRET: Every 90 days
   - GROQ_API_KEY: If exposed
   - DATABASE_URL: If credentials compromised

3. **Use strong JWT secrets**
   - Minimum 32 characters
   - Random, not guessable
   - Generated with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## 📝 Quick Setup Commands

If secrets are missing, add them via HF CLI:

```bash
# Install HF CLI (if not already)
pip install huggingface-hub

# Login
huggingface-cli login

# Add secret
huggingface-cli repo secret add \
  Asma-yaseen/evolution-chatbot \
  DATABASE_URL \
  --value "postgresql://..."

# Repeat for each secret...
```

Or manually through web UI (recommended):
https://huggingface.co/spaces/Asma-yaseen/evolution-chatbot/settings

---

## ✅ Verification Steps

After setting all secrets:

1. **Backend Running**: ✅ (Verified: API responds)
2. **Database Connected**: Test by creating a user via signup
3. **CORS Configured**: Test from frontend (no CORS errors)
4. **AI Working**: Test chat endpoint returns responses
5. **Voice Working**: Test transcription endpoint with audio

---

**Last Updated**: 2026-01-12
**Backend Version**: 1.0.0
**Status**: Deployed and Running
