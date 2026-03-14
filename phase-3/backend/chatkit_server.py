"""
ChatKit-compatible Server for Evolution Todo.

Task: T-CHATKIT-001
Spec: specs/phase-3-chatbot/spec.md

Implements ChatKit server protocol WITHOUT depending on the Python 'chatkit'
package (which is a placeholder v0.0.1 with no code).

Protocol:
  - respond(): stream events as SSE
  - get_threads(): list conversations
  - get_thread_messages(): messages in a thread
  - delete_thread(): delete conversation

All state is stored in PostgreSQL (stateless architecture).
"""
from typing import AsyncIterator, List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from sqlmodel import Session, select
import os

from models import Conversation, Message
from db import engine
from agent import run_agent


# ── Event types (ChatKit-compatible SSE events) ───────────────────────────────

@dataclass
class TextEvent:
    text: str

    def to_sse(self) -> str:
        import json
        return f"data: {json.dumps({'type': 'text', 'text': self.text})}\n\n"


@dataclass
class DoneEvent:
    thread_id: Optional[str] = None
    error: Optional[str] = None

    def to_sse(self) -> str:
        import json
        payload: Dict = {"type": "done"}
        if self.thread_id:
            payload["thread_id"] = self.thread_id
        if self.error:
            payload["error"] = self.error
        return f"data: {json.dumps(payload)}\n\n"


@dataclass
class TodoRequestContext:
    """Request context carrying authenticated user info."""
    user_id: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None


# ── ChatKit Server ────────────────────────────────────────────────────────────

class EvolutionTodoChatKitServer:
    """
    ChatKit-compatible server for Evolution Todo.

    Stateless design: all state in PostgreSQL.
    Server restart does NOT lose conversation context.
    K8s-ready: any instance can handle any request.
    """

    async def respond(
        self,
        context: TodoRequestContext,
        thread_id: Optional[str],
        user_message: str,
    ) -> AsyncIterator:
        """
        Process user message and yield SSE events.

        Flow:
        1. Load or create conversation (thread)
        2. Load history from DB
        3. Store user message
        4. Run AI agent (Agents SDK Runner.run())
        5. Store assistant response
        6. Yield TextEvent + DoneEvent
        """
        user_id = context.user_id

        with Session(engine) as session:
            # 1. Load or create conversation
            if thread_id:
                conversation = session.get(Conversation, int(thread_id))
                if not conversation or conversation.user_id != user_id:
                    yield DoneEvent(error="Thread not found")
                    return
            else:
                conversation = Conversation(user_id=user_id)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)

            conversation_id = conversation.id

            # 2. Load history from DB
            db_messages = session.exec(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            ).all()
            history = [{"role": m.role, "content": m.content} for m in db_messages]

            # 3. Store user message
            session.add(Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content=user_message,
                created_at=datetime.utcnow(),
            ))
            session.commit()

            # 4. Run AI agent (openai-agents SDK)
            try:
                assistant_response, tool_calls = await run_agent(
                    history, user_message, user_id
                )
            except Exception as e:
                print(f"❌ Agent error: {e}")
                session.add(Message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="assistant",
                    content=f"❌ Error: {e}",
                    tool_calls=[],
                    created_at=datetime.utcnow(),
                ))
                session.commit()
                yield DoneEvent(error=str(e))
                return

            # 5. Store assistant response
            session.add(Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content=assistant_response,
                tool_calls=tool_calls,
                created_at=datetime.utcnow(),
            ))
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            session.commit()

            # 6. Yield events
            yield TextEvent(text=assistant_response)
            yield DoneEvent(thread_id=str(conversation_id))

    async def get_threads(self, context: TodoRequestContext) -> List[Dict]:
        """Return all conversations for a user."""
        with Session(engine) as session:
            convs = session.exec(
                select(Conversation)
                .where(Conversation.user_id == context.user_id)
                .order_by(Conversation.updated_at.desc())
            ).all()
            return [
                {
                    "id": str(c.id),
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in convs
            ]

    async def get_thread_messages(
        self, context: TodoRequestContext, thread_id: str
    ) -> List[Dict]:
        """Return messages in a thread."""
        with Session(engine) as session:
            conv = session.get(Conversation, int(thread_id))
            if not conv or conv.user_id != context.user_id:
                return []
            msgs = session.exec(
                select(Message)
                .where(Message.conversation_id == int(thread_id))
                .order_by(Message.created_at)
            ).all()
            return [
                {
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                }
                for m in msgs
            ]

    async def delete_thread(
        self, context: TodoRequestContext, thread_id: str
    ) -> bool:
        """Delete a thread and all its messages."""
        with Session(engine) as session:
            conv = session.get(Conversation, int(thread_id))
            if not conv or conv.user_id != context.user_id:
                return False
            for msg in session.exec(
                select(Message).where(Message.conversation_id == int(thread_id))
            ).all():
                session.delete(msg)
            session.delete(conv)
            session.commit()
            return True


# Singleton
chatkit_server = EvolutionTodoChatKitServer()
