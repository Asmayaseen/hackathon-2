"""
JWT Authentication Middleware with Enhanced Error Messages.

Task: 1.5
Spec: specs/features/authentication.md
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

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        str: user_id extracted from token payload

    Raises:
        HTTPException: 401 if token is invalid or expired
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
