# Phase III: AI-Powered Todo Chatbot - Implementation Plan

**Version**: 1.0.0
**Status**: Draft
**Constitution**: v1.0.0 Compliant
**Spec Reference**: `specs/phase-3-chatbot/spec.md`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PHASE III ARCHITECTURE                          │
│                        (Stateless + Event-Driven)                        │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ ChatKit Frontend │ (Next.js 16 + OpenAI ChatKit + Voice Input)
│ + Urdu Support   │
└────────┬─────────┘
         │ HTTP POST /api/{user_id}/chat
         │ Authorization: Bearer <JWT>
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ FastAPI Backend (Stateless)                                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Chat Endpoint (/api/{user_id}/chat)                         │ │
│ │ 1. Verify JWT authentication                                │ │
│ │ 2. Load conversation history from DB                        │ │
│ │ 3. Append new user message                                  │ │
│ │ 4. Invoke OpenAI Agents SDK                                 │ │
│ │ 5. Store assistant response to DB                           │ │
│ │ 6. Return response to client                                │ │
│ └──────────────────┬──────────────────────────────────────────┘ │
│                    │                                             │
│                    ▼                                             │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ OpenAI Agents SDK Runner                                    │ │
│ │ - Model: gpt-4o-2024-11-20                                  │ │
│ │ - Instructions: Natural language todo assistant             │ │
│ │ - Tools: 11 MCP tools (via function calling)                │ │
│ │ - Context: Conversation history + current message           │ │
│ └──────────────────┬──────────────────────────────────────────┘ │
│                    │                                             │
│                    ▼                                             │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ MCP Server (Official Python SDK)                            │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ Tool 1: add_task(user_id, title, ...)                   │ │ │
│ │ │ Tool 2: list_tasks(user_id, filters, ...)               │ │ │
│ │ │ Tool 3: complete_task(user_id, task_id)                 │ │ │
│ │ │ Tool 4: delete_task(user_id, task_id)                   │ │ │
│ │ │ Tool 5: update_task(user_id, task_id, ...)              │ │ │
│ │ │ Tool 6: search_tasks(user_id, query, ...)               │ │ │
│ │ │ Tool 7: set_priority(user_id, task_id, priority)        │ │ │
│ │ │ Tool 8: add_tags(user_id, task_id, tags)                │ │ │
│ │ │ Tool 9: schedule_reminder(user_id, task_id, datetime)   │ │ │
│ │ │ Tool 10: get_recurring_tasks(user_id, pattern)          │ │ │
│ │ │ Tool 11: analytics_summary(user_id)                     │ │ │
│ │ └──────────────────┬──────────────────────────────────────┘ │ │
│ │                    │ Calls existing FastAPI routes          │ │
│ │                    ▼                                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                    │                                             │
│                    ▼                                             │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Existing Task Routes                                        │ │
│ │ - POST /api/{user_id}/tasks (create)                        │ │
│ │ - GET /api/{user_id}/tasks (list)                           │ │
│ │ - PATCH /api/{user_id}/tasks/{id}/complete                  │ │
│ │ - DELETE /api/{user_id}/tasks/{id}                          │ │
│ │ - PUT /api/{user_id}/tasks/{id} (update)                    │ │
│ │ - GET /api/{user_id}/tasks/search (search)                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
└──────────────────────┬────────────────────────────────────────────┘
                       │
                       ▼
          ┌───────────────────────────┐
          │ Neon PostgreSQL Database  │
          │ ┌────────────────────────┐│
          │ │ conversations          ││
          │ │ messages               ││
          │ │ tasks (existing)       ││
          │ │ users (existing)       ││
          │ └────────────────────────┘│
          └───────────────────────────┘
```

---

## Component Breakdown

### 1. Database Layer (New Models)

**File**: `phase-2/backend/models.py` (extend existing)

```python
class Conversation(SQLModel, table=True):
    """Chat conversation sessions."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Chat messages in conversations."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(...)  # "user" | "assistant"
    content: str = Field(...)
    tool_calls: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Migration Script**: `phase-2/backend/migrations/add_chat_tables.py`

---

### 2. MCP Server Implementation

**File**: `phase-2/backend/mcp_server.py`

```python
"""
MCP Server using Official MCP Python SDK.

Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-4)
Task: T-CHAT-001
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Sequence
import httpx

