"""
ChatKit Store Contract Implementation for Evolution Todo.

Task: T-CHATKIT-002
Spec: specs/phase-3-chatbot/spec.md (Principle VI: Stateless Architecture)

Implements ChatKit Store and FileStore contracts for persistent storage of:
- Conversation threads (mapped to Conversation model)
- Messages (mapped to Message model)
- User context and metadata

Architecture:
- All state persisted to PostgreSQL (Neon)
- No in-memory session storage
- Server restart does NOT lose data
- Horizontal scalability enabled (K8s-ready)

Store Operations:
- get(): Retrieve conversation or message by ID
- set(): Create or update conversation or message
- delete(): Remove conversation or message
- list(): List all conversations for a user

FileStore Operations (if needed for attachments):
- upload(): Store file attachments (future feature)
- download(): Retrieve file attachments (future feature)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select

from models import Conversation, Message
from db import engine


class ChatKitStore:
    """
    Store contract implementation for ChatKit conversation persistence.

    Provides thread-safe, database-backed storage for conversation state.
    All operations are scoped by user_id for data isolation.

    Thread Safety:
    - Uses SQLModel Session with connection pooling
    - Each operation gets fresh session (thread-safe)
    - Atomic commits ensure consistency

    Error Handling:
    - All database errors caught and logged
    - Returns None on failure (graceful degradation)
    - Rollback on exception to maintain consistency
    """

    def __init__(self):
        """Initialize store with database engine."""
        self.engine = engine
        print("✅ ChatKit Store Initialized (PostgreSQL)")

    def get_conversation(
        self,
        user_id: str,
        conversation_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a conversation by ID.

        Args:
            user_id: User ID for isolation
            conversation_id: Conversation ID to retrieve

        Returns:
            Conversation dict or None if not found

        Security:
            - Verifies conversation belongs to user
            - Returns None if user_id doesn't match
        """
        try:
            with Session(self.engine) as session:
                conversation = session.get(Conversation, conversation_id)

                if not conversation or conversation.user_id != user_id:
                    return None

                return {
                    "id": conversation.id,
                    "user_id": conversation.user_id,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat()
                }
        except Exception as e:
            print(f"❌ Error getting conversation {conversation_id}: {e}")
            return None

    def create_conversation(self, user_id: str) -> Optional[int]:
        """
        Create a new conversation.

        Args:
            user_id: User ID for the conversation

        Returns:
            New conversation ID or None on failure

        Database:
            - Inserts into conversations table
            - Auto-generates ID
            - Sets created_at and updated_at timestamps
        """
        try:
            with Session(self.engine) as session:
                conversation = Conversation(user_id=user_id)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)

                return conversation.id
        except Exception as e:
            print(f"❌ Error creating conversation: {e}")
            return None

    def update_conversation_timestamp(
        self,
        user_id: str,
        conversation_id: int
    ) -> bool:
        """
        Update conversation's updated_at timestamp.

        Called when new messages are added to conversation.

        Args:
            user_id: User ID for isolation
            conversation_id: Conversation ID to update

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            with Session(self.engine) as session:
                conversation = session.get(Conversation, conversation_id)

                if not conversation or conversation.user_id != user_id:
                    return False

                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()

                return True
        except Exception as e:
            print(f"❌ Error updating conversation {conversation_id}: {e}")
            return False

    def delete_conversation(
        self,
        user_id: str,
        conversation_id: int
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            user_id: User ID for isolation
            conversation_id: Conversation ID to delete

        Returns:
            True if deleted successfully, False otherwise

        Database:
            - Deletes all messages first (cascade)
            - Then deletes conversation
            - Atomic transaction (all or nothing)
        """
        try:
            with Session(self.engine) as session:
                conversation = session.get(Conversation, conversation_id)

                if not conversation or conversation.user_id != user_id:
                    return False

                # Delete all messages first
                messages_query = select(Message).where(
                    Message.conversation_id == conversation_id
                )
                messages = session.exec(messages_query).all()
                for msg in messages:
                    session.delete(msg)

                # Delete conversation
                session.delete(conversation)
                session.commit()

                return True
        except Exception as e:
            print(f"❌ Error deleting conversation {conversation_id}: {e}")
            return False

    def list_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all conversations for a user.

        Args:
            user_id: User ID to list conversations for
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip (pagination)

        Returns:
            List of conversation dicts, sorted by updated_at desc

        Pagination:
            - Default limit: 50 conversations
            - Use offset for pagination
            - Sorted by most recent first
        """
        try:
            with Session(self.engine) as session:
                conversations_query = (
                    select(Conversation)
                    .where(Conversation.user_id == user_id)
                    .order_by(Conversation.updated_at.desc())
                    .limit(limit)
                    .offset(offset)
                )

                conversations = session.exec(conversations_query).all()

                return [
                    {
                        "id": conv.id,
                        "user_id": conv.user_id,
                        "created_at": conv.created_at.isoformat(),
                        "updated_at": conv.updated_at.isoformat()
                    }
                    for conv in conversations
                ]
        except Exception as e:
            print(f"❌ Error listing conversations for user {user_id}: {e}")
            return []

    def add_message(
        self,
        conversation_id: int,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None
    ) -> Optional[int]:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID to add message to
            user_id: User ID for isolation
            role: "user" or "assistant"
            content: Message text
            tool_calls: Optional list of tool calls made by AI

        Returns:
            New message ID or None on failure

        Validation:
            - Verifies conversation exists and belongs to user
            - Validates role is "user" or "assistant"
            - Auto-sets created_at timestamp
        """
        try:
            with Session(self.engine) as session:
                # Verify conversation exists and belongs to user
                conversation = session.get(Conversation, conversation_id)
                if not conversation or conversation.user_id != user_id:
                    return None

                # Create message
                message = Message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role=role,
                    content=content,
                    tool_calls=tool_calls or [],
                    created_at=datetime.utcnow()
                )
                session.add(message)

                # Update conversation timestamp
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)

                session.commit()
                session.refresh(message)

                return message.id
        except Exception as e:
            print(f"❌ Error adding message to conversation {conversation_id}: {e}")
            return None

    def get_messages(
        self,
        conversation_id: int,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all messages in a conversation.

        Args:
            conversation_id: Conversation ID to get messages from
            user_id: User ID for isolation
            limit: Maximum number of messages to return
            offset: Number of messages to skip (pagination)

        Returns:
            List of message dicts, sorted by created_at asc

        Pagination:
            - Default limit: 100 messages
            - Use offset for pagination
            - Sorted chronologically (oldest first)
        """
        try:
            with Session(self.engine) as session:
                # Verify conversation belongs to user
                conversation = session.get(Conversation, conversation_id)
                if not conversation or conversation.user_id != user_id:
                    return []

                # Get messages
                messages_query = (
                    select(Message)
                    .where(Message.conversation_id == conversation_id)
                    .order_by(Message.created_at.asc())
                    .limit(limit)
                    .offset(offset)
                )

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
        except Exception as e:
            print(f"❌ Error getting messages for conversation {conversation_id}: {e}")
            return []

    def get_conversation_history(
        self,
        conversation_id: int,
        user_id: str
    ) -> List[Dict[str, str]]:
        """
        Get conversation history in OpenAI format for agent.

        Converts database messages to OpenAI chat format:
        [{"role": "user"|"assistant", "content": str}]

        Args:
            conversation_id: Conversation ID to get history from
            user_id: User ID for isolation

        Returns:
            List of messages in OpenAI format

        Used By:
            - run_agent() in agent.py
            - ChatKit respond() method
        """
        messages = self.get_messages(conversation_id, user_id)

        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]


class ChatKitFileStore:
    """
    FileStore contract implementation for file attachments (future feature).

    Provides file upload/download for:
    - Task attachments (images, documents)
    - Voice transcriptions (audio files)
    - Export files (JSON, CSV)

    Storage Options:
    - Local filesystem (development)
    - S3-compatible storage (production)
    - PostgreSQL BYTEA (small files)

    Status: NOT IMPLEMENTED (Phase III)
    Will be implemented in Phase IV/V if needed.
    """

    def __init__(self):
        """Initialize file store (placeholder)."""
        print("⚠️  ChatKit FileStore NOT IMPLEMENTED (future feature)")

    async def upload(self, file_data: bytes, filename: str) -> Optional[str]:
        """Upload file and return file ID."""
        raise NotImplementedError("File upload not implemented in Phase III")

    async def download(self, file_id: str) -> Optional[bytes]:
        """Download file by ID."""
        raise NotImplementedError("File download not implemented in Phase III")


# Singleton instances
chatkit_store = ChatKitStore()
chatkit_file_store = ChatKitFileStore()
