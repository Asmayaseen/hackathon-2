"""
Evolution Todo API - FastAPI Backend

Task: 1.6
Spec: specs/overview.md
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env file first

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db import create_db_and_tables
import os
import traceback

# Initialize FastAPI app
app = FastAPI(
    title="Evolution Todo API",
    version="1.0.0",
    description="RESTful API for Evolution Todo application"
)

# CORS Configuration
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://frontend-umber-nine-80.vercel.app,https://frontend-qnzzeug89-asma-yaseens-projects.vercel.app,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions and return with proper CORS headers."""
    print(f"❌ Global Exception: {exc}")
    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:3000"),
            "Access-Control-Allow-Credentials": "true",
        }
    )


@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    create_db_and_tables()


@app.get("/")
def root():
    """Root endpoint - API status check."""
    return {
        "message": "Evolution Todo API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return {
        "status": "healthy",
        "service": "evolution-todo-api",
        "version": "1.0.0"
    }


@app.get("/ready")
def readiness_check():
    """Readiness check - verifies database connectivity."""
    try:
        from db import engine
        from sqlmodel import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Database not ready: {str(e)}")


# Import and include routers
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router
from routes.recurrence import router as recurrence_router
from routes.search import router as search_router
from routes.bulk import router as bulk_router
from routes.history import router as history_router
from routes.notifications import router as notifications_router
from routes.preferences import router as preferences_router
from routes.stats import router as stats_router
from routes.export_import import router as export_import_router
from routes.chat import router as chat_router  # Phase III: AI Chatbot
from routes.voice import router as voice_router  # Phase III: Voice Input (Whisper)
# ChatKit Integration: Waiting for official OpenAI ChatKit SDK release
# from routes.chatkit import router as chatkit_router  # Phase III: ChatKit Integration

app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(recurrence_router)
app.include_router(search_router)
app.include_router(bulk_router)
app.include_router(history_router)
app.include_router(notifications_router)
app.include_router(preferences_router)
app.include_router(stats_router)
app.include_router(export_import_router)
app.include_router(chat_router)  # Phase III: AI Chatbot (T-CHAT-012)
app.include_router(voice_router)  # Phase III: Voice Input (T-CHAT-015)
# app.include_router(chatkit_router)  # Phase III: ChatKit Integration (T-CHATKIT-003)


# Phase III: ChatKit Integration (T-CHATKIT-003)
# NOTE: ChatKit SDK not publicly available yet - using REST API in routes/chat.py instead
# Uncomment when OpenAI releases chatkit package to PyPI
# from fastapi import Depends, HTTPException, status
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from middleware.auth import verify_token
# from chatkit_server import chatkit_server, TodoRequestContext
# import secrets


# class ChatKitSessionRequest(BaseModel):
#     """Request model for ChatKit session creation."""
#     user_id: str


# class ChatKitSessionResponse(BaseModel):
#     """Response model for ChatKit session creation."""
#     client_secret: str
#     server_url: str


# @app.post("/api/chatkit/session", response_model=ChatKitSessionResponse)
# async def create_chatkit_session(
#     request: ChatKitSessionRequest,
#     authenticated_user_id: str = Depends(verify_token)
# ):
#     """
#     Create a ChatKit session with client_secret for frontend integration.
#
#     Flow:
#     1. Verify JWT token (user is authenticated)
#     2. Generate client_secret for ChatKit session
#     3. Create RequestContext with user_id
#     4. Return client_secret and server_url to frontend
#
#     Frontend Usage:
#     ```typescript
#     // 1. Get session from backend
#     const response = await fetch('/api/chatkit/session', {
#       method: 'POST',
#       headers: {
#         'Authorization': `Bearer ${jwtToken}`,
#         'Content-Type': 'application/json'
#       },
#       body: JSON.stringify({ user_id: userId })
#     });
#     const { client_secret, server_url } = await response.json();