# Initialize MCP Server
mcp_server = Server("evolution-todo-mcp")

# Tool definitions
@mcp_server.list_tools()
async def list_tools() -> Sequence[Tool]:
    return [
        Tool(
            name="add_task",
            description="Create a new task with optional priority, due date, tags, and recurrence",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "title": {"type": "string", "description": "Task title (required)"},
                    "description": {"type": "string", "description": "Task description (optional)"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "none"]},
                    "due_date": {"type": "string", "format": "date-time"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "recurrence_pattern": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
                },
                "required": ["user_id", "title"]
            }
        ),
        # ... (10 more tools)
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    if name == "add_task":
        # Call existing FastAPI route
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000/api/{arguments['user_id']}/tasks",
                json={
                    "title": arguments["title"],
                    "description": arguments.get("description"),
                    "priority": arguments.get("priority", "none"),
                    "due_date": arguments.get("due_date"),
                    "tags": arguments.get("tags", []),
                    "recurrence_pattern": arguments.get("recurrence_pattern")
                },
                headers={"Authorization": f"Bearer {arguments['token']}"}
            )
            result = response.json()
            return [TextContent(
                type="text",
                text=f"✅ Task created: '{result['title']}' (ID: {result['id']})"
            )]
    # ... (handle other tools)
```

**Pattern**: Each MCP tool calls corresponding FastAPI route internally

---

### 3. OpenAI Agents SDK Integration

**File**: `phase-2/backend/agent.py`

```python
"""
OpenAI Agents SDK integration for conversational AI.

Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-3)
Task: T-CHAT-002
"""
from openai import OpenAI
from openai.agents import Agent, Runner
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define AI Agent
todo_agent = Agent(
    name="Evolution Todo Assistant",
    model="gpt-4o-2024-11-20",
    instructions="""
    You are a helpful AI assistant for managing todo tasks.

    CAPABILITIES:
    - Understand natural language task commands in English and Urdu
    - Extract task details (title, priority, due dates, tags, recurrence)
    - Help users create, update, complete, delete, and search tasks
    - Provide task analytics and summaries
    - Support voice input (transcribed text)

    BEHAVIOR:
    - Always be friendly and conversational
    - Confirm actions before executing (e.g., "Do you want to delete this task?")
    - Format task lists clearly with status indicators
    - Detect language (English/Urdu) and respond in the same language
    - Extract dates smartly: "tomorrow" → next day, "Friday" → next Friday
    - Handle ambiguity: ask clarifying questions if needed

    TOOLS:
    You have access to 11 MCP tools for task management.
    Use them intelligently based on user intent.

    EXAMPLES:
    User: "Add a task to buy groceries tomorrow"
    → Call add_task(title="Buy groceries", due_date=<tomorrow>)

    User: "Show my high priority tasks"
    → Call list_tasks(priority="high")

    User: "ہفتہ وار گروسری شاپنگ کا کام بنائیں"
    → Call add_task(title="گروسری شاپنگ", recurrence_pattern="weekly")
    → Respond in Urdu: "✅ ہفتہ وار کام بنایا گیا"
    """,
    tools=[]  # Will be populated with MCP tools
)

async def run_agent(conversation_history: list, user_message: str):
    """
    Run the AI agent with conversation history and new message.

    Returns: (assistant_response, tool_calls)
    """
    messages = conversation_history + [{"role": "user", "content": user_message}]

    runner = Runner(agent=todo_agent, client=client)
    result = await runner.run(messages=messages)

    return result.content, result.tool_calls
```

---

### 4. Chat API Endpoint

**File**: `phase-2/backend/routes/chat.py` (new)

```python
"""
Conversational chat endpoint using OpenAI Agents SDK + MCP.

Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-3)
Task: T-CHAT-003
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
    Stateless chat endpoint.

    Flow:
    1. Verify user authentication
    2. Load or create conversation
    3. Load conversation history from DB
    4. Append new user message to history
    5. Run AI agent with full context
    6. Store user message and assistant response to DB
    7. Return response

    Server holds NO state - everything in database.
    """
    # 1. Verify user
    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2. Load or create conversation
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # 3. Load conversation history from DB
    messages_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)

    db_messages = session.exec(messages_query).all()
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in db_messages
    ]

    # 4. Store user message
    user_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_msg)
    session.commit()

    # 5. Run AI agent
    assistant_response, tool_calls = await run_agent(
        conversation_history,
        request.message
    )

    # 6. Store assistant response
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

    # 7. Return response (stateless - server ready for next request)
    return ChatResponse(
        conversation_id=conversation.id,
        response=assistant_response,
        tool_calls=tool_calls
    )
