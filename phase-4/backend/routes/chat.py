"""
Conversational chat endpoint using OpenAI Agents SDK + MCP.

Task: T-CHAT-011
Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-3, US-CHAT-5)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from models import Conversation, Message, User
from db import get_session
from middleware.auth import verify_token
from agent import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model."""
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    """Chat response model."""
    conversation_id: int
    response: str
    tool_calls: List[dict] = []


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Stateless chat endpoint for conversational task management.

    Flow:
    1. Verify user authentication
    2. Load or create conversation from database
    3. Load conversation history from database
    4. Store new user message to database
    5. Run AI agent with full conversation context
    6. Store assistant response to database
    7. Return response to client

    IMPORTANT: Server holds NO state - everything persisted to database.
    This enables:
    - Server restarts without losing conversations
    - Horizontal scaling (any server can handle any request)
    - Kubernetes-ready stateless architecture

    Args:
        user_id: User ID from URL path
        request: ChatRequest with optional conversation_id and message
        session: Database session (injected)
        authenticated_user_id: User ID from JWT token (injected)

    Returns:
        ChatResponse with conversation_id, assistant response, and tool_calls

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If conversation_id not found or doesn't belong to user
    """
    # 1. Verify user authentication
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's chat"
        )

    # 2. Load or create conversation
    if request.conversation_id:
        # Load existing conversation
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # 3. Load conversation history from database (stateless)
    messages_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)

    db_messages = session.exec(messages_query).all()
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in db_messages
    ]

    # 4. Store user message to database BEFORE processing
    # (ensures no message loss even if AI agent fails)
    user_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_msg)
    session.commit()

    # 5. Run AI agent with full conversation context
    try:
        assistant_response, tool_calls = await run_agent(
            conversation_history,
            request.message,
            user_id  # Pass user_id for MCP tool calls
        )
    except Exception as e:
        # Store error as assistant response (for debugging)
        error_msg = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=f"❌ Error processing message: {str(e)}",
            tool_calls=[],
            created_at=datetime.utcnow()
        )
        session.add(error_msg)
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI agent error: {str(e)}"
        )

    # 6. Store assistant response to database
    assistant_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=assistant_response,
        tool_calls=tool_calls,
        created_at=datetime.utcnow()
    )
    session.add(assistant_msg)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()

    # 7. Return response (server is now stateless again - ready for next request)
    return ChatResponse(
        conversation_id=conversation.id,
        response=assistant_response,
        tool_calls=tool_calls
    )


@router.get("/{user_id}/conversations", response_model=List[dict])
async def list_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    List all conversations for a user.

    Args:
        user_id: User ID from URL path
        session: Database session (injected)
        authenticated_user_id: User ID from JWT token (injected)

    Returns:
        List of conversations with metadata
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's conversations"
        )

    conversations_query = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc())

    conversations = session.exec(conversations_query).all()

    return [
        {
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        }
        for conv in conversations
    ]


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=List[dict])
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Get all messages in a conversation.

    Args:
        user_id: User ID from URL path
        conversation_id: Conversation ID to retrieve messages from
        session: Database session (injected)
        authenticated_user_id: User ID from JWT token (injected)

    Returns:
        List of messages with role, content, and timestamps
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's messages"
        )

    # Verify conversation belongs to user
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get all messages
    messages_query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)

    messages = session.exec(messages_query).all()

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "tool_calls": msg.tool_calls or [],
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]
