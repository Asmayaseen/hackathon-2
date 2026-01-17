# Security Guidelines - Evolution Todo

**CRITICAL**: This document contains important security information. Please read carefully before setting up or deploying the application.

---

## 🔐 Environment Variables Security

### **NEVER Commit These Files to Git:**
- `.env`
- `.env.local`
- `.env.production`
- `.env.development`
- Any file containing real API keys, passwords, or secrets

### **Safe to Commit:**
- `.env.example` (placeholder values only)
- `.env.local.example` (placeholder values only)

---

## 📋 Required Environment Variables

### Phase 2 Frontend

**File:** `phase-2/frontend/.env.local`

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://your-backend-url.hf.space
```

**Production File:** `phase-2/frontend/.env.production`
```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-todo-api.hf.space
```

### Phase 3 Frontend

**File:** `phase-3/frontend/.env.local`

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI API Key (for Whisper voice transcription)
NEXT_PUBLIC_OPENAI_API_KEY=sk-proj-your_key_here

# Groq API Key (for AI chat)
GROQ_API_KEY=gsk_your_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=openai/gpt-oss-20b
```

**Production:**
```env
NEXT_PUBLIC_API_URL=https://asma-yaseen-evolution-chatbot.hf.space
NEXT_PUBLIC_OPENAI_API_KEY=<from-vercel-secrets>
GROQ_API_KEY=<from-vercel-secrets>
```

### Phase 3 Backend

**File:** `phase-3/backend/.env`

```env
# Database (NEVER commit real connection string!)
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# Authentication
JWT_SECRET=your_secure_random_32_char_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# AI Configuration
GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=sk-your_key_here  # Optional, if using OpenAI

# CORS (update for production)
CORS_ORIGINS=http://localhost:3000,https://your-production-url.vercel.app
```

---

## 🔑 How to Generate Secure Secrets

### JWT Secret (32+ characters)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Or use OpenSSL:
```bash
openssl rand -base64 32
```

---

## 🚀 Deployment Security

### Vercel Environment Variables

**Set these in Vercel Dashboard → Settings → Environment Variables:**

1. **Phase 2 Deployment:**
   - `NEXT_PUBLIC_API_URL` = `https://asma-yaseen-evolution-todo-api.hf.space`

2. **Phase 3 Deployment:**
   - `NEXT_PUBLIC_API_URL` = `https://asma-yaseen-evolution-chatbot.hf.space`
   - `NEXT_PUBLIC_OPENAI_API_KEY` = `<your-openai-key>`
   - `GROQ_API_KEY` = `<your-groq-key>`
   - `GROQ_BASE_URL` = `https://api.groq.com/openai/v1`
   - `AI_MODEL` = `openai/gpt-oss-20b`

**Apply to:** ✅ Production ✅ Preview ✅ Development

### Hugging Face Secrets

**Set these in HF Space Settings → Repository secrets:**

1. **Database:**
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

2. **Authentication:**
   ```
   JWT_SECRET=<your-generated-secret>
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=1440
   ```

3. **AI Keys:**
   ```
   GROQ_API_KEY=gsk_your_key_here
   OPENAI_API_KEY=sk_your_key_here  # If using OpenAI
   ```

4. **CORS (CRITICAL - Update with your Vercel URLs):**
   ```
   CORS_ORIGINS=https://your-vercel-app.vercel.app,https://frontend-preview.vercel.app
   ```

---

## 🛡️ Security Best Practices

### 1. **API Key Rotation**
- Rotate API keys every 90 days
- Immediately rotate if you suspect a key was exposed
- Never share keys via email, chat, or screenshots

### 2. **Database Security**
- Use connection pooling for PostgreSQL (Neon provides this)
- Enable SSL mode: `?sslmode=require`
- Use read-only database users for analytics queries
- Regularly backup your database

### 3. **JWT Tokens**
- Use strong secrets (32+ characters, random)
- Set appropriate expiration times (1440 minutes = 24 hours)
- Store tokens in httpOnly cookies when possible (not implemented yet)
- Never log JWT tokens in production

### 4. **CORS Configuration**
- Only whitelist specific domains (never use `*` in production)
- Update CORS_ORIGINS when deploying to new domains
- Test CORS settings after each deployment

### 5. **Git Security**
- Review `.gitignore` before committing
- Use `git status` to verify no .env files are tracked
- If you accidentally commit secrets:
  1. Rotate the exposed keys immediately
  2. Remove from git history: `git filter-branch` or BFG Repo-Cleaner
  3. Force push (carefully)

---

## 🚨 If You Accidentally Expose Secrets

### Immediate Actions:

1. **Rotate All Exposed Keys:**
   - OpenAI: https://platform.openai.com/api-keys
   - Groq: https://console.groq.com/keys
   - Database: Create new user or change password in Neon dashboard
   - JWT: Generate new secret and redeploy

2. **Remove from Git History:**
   ```bash
   # Install BFG Repo-Cleaner
   # https://rtyley.github.io/bfg-repo-cleaner/

   bfg --replace-text passwords.txt  # File containing old secrets
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

3. **Update All Deployments:**
   - Update Vercel environment variables
   - Update Hugging Face secrets
   - Redeploy both frontend and backend

4. **Monitor for Abuse:**
   - Check API usage dashboards for unusual activity
   - Review database logs for unauthorized access
   - Enable alerts for high usage (if available)

---

## ✅ Security Checklist

Before deploying to production:

- [ ] All .env files are in .gitignore
- [ ] No real API keys in tracked files
- [ ] JWT secret is strong and random
- [ ] Database connection uses SSL
- [ ] CORS is configured for specific domains only
- [ ] Environment variables are set in Vercel/HF dashboards
- [ ] API keys have appropriate usage limits set
- [ ] Sensitive files (like this one) don't contain real secrets

---

## 📚 Additional Resources

- **Neon Database Security:** https://neon.tech/docs/security
- **Vercel Environment Variables:** https://vercel.com/docs/environment-variables
- **Hugging Face Secrets:** https://huggingface.co/docs/hub/spaces-secrets
- **OWASP Security Practices:** https://owasp.org/www-project-top-ten/

---

**Last Updated:** 2026-01-12
**Status:** Active
**Maintained By:** Development Team