```

---

### 5. ChatKit Frontend

**File**: `phase-2/frontend/src/app/chat/page.tsx` (new)

```typescript
/**
 * ChatKit-based conversational interface.
 *
 * Spec: specs/phase-3-chatbot/spec.md (US-CHAT-1 through US-CHAT-8)
 * Task: T-CHAT-004
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChatKit } from '@openai/chatkit';

export default function ChatPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const id = localStorage.getItem('user_id');

    if (!token || !id) {
      router.push('/auth/signin');
      return;
    }

    setUserId(id);
  }, [router]);

  const handleSendMessage = async (message: string) => {
    if (!userId) return;

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: message
        })
      }
    );

    const data = await response.json();
    setConversationId(data.conversation_id);
    return data.response;
  };

  if (!userId) return <div>Loading...</div>;

  return (
    <div className="h-screen">
      <ChatKit
        api={{
          url: process.env.NEXT_PUBLIC_API_URL,
          key: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY
        }}
        theme="dark"
        voice={{
          enabled: true,  // Voice input support
          language: ['en-US', 'ur-PK']  // English + Urdu
        }}
        onMessage={handleSendMessage}
        placeholder="Type or speak your task... (English/Urdu) 🎤"
      />
    </div>
  );
}
```

**Environment Variables** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<your-domain-key>
```

---

## Technical Decisions

### Decision 1: MCP Tools Call Existing Routes

**Options Considered:**
1. MCP tools directly access database
2. MCP tools call existing FastAPI routes
3. Refactor routes into service layer

**Chosen**: Option 2 (MCP → FastAPI routes)

**Rationale**:
- ✅ Reuses existing authentication + validation logic
- ✅ No code duplication
- ✅ Maintains single source of truth for business logic
- ✅ Easier to test and debug
- ❌ Slightly higher latency (internal HTTP call)

---

### Decision 2: Stateless Chat with Database Persistence

**Options Considered:**
1. In-memory conversation state
2. Database-backed conversations
3. Redis cache with DB fallback

**Chosen**: Option 2 (Database only)

**Rationale**:
- ✅ Meets constitution requirement (stateless architecture)
- ✅ Enables horizontal scaling for Phase IV/V
- ✅ Survives server restarts
- ✅ Simpler architecture for hackathon
- ❌ Slightly slower than Redis (acceptable for MVP)

---

### Decision 3: OpenAI Agents SDK vs LangChain

**Options Considered:**
1. OpenAI Agents SDK
2. LangChain
3. Custom agent implementation

**Chosen**: Option 1 (OpenAI Agents SDK)

**Rationale**:
- ✅ Required by hackathon specs (constitution III)
- ✅ Official support from OpenAI
- ✅ Built-in MCP integration
- ✅ Simpler API than LangChain
- ✅ Better performance for GPT-4 models

---

### Decision 4: Voice Input via OpenAI Whisper

**Options Considered:**
1. Browser Web Speech API
2. OpenAI Whisper API
3. Third-party service (AssemblyAI)

**Chosen**: Option 2 (Whisper API)

**Rationale**:
- ✅ Better multilingual support (English + Urdu)
- ✅ Higher accuracy than browser API
- ✅ Consistent with OpenAI ecosystem
- ✅ Bonus points for voice commands (+200)

---

## Data Flow Diagrams

### Diagram 1: Chat Message Flow

```
User types: "Add task to buy milk tomorrow"
    ↓
ChatKit sends POST /api/{user_id}/chat
    ↓
FastAPI Chat Endpoint:
  1. Verify JWT ✓
  2. Load conversation from DB (or create new)
  3. Load message history from DB
  4. Store user message to DB
    ↓
OpenAI Agents SDK:
  1. Analyze message with GPT-4
  2. Identify intent: "create task"
  3. Extract params: title="Buy milk", due_date=<tomorrow>
  4. Select tool: add_task
  5. Execute tool via MCP Server
    ↓
MCP Server:
  1. Call POST /api/{user_id}/tasks internally
  2. Return result: {id: 42, title: "Buy milk"}
    ↓
OpenAI Agents SDK:
  1. Format response: "✅ Task 'Buy milk' added for tomorrow"
    ↓
FastAPI Chat Endpoint:
  1. Store assistant response to DB
  2. Update conversation timestamp
  3. Return response to client
    ↓
ChatKit displays: "✅ Task 'Buy milk' added for tomorrow"
```

---

### Diagram 2: Stateless Restart Resilience

```
User has conversation_id=99 with 10 messages
    ↓
Server crashes 💥
    ↓
Server restarts
    ↓
User reloads ChatKit
    ↓
ChatKit sends POST /api/{user_id}/chat with conversation_id=99
    ↓
FastAPI Chat Endpoint:
  1. Load conversation #99 from DB ✓
  2. Load all 10 messages from DB ✓
  3. Conversation history restored
    ↓
User continues chatting seamlessly
```

---

## Implementation Dependencies

### Phase II Components (Existing - Required)

1. ✅ User authentication (JWT)
2. ✅ Task model with advanced fields (priority, tags, due_date, recurrence)
3. ✅ Task CRUD routes
4. ✅ Search endpoint
5. ✅ Database connection (Neon PostgreSQL)

### Phase III New Components (To Implement)

1. ⏳ Conversation model
2. ⏳ Message model
3. ⏳ Database migration for chat tables
4. ⏳ MCP Server with 11 tools
5. ⏳ OpenAI Agents SDK integration
6. ⏳ Chat endpoint (`/api/{user_id}/chat`)
7. ⏳ ChatKit frontend page
8. ⏳ Voice input integration
9. ⏳ Urdu language support

---

## Testing Strategy

### Unit Tests

- MCP tools return correct responses
- Agent instructions parse natural language correctly
- Conversation/Message models validate properly

### Integration Tests

- Chat endpoint creates conversation
- Messages persist to database
- MCP tools call FastAPI routes successfully
- Agent selects correct tools for commands

### End-to-End Tests

- User sends message → task is created
- Server restart → conversation history loads
- Voice input → transcribed and processed
- Urdu input → detected and responded to

---

## Deployment Architecture

### Development
- Frontend: `http://localhost:3000/chat`
- Backend: `http://localhost:8000`
- Database: Neon PostgreSQL (shared)

### Production (Phase III)
- Frontend: Vercel (ChatKit page)
  - Domain: `https://your-app.vercel.app/chat`
  - Allowlist domain in OpenAI settings
- Backend: Hugging Face Spaces (same as Phase II)
- Database: Neon PostgreSQL (same)

**Domain Allowlist Setup**:
1. Deploy frontend to Vercel
2. Get production URL
3. Add to OpenAI: https://platform.openai.com/settings/organization/security/domain-allowlist
4. Get domain key
5. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in Vercel

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| **OpenAI API rate limits** | High | Implement request throttling, use GPT-4 Mini for testing |
| **MCP SDK learning curve** | Medium | Start with simple tools, reference official docs |
| **Urdu NLU accuracy** | Medium | Test with GPT-4, provide clear examples in agent instructions |
| **Voice transcription cost** | Low | Use OpenAI Whisper, cache transcriptions if needed |
| **Stateless performance** | Low | Database queries < 100ms, acceptable for MVP |

---

## Next Steps

Following Spec-Driven workflow:

1. ✅ Specify - COMPLETE
2. ✅ Plan - COMPLETE (this document)
3. ⏳ Tasks - Create atomic task breakdown
4. ⏳ Implement - Execute via Claude Code

**References:**
- Specification: `specs/phase-3-chatbot/spec.md`
- Constitution: `.specify/memory/constitution.md`
- Phase II Backend: `phase-2/backend/`
- Phase II Frontend: `phase-2/frontend/`
- Hackathon Guide: `hackathon.md` (Phase III section)