#     // 2. Initialize ChatKit
#     import { useChatKit } from '@openai/chatkit';
#
#     const chatkit = useChatKit({
#       clientSecret: client_secret,
#       serverUrl: server_url
#     });
#     ```
#
#     Args:
#         request: ChatKitSessionRequest with user_id
#         authenticated_user_id: User ID from JWT token
#
#     Returns:
#         ChatKitSessionResponse with client_secret and server_url
#
#     Raises:
#         HTTPException 403: If user_id doesn't match authenticated user
#
#     Task: T-CHATKIT-003
#     Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
#     """
#     # Verify user_id matches authenticated user
#     if request.user_id != authenticated_user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Cannot create session for another user"
#         )
#
#     # Generate client_secret (secure random token)
#     client_secret = secrets.token_urlsafe(32)
#
#     # Get server URL from environment or use default
#     server_url = os.getenv("CHATKIT_SERVER_URL", "http://localhost:8000/api/chatkit")
#
#     # Store client_secret in session storage (if needed for verification)
#     # For now, we trust JWT authentication on each request
#
#     return ChatKitSessionResponse(
#         client_secret=client_secret,
#         server_url=server_url
#     )


# @app.post("/api/chatkit/respond")
# async def chatkit_respond(
#     request: Request,
#     authenticated_user_id: str = Depends(verify_token)
# ):
#     """
#     ChatKit respond endpoint - handles chat requests from ChatKit frontend.
#
#     This endpoint is called by ChatKit frontend when user sends a message.
#     It delegates to ChatKitServer.respond() for processing.
#
#     Flow:
#     1. Extract user_id from JWT token
#     2. Parse request body (thread_id, message)
#     3. Create RequestContext with user_id
#     4. Call chatkit_server.respond()
#     5. Stream response events to client
#
#     Args:
#         request: FastAPI Request object
#         authenticated_user_id: User ID from JWT token
#
#     Returns:
#         Streaming response with ChatKit events
#
#     Task: T-CHATKIT-003
#     Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
#     """
#     # Parse request body
#     body = await request.json()
#     thread_id = body.get("thread_id")
#     user_message = body.get("message")
#
#     if not user_message:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Message is required"
#         )
#
#     # Create RequestContext with authenticated user
#     context = TodoRequestContext(user_id=authenticated_user_id)
#
#     # Call ChatKit server to process message
#     events = []
#     async for event in chatkit_server.respond(context, thread_id, user_message):
#         events.append(event)
#
#     return JSONResponse(content={"events": [e.dict() for e in events]})


# @app.get("/api/chatkit/threads")
# async def chatkit_list_threads(
#     authenticated_user_id: str = Depends(verify_token)
# ):
#     """
#     List all ChatKit threads (conversations) for authenticated user.
#
#     Args:
#         authenticated_user_id: User ID from JWT token
#
#     Returns:
#         List of threads with id, created_at, updated_at
#
#     Task: T-CHATKIT-003
#     Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
#     """
#     context = TodoRequestContext(user_id=authenticated_user_id)
#     threads = await chatkit_server.get_threads(context)
#     return JSONResponse(content={"threads": threads})


# @app.get("/api/chatkit/threads/{thread_id}/messages")
# async def chatkit_get_thread_messages(
#     thread_id: str,
#     authenticated_user_id: str = Depends(verify_token)
# ):
#     """
#     Get all messages in a ChatKit thread.
#
#     Args:
#         thread_id: Thread ID to get messages from
#         authenticated_user_id: User ID from JWT token
#
#     Returns:
#         List of messages with role, content, created_at
#
#     Task: T-CHATKIT-003
#     Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
#     """
#     context = TodoRequestContext(user_id=authenticated_user_id)
#     messages = await chatkit_server.get_thread_messages(context, thread_id)
#     return JSONResponse(content={"messages": messages})


# @app.delete("/api/chatkit/threads/{thread_id}")
# async def chatkit_delete_thread(
#     thread_id: str,
#     authenticated_user_id: str = Depends(verify_token)
# ):
#     """
#     Delete a ChatKit thread and all its messages.
#
#     Args:
#         thread_id: Thread ID to delete
#         authenticated_user_id: User ID from JWT token
#
#     Returns:
#         Success status
#
#     Task: T-CHATKIT-003
#     Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
#     """
#     context = TodoRequestContext(user_id=authenticated_user_id)
#     success = await chatkit_server.delete_thread(context, thread_id)
#
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Thread not found"
#         )
#
#     return JSONResponse(content={"success": True})
