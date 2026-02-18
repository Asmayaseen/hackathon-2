"""
Local ChatKit SDK shim module.

Provides the types and base classes needed by chatkit_server.py
until the official OpenAI ChatKit SDK is released on PyPI.

This module implements the minimal interface required:
- ChatKitServer[RequestContext]: Base class for chat server
- RequestContext: Base dataclass for user context
- ResponseEvent, TextEvent, DoneEvent: Event types for streaming
"""
from typing import TypeVar, Generic, AsyncIterator, Optional, Any
from dataclasses import dataclass


@dataclass
class RequestContext:
    """Base request context for user-scoped operations."""
    pass


@dataclass
class ResponseEvent:
    """Base class for response events."""
    pass


@dataclass
class TextEvent(ResponseEvent):
    """Text chunk event for streaming responses."""
    text: str = ""

    def dict(self):
        return {"text": self.text}


@dataclass
class DoneEvent(ResponseEvent):
    """Completion event signaling end of response."""
    error: Optional[str] = None

    def dict(self):
        return {"error": self.error}


T = TypeVar("T", bound=RequestContext)


class ChatKitServer(Generic[T]):
    """
    Base ChatKit server class.

    Provides the interface for handling chat requests with
    user-scoped context. Subclasses should override respond()
    to implement custom chat logic.
    """

    def __init__(self):
        """Initialize ChatKit server."""
        pass

    async def respond(
        self,
        context: T,
        thread_id: Optional[str],
        user_message: str
    ) -> AsyncIterator[ResponseEvent]:
        """Process user message and yield response events."""
        raise NotImplementedError("Subclasses must implement respond()")

    async def get_threads(self, context: T):
        """List all threads for user."""
        return []
