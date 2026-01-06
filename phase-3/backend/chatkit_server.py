"""
ChatKit Python Backend Server for Evolution Todo.

Task: T-CHATKIT-001
Spec: specs/phase-3-chatbot/spec.md

Implements ChatKitServer[RequestContext] from OpenAI Agents SDK to provide
conversational task management through ChatKit frontend.

Architecture:
- Extends ChatKitServer[RequestContext] for user isolation
- Integrates with existing MCP tools (11 tools in mcp_server.py)
- Stateless design with PostgreSQL persistence
- All conversation state stored in database (Conversation + Message models)
- User authentication via RequestContext.user_id

Integration:
- MCP Tools: Defined in mcp_server.py (add_task, list_tasks, etc.)
- Agent Logic: run_agent() in agent.py
- Database: Neon PostgreSQL via models.py
- Authentication: JWT via middleware/auth.py
"""
from typing import AsyncIterator, List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from chatkit import ChatKitServer, RequestContext, ResponseEvent, TextEvent, DoneEvent
from sqlmodel import Session, select
from openai import OpenAI
import os

from models import Conversation, Message, User
from db import engine
from agent import run_agent


@dataclass
class TodoRequestContext(RequestContext):
    """
    Request context for user-scoped operations.

    Extends ChatKitServer RequestContext to include user_id for:
    - User isolation: Each user sees only their own conversations/tasks
    - MCP tool authentication: user_id passed to all tool calls
    - Database filtering: All queries scoped by user_id

    Fields:
        user_id: Authenticated user ID from JWT token
        user_name: User's display name (optional, for personalization)
        user_email: User's email (optional, for notifications)
    """
    user_id: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class EvolutionTodoChatKitServer(ChatKitServer[TodoRequestContext]):
    """
    ChatKit server implementation for Evolution Todo chatbot.

    Responsibilities:
    - Handle chat requests through OpenAI ChatKit protocol
    - Integrate with existing MCP tools for task management
    - Persist conversation history to database (stateless architecture)
    - Enforce user isolation via RequestContext

    Base Class Behavior (DO NOT override):
    - threads.list: List conversations for user
    - threads.items.list: List messages in conversation
    - threads.delete: Delete conversation

    Custom Behavior (Override respond()):
    - Process user messages through AI agent
    - Call MCP tools for task operations
    - Store messages in database
    - Stream responses to client
    """

    def __init__(self):
        """Initialize ChatKit server with database connection."""
        super().__init__()
        self.openai_client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
                     if os.getenv("GROQ_API_KEY") else None
        )
        print("✅ ChatKit Server Initialized")

    async def respond(
        self,
        context: TodoRequestContext,
        thread_id: Optional[str],
        user_message: str
    ) -> AsyncIterator[ResponseEvent]:
        """
        Process user message and generate AI response with tool execution.

        Flow:
        1. Load or create conversation (thread_id maps to conversation_id)
        2. Load conversation history from database
        3. Store user message to database
        4. Run AI agent with conversation context
        5. AI agent calls MCP tools as needed
        6. Store assistant response to database
        7. Stream response events to client

        Args:
            context: TodoRequestContext with user_id for authentication
            thread_id: Optional thread ID (conversation_id from database)
            user_message: User's input message

        Yields:
            ResponseEvent: Stream of text events and completion event

        Architecture Notes:
        - Server is STATELESS: All state in database
        - Conversation history loaded from DB on each request
        - Server restart does NOT lose conversation context
        - Any server instance can handle any request (K8s-ready)
        """
        user_id = context.user_id

        with Session(engine) as session:
            # 1. Load or create conversation
            if thread_id:
                # Convert thread_id to conversation_id (they are the same)
                conversation = session.get(Conversation, int(thread_id))
                if not conversation or conversation.user_id != user_id:
                    # Thread doesn't exist or doesn't belong to user
                    yield DoneEvent(error="Thread not found")
                    return
            else:
                # Create new conversation
                conversation = Conversation(user_id=user_id)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)

            conversation_id = conversation.id

            # 2. Load conversation history from database (STATELESS)
            messages_query = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)

            db_messages = session.exec(messages_query).all()
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in db_messages
            ]

            # 3. Store user message to database BEFORE processing
            # (Ensures no message loss even if AI agent fails)
            user_msg = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content=user_message,
                created_at=datetime.utcnow()
            )
            session.add(user_msg)
            session.commit()

            # 4. Run AI agent with full conversation context
            try:
                assistant_response, tool_calls = await run_agent(
                    conversation_history,
                    user_message,
                    user_id  # Pass user_id for MCP tool authentication
                )
            except Exception as e:
                # Log error and return error event
                print(f"❌ AI Agent Error: {e}")

                # Store error message in database
                error_msg = Message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="assistant",
                    content=f"❌ Error processing message: {str(e)}",
                    tool_calls=[],
                    created_at=datetime.utcnow()
                )
                session.add(error_msg)
                session.commit()

                yield DoneEvent(error=str(e))
                return

            # 5. Store assistant response to database
            assistant_msg = Message(
                conversation_id=conversation_id,
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

            # 6. Stream response to client
            # ChatKit expects streaming events for better UX
            yield TextEvent(text=assistant_response)
            yield DoneEvent(thread_id=str(conversation_id))

    async def get_threads(
        self,
        context: TodoRequestContext
    ) -> List[Dict]:
        """
        Get all conversations (threads) for the authenticated user.

        Called by ChatKit when client requests threads.list.

        Args:
            context: TodoRequestContext with user_id

        Returns:
            List of thread dictionaries with id, created_at, updated_at
        """
        user_id = context.user_id

        with Session(engine) as session:
            conversations_query = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc())

            conversations = session.exec(conversations_query).all()

            return [
                {
                    "id": str(conv.id),
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]

    async def get_thread_messages(
        self,
        context: TodoRequestContext,
        thread_id: str
    ) -> List[Dict]:
        """
        Get all messages in a conversation thread.

        Called by ChatKit when client requests threads.items.list.

        Args:
            context: TodoRequestContext with user_id
            thread_id: Thread ID (conversation_id)

        Returns:
            List of message dictionaries with role, content, timestamp
        """
        user_id = context.user_id

        with Session(engine) as session:
            # Verify conversation belongs to user
            conversation = session.get(Conversation, int(thread_id))
            if not conversation or conversation.user_id != user_id:
                return []

            # Get all messages
            messages_query = select(Message).where(
                Message.conversation_id == int(thread_id)
            ).order_by(Message.created_at)

            messages = session.exec(messages_query).all()

            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]

    async def delete_thread(
        self,
        context: TodoRequestContext,
        thread_id: str
    ) -> bool:
        """
        Delete a conversation thread and all its messages.

        Called by ChatKit when client requests threads.delete.

        Args:
            context: TodoRequestContext with user_id
            thread_id: Thread ID to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        user_id = context.user_id

        with Session(engine) as session:
            conversation = session.get(Conversation, int(thread_id))
            if not conversation or conversation.user_id != user_id:
                return False

            # Delete all messages first (cascade)
            messages_query = select(Message).where(
                Message.conversation_id == int(thread_id)
            )
            messages = session.exec(messages_query).all()
            for msg in messages:
                session.delete(msg)

            # Delete conversation
            session.delete(conversation)
            session.commit()

            return True


# Singleton instance
chatkit_server = EvolutionTodoChatKitServer()
