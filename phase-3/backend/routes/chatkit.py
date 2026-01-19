"""
ChatKit Integration Routes - Phase III

Task: T-CHATKIT-003
Spec: specs/phase-3-chatbot/spec.md

Provides ChatKit session management and streaming chat endpoints.
Integrates with chatkit_server.py for AI-powered task management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from middleware.auth import verify_token
from chatkit_server import chatkit_server, TodoRequestContext
import secrets
import os
import json

router = APIRouter(prefix="/api/chatkit", tags=["chatkit"])


class ChatKitSessionRequest(BaseModel):
    """Request model for ChatKit session creation."""
    user_id: str


class ChatKitSessionResponse(BaseModel):
    """Response model for ChatKit session creation."""
    client_secret: str
    server_url: str


@router.post("/session", response_model=ChatKitSessionResponse)
async def create_chatkit_session(
    request: ChatKitSessionRequest,
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Create a ChatKit session with client_secret for frontend integration.

    Flow:
    1. Verify JWT token (user is authenticated)
    2. Generate client_secret for ChatKit session
    3. Create RequestContext with user_id
    4. Return client_secret and server_url to frontend

    Frontend Usage:
    ```typescript
    // 1. Get session from backend
    const response = await fetch('/api/chatkit/session', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id: userId })
    });
    const { client_secret, server_url } = await response.json();

    // 2. Initialize ChatKit
    import { useChatKit } from '@openai/chatkit';

    const chatkit = useChatKit({
      clientSecret: client_secret,
      serverUrl: server_url
    });
    ```

    Args:
        request: ChatKitSessionRequest with user_id
        authenticated_user_id: User ID from JWT token

    Returns:
        ChatKitSessionResponse with client_secret and server_url

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user

    Task: T-CHATKIT-003
    Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
    """
    # Verify user_id matches authenticated user
    if request.user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create session for another user"
        )

    # Generate client_secret (secure random token)
    client_secret = secrets.token_urlsafe(32)

    # Get server URL from environment or use default
    server_url = os.getenv("CHATKIT_SERVER_URL", "http://localhost:8000/api/chatkit")

    # Store client_secret in session storage (if needed for verification)
    # For now, we trust JWT authentication on each request

    return ChatKitSessionResponse(
        client_secret=client_secret,
        server_url=server_url
    )


@router.post("/respond")
async def chatkit_respond(
    request: Request,
    authenticated_user_id: str = Depends(verify_token)
):
    """
    ChatKit respond endpoint - handles chat requests from ChatKit frontend.

    This endpoint is called by ChatKit frontend when user sends a message.
    It delegates to ChatKitServer.respond() for processing.

    Flow:
    1. Extract user_id from JWT token
    2. Parse request body (thread_id, message)
    3. Create RequestContext with user_id
    4. Call chatkit_server.respond()
    5. Stream response events to client

    Args:
        request: FastAPI Request object
        authenticated_user_id: User ID from JWT token

    Returns:
        Streaming response with ChatKit events

    Task: T-CHATKIT-003
    Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
    """
    # Parse request body
    body = await request.json()
    thread_id = body.get("thread_id")
    user_message = body.get("message")

    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )

    # Create RequestContext with authenticated user
    context = TodoRequestContext(user_id=authenticated_user_id)

    # Stream response events
    async def event_stream():
        try:
            async for event in chatkit_server.respond(context, thread_id, user_message):
                # Convert event to JSON and yield
                event_data = {
                    "type": event.__class__.__name__,
                    "data": event.dict() if hasattr(event, 'dict') else str(event)
                }
                yield f"data: {json.dumps(event_data)}\n\n"
        except Exception as e:
            error_event = {
                "type": "error",
                "data": {"error": str(e)}
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/threads")
async def chatkit_list_threads(
    authenticated_user_id: str = Depends(verify_token)
):
    """
    List all ChatKit threads (conversations) for authenticated user.

    Args:
        authenticated_user_id: User ID from JWT token

    Returns:
        List of threads with id, created_at, updated_at

    Task: T-CHATKIT-003
    Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
    """
    context = TodoRequestContext(user_id=authenticated_user_id)
    threads = await chatkit_server.get_threads(context)
    return JSONResponse(content={"threads": threads})


@router.get("/threads/{thread_id}/messages")
async def chatkit_get_thread_messages(
    thread_id: str,
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Get all messages in a ChatKit thread.

    Args:
        thread_id: Thread ID to get messages from
        authenticated_user_id: User ID from JWT token

    Returns:
        List of messages with role, content, created_at

    Task: T-CHATKIT-003
    Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
    """
    context = TodoRequestContext(user_id=authenticated_user_id)
    messages = await chatkit_server.get_thread_messages(context, thread_id)
    return JSONResponse(content={"messages": messages})


@router.delete("/threads/{thread_id}")
async def chatkit_delete_thread(
    thread_id: str,
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Delete a ChatKit thread and all its messages.

    Args:
        thread_id: Thread ID to delete
        authenticated_user_id: User ID from JWT token

    Returns:
        Success status

    Task: T-CHATKIT-003
    Spec: specs/phase-3-chatbot/spec.md (ChatKit Integration)
    """
    context = TodoRequestContext(user_id=authenticated_user_id)
    success = await chatkit_server.delete_thread(context, thread_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    return JSONResponse(content={"success": True})
