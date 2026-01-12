# Vercel Deployment Setup - Phase 3

## 🔧 Current Issue Fixed

The error `"The specified Root Directory 'frontend' does not exist"` occurred because:
- Vercel Project Settings had Root Directory set to "frontend"
- But your project structure is: `phase-3/frontend/`

## ✅ Solution Applied

### 1. Updated vercel.json
The `vercel.json` has been updated to point to Phase 3 frontend:

```json
{
  "buildCommand": "cd phase-3/frontend && npm install && npm run build",
  "framework": "nextjs",
  "outputDirectory": "phase-3/frontend/.next"
}
```

### 2. Update Vercel Project Settings

**IMPORTANT**: You MUST update these settings in Vercel Dashboard:

#### Option A: Set Root Directory (Recommended)
1. Go to: https://vercel.com/asma-yaseens-projects/hackathon-2/settings/general
2. Scroll to **"Root Directory"** section
3. Click **"Edit"**
4. Change from: `frontend`
5. Change to: `phase-3/frontend`
6. Click **"Save"**

#### Option B: Clear Root Directory
1. Go to same settings page
2. In **"Root Directory"** section
3. Click **"Edit"**
4. **Delete** the value (leave it empty)
5. Click **"Save"**
6. Vercel will use `vercel.json` configuration

## 📋 Complete Deployment Checklist

### Step 1: Commit Changes
```bash
git add vercel.json
git commit -m "fix: Configure Vercel for Phase 3 frontend deployment"
git push origin phase-3
```

### Step 2: Update Vercel Project Settings

Go to: https://vercel.com/asma-yaseens-projects/hackathon-2/settings

#### General Settings:
- **Root Directory**: `phase-3/frontend` (or leave empty)
- **Framework Preset**: Next.js (auto-detected)
- **Build Command**: (leave empty, uses vercel.json)
- **Output Directory**: (leave empty, uses vercel.json)
- **Install Command**: (leave empty, uses vercel.json)

#### Environment Variables:
Click **"Environment Variables"** tab and add:

| Name | Value | Environments |
|------|-------|--------------|
| `NEXT_PUBLIC_API_URL` | `https://asma-yaseen-evolution-chatbot.hf.space` | Production, Preview, Development |

**Apply to all environments**: ✅ Production ✅ Preview ✅ Development

### Step 3: Deploy

After updating settings:

#### Option 1: Redeploy Current Deployment
1. Go to: https://vercel.com/asma-yaseens-projects/hackathon-2/deployments
2. Find the latest deployment
3. Click **"•••"** (three dots menu)
4. Click **"Redeploy"**
5. Confirm redeploy

#### Option 2: Push New Commit
```bash
# Trigger new deployment by pushing
git commit --allow-empty -m "chore: Trigger Vercel redeployment"
git push origin phase-3
```

## 🎯 Expected Build Output

If successful, you should see:

```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /                                    ...      ... kB
├ ○ /auth/signin                         ...      ... kB
├ ○ /auth/signup                         ...      ... kB
├ ○ /chat                                ...      ... kB
└ ○ /dashboard                           ...      ... kB
```

## 🔍 Troubleshooting

### Error: "Could not find package.json"
**Fix**: Root Directory setting is still wrong. Set to `phase-3/frontend`.

### Error: "Module not found" or build errors
**Fix**: Check environment variables are set in Vercel.

### Error: "Port already in use" (local dev)
**Fix**: This is normal for Vercel CLI. Ignore or stop local server.

### Deployment succeeds but app doesn't work
**Checklist**:
1. ✅ `NEXT_PUBLIC_API_URL` is set in Vercel
2. ✅ Backend is running on Hugging Face
3. ✅ CORS is configured in backend .env
4. ✅ Check browser console for errors

## 🚀 Deployment URLs

After successful deployment:

- **Production**: https://hackathon-2-chi-one.vercel.app (or your custom domain)
- **Preview**: https://hackathon-2-[hash].vercel.app (for PRs)

## 📊 Deployment Status

Check deployment logs at:
https://vercel.com/asma-yaseens-projects/hackathon-2/deployments

## 🔗 Related Documentation

- Backend Deployment: See `phase-3/DEPLOYMENT.md`
- Environment Setup: See `SECURITY.md`
- Testing Guide: See `phase-3/READY_FOR_TESTING.md`

---

**Last Updated**: 2026-01-12
**Status**: Configuration Updated
**Action Required**: Update Vercel Project Settings
