# Fix JWT 401 Unauthorized Error

**Error:** `Request failed with status code 401`
**Location:** Frontend trying to access `/api/{user_id}/conversations`
**Status:** Backend is running, but JWT authentication failing

---

## Problem Diagnosis

Backend logs show:
```
INFO: GET /api/0338ce75-919a-4785-ae38-9b868c20e212/conversations HTTP/1.1" 401 Unauthorized
```

**Possible causes:**
1. JWT token expired
2. JWT token invalid (wrong signature)
3. JWT_SECRET mismatch between signin and verification
4. Token not in correct format

---

## Quick Fixes

### Fix 1: Re-login to Get Fresh Token ✅

**Problem:** Token in localStorage might be expired or invalid.

**Solution:**
1. Go to login page
2. Login again
3. This will create a new JWT token
4. Try accessing chat/conversations again

### Fix 2: Check JWT Secret Consistency

**Problem:** JWT_SECRET might be different from when token was created.

**Check backend .env:**
```bash
cd /mnt/d/hackathon-2/phase-3/backend
cat .env | grep JWT_SECRET
```

Should show:
```
JWT_SECRET=5Uk7VYMMiWOxhfeU1LCCWey2qQcpp1PX4sxFMQzKhGk=
```

**If it changed:** All old tokens are now invalid. Users need to re-login.

### Fix 3: Debug JWT Token

Add this temporary debug endpoint to check token:

```python
# Add to routes/auth.py

@router.post("/debug-token")
async def debug_token(credentials = Depends(security)):
    """Debug JWT token (REMOVE IN PRODUCTION)."""
    token = credentials.credentials

    try:
        # Decode without verification to see payload
        unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"Token payload: {unverified}")

        # Now try to verify
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "status": "valid",
            "payload": payload,
            "user_id": payload.get("user_id")
        }
    except jwt.ExpiredSignatureError:
        return {"status": "expired", "message": "Token expired"}
    except Exception as e:
        return {"status": "invalid", "error": str(e)}
```

Test:
```bash
curl -X POST http://localhost:8000/api/auth/debug-token \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Enhanced JWT Middleware (Better Error Messages)

Replace `/middleware/auth.py` with enhanced version:

```python
"""
JWT Authentication Middleware with Enhanced Error Messages.
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
import jwt
import os
from datetime import datetime

security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-min-32-chars")
JWT_ALGORITHM = "HS256"


async def verify_token(credentials = Depends(security)) -> str:
    """
    Verify JWT token and extract user_id.

    Enhanced with detailed error messages for debugging.
    """
    token = credentials.credentials

    try:
        # Decode and verify JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Extract user_id from payload
        user_id = payload.get("user_id")

        if not user_id:
            print(f"❌ JWT Error: user_id not found in payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found"
            )

        # Log successful verification (for debugging)
        exp = payload.get("exp")
        if exp:
            exp_time = datetime.fromtimestamp(exp)
            print(f"✅ JWT Valid: user_id={user_id}, expires={exp_time}")

        return user_id

    except jwt.ExpiredSignatureError as e:
        print(f"❌ JWT Expired: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please login again."
        )
    except jwt.InvalidSignatureError as e:
        print(f"❌ JWT Invalid Signature: {e}")
        print(f"   Using secret: {JWT_SECRET[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature. Please login again."
        )
    except jwt.DecodeError as e:
        print(f"❌ JWT Decode Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token. Please login again."
        )
    except Exception as e:
        print(f"❌ JWT Unknown Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )
```

This will show detailed error messages in backend logs.

---

## Frontend Fix: Token Refresh Logic

Add token validation before making requests:

```typescript
// frontend/lib/auth.ts

export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    return Date.now() >= exp;
  } catch {
    return true; // If can't decode, consider expired
  }
}

export function getValidToken(): string | null {
  const token = localStorage.getItem('token');

  if (!token) return null;

  if (isTokenExpired(token)) {
    console.log('Token expired, redirecting to login...');
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    window.location.href = '/login';
    return null;
  }

  return token;
}

// Use in API calls:
const token = getValidToken();
if (!token) {
  return; // Will redirect to login
}

const response = await axios.get(url, {
  headers: { Authorization: `Bearer ${token}` }
});
```

---

## Complete Solution Steps

### Step 1: Check Backend Logs
```bash
tail -f /tmp/claude/-mnt-d-hackathon-2/tasks/b64cbe8.output
```

Look for specific JWT error messages.

### Step 2: Update JWT Middleware
```bash
cd /mnt/d/hackathon-2/phase-3/backend
# Apply enhanced middleware code above
```

### Step 3: Restart Backend
```bash
# Kill current process
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill

# Start again
./start_backend.sh
```

### Step 4: Clear Frontend Storage and Re-login
```javascript
// In browser console:
localStorage.clear();
// Then go to login page and login again
```

### Step 5: Test
Try accessing chat page again. Should work now.

---

## Prevention: Token Expiry Settings

Check token expiry time in backend:

```bash
# In .env
JWT_EXPIRE_MINUTES=1440  # 24 hours

# If too short, increase it:
JWT_EXPIRE_MINUTES=10080  # 7 days
```

---

## Quick Test Script

```bash
# Test JWT token from frontend localStorage

# 1. Get token from browser console
TOKEN="paste-token-here"

# 2. Test it
curl -X GET http://localhost:8000/api/YOUR_USER_ID/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -v

# Look for:
# < HTTP/1.1 200 OK  (success)
# < HTTP/1.1 401 Unauthorized  (token invalid)
```

---

## Summary

**Most likely cause:** Token expired or invalid.

**Quickest fix:**
1. Clear localStorage in browser
2. Login again
3. Try chat page

**If still failing:**
1. Check backend logs for specific JWT error
2. Apply enhanced middleware for better error messages
3. Verify JWT_SECRET in .env hasn't changed

---

**Last Updated:** 2026-01-12
**Status:** Diagnostic guide created, awaiting user action
