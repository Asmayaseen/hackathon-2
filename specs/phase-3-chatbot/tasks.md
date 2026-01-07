# Phase III: AI-Powered Todo Chatbot - Tasks Breakdown

**Version**: 1.0.0
**Status**: Ready for Implementation
**Constitution**: v1.0.0 Compliant
**Spec**: `specs/phase-3-chatbot/spec.md`
**Plan**: `specs/phase-3-chatbot/plan.md`

---

## Task Organization

Tasks are grouped by user story and marked as:
- **[P]** - Parallelizable (can run simultaneously)
- **[S]** - Sequential (depends on previous tasks)

---

## Group 1: Database Foundation (US-CHAT-5)

### T-CHAT-001: Add Conversation and Message Models [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 15 minutes
**Dependencies**: None

**Description**: Extend `phase-2/backend/models.py` with Conversation and Message models for chat persistence.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-1, FR-CHAT-2
- `specs/phase-3-chatbot/plan.md` → Component 1

**Acceptance Criteria**:
- ✅ Conversation model created with fields: id, user_id, created_at, updated_at
- ✅ Message model created with fields: id, conversation_id, user_id, role, content, tool_calls, created_at
- ✅ Foreign key constraints defined
- ✅ Indexes added on user_id and conversation_id

**Implementation**:
```python
# File: phase-2/backend/models.py
# Add after existing models

class Conversation(SQLModel, table=True):
    """Chat conversation sessions for stateless persistence."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Individual chat messages in conversations."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(...)  # "user" | "assistant"
    content: str = Field(...)
    tool_calls: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Test Scenario**:
```python
GIVEN database connection exists
WHEN Conversation and Message models are imported
THEN SQLModel creates tables in Neon PostgreSQL
AND foreign keys are enforced
```

---

### T-CHAT-002: Create Database Migration Script [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 10 minutes
**Dependencies**: T-CHAT-001

**Description**: Create migration script to add conversations and messages tables to existing database.

**Spec Reference**:
- `specs/phase-3-chatbot/plan.md` → Component 1

**Acceptance Criteria**:
- ✅ Migration script creates conversations table
- ✅ Migration script creates messages table
- ✅ Script is idempotent (can run multiple times safely)
- ✅ Indexes are created
- ✅ Run successfully on Neon database

**Implementation**:
```python
# File: phase-2/backend/migrations/003_add_chat_tables.py
"""
Add conversations and messages tables for Phase III chatbot.

Task: T-CHAT-002
Spec: specs/phase-3-chatbot/spec.md
"""
from sqlmodel import SQLModel, create_engine
from models import Conversation, Message
import os

def run_migration():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    # Create tables
    SQLModel.metadata.create_all(engine, tables=[
        Conversation.__table__,
        Message.__table__
    ])

    print("✅ Migration complete: conversations + messages tables created")

if __name__ == "__main__":
    run_migration()
```

**Test Scenario**:
```bash
GIVEN Neon database is running
WHEN python migrations/003_add_chat_tables.py is executed
THEN conversations and messages tables are created
AND running migration again does not error (idempotent)
```

---

## Group 2: MCP Server Implementation (US-CHAT-1 to US-CHAT-4)

### T-CHAT-003: Create MCP Server Foundation [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 30 minutes
**Dependencies**: None (can run in parallel with Group 1)

**Description**: Initialize MCP Server using Official MCP Python SDK with basic structure.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-4
- `specs/phase-3-chatbot/plan.md` → Component 2

**Acceptance Criteria**:
- ✅ MCP Server initialized with SDK
- ✅ Server can list available tools
- ✅ Server can handle tool calls
- ✅ Internal HTTP client configured for calling FastAPI routes

**Implementation**:
```python
# File: phase-2/backend/mcp_server.py
"""
MCP Server for Evolution Todo - Exposes task operations as AI tools.

Task: T-CHAT-003
Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-4)
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Sequence
import httpx
import os

# Initialize MCP Server
mcp_server = Server("evolution-todo-mcp")

# Internal API base URL
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

@mcp_server.list_tools()
async def list_tools() -> Sequence[Tool]:
    """Return list of available tools for AI agent."""
    return []  # Will be populated in subsequent tasks

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Execute tool and return result."""
    # Tool implementations will be added in subsequent tasks
    pass
```

**Test Scenario**:
```python
GIVEN MCP Server is initialized
WHEN list_tools() is called
THEN empty list is returned (foundation ready)
```

---

### T-CHAT-004: Implement add_task MCP Tool [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 20 minutes
**Dependencies**: T-CHAT-003

**Description**: Implement add_task MCP tool that calls POST /api/{user_id}/tasks endpoint.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-4 (Tool #1)

**Acceptance Criteria**:
- ✅ add_task tool defined with schema
- ✅ Calls POST /api/{user_id}/tasks internally
- ✅ Returns formatted success message
- ✅ Handles errors gracefully

**Implementation**:
```python
# Add to phase-2/backend/mcp_server.py

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
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "none"], "default": "none"},
                    "due_date": {"type": "string", "format": "date-time", "description": "When task is due"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"},
                    "recurrence_pattern": {"type": "string", "enum": ["daily", "weekly", "monthly"], "description": "Recurring pattern"}
                },
                "required": ["user_id", "title"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    if name == "add_task":
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/api/{arguments['user_id']}/tasks",
                json={
                    "title": arguments["title"],
                    "description": arguments.get("description"),
                    "priority": arguments.get("priority", "none"),
                    "due_date": arguments.get("due_date"),
                    "tags": arguments.get("tags", []),
                    "recurrence_pattern": arguments.get("recurrence_pattern")
                }
            )
            result = response.json()
            return [TextContent(
                type="text",
                text=f"✅ Task created: '{result['title']}' (ID: {result['id']})"
            )]
```

**Test Scenario**:
```python
GIVEN MCP Server is running
WHEN add_task is called with user_id="test-user", title="Buy milk"
THEN POST /api/test-user/tasks is called
AND task is created in database
AND success message is returned
```

---

### T-CHAT-005: Implement list_tasks MCP Tool [P]

**Priority**: P1 (Critical)
**Estimated Effort**: 20 minutes
**Dependencies**: T-CHAT-003

**Description**: Implement list_tasks MCP tool with filtering and sorting support.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-4 (Tool #2)

**Implementation**: (Similar pattern to T-CHAT-004, calls GET /api/{user_id}/tasks)

---

### T-CHAT-006: Implement complete_task MCP Tool [P]

**Priority**: P1 (Critical)
**Estimated Effort**: 15 minutes
**Dependencies**: T-CHAT-003

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-4 (Tool #3)

**Implementation**: Calls PATCH /api/{user_id}/tasks/{id}/complete

---

### T-CHAT-007: Implement delete_task MCP Tool [P]

**Priority**: P1 (Critical)
**Estimated Effort**: 15 minutes
**Dependencies**: T-CHAT-003

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-4 (Tool #4)

**Implementation**: Calls DELETE /api/{user_id}/tasks/{id}

---

### T-CHAT-008: Implement update_task MCP Tool [P]

**Priority**: P1 (Critical)
**Estimated Effort**: 20 minutes
**Dependencies**: T-CHAT-003

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-4 (Tool #5)

**Implementation**: Calls PUT /api/{user_id}/tasks/{id}

---

### T-CHAT-009: Implement Advanced MCP Tools (6-11) [P]

**Priority**: P2 (Bonus)
**Estimated Effort**: 60 minutes
**Dependencies**: T-CHAT-003

**Description**: Implement 6 advanced tools for bonus points.

**Tools**:
6. search_tasks → Calls GET /api/{user_id}/tasks/search
7. set_priority → Calls PUT /api/{user_id}/tasks/{id}
8. add_tags → Calls PUT /api/{user_id}/tasks/{id}
9. schedule_reminder → Calls POST /api/{user_id}/notifications
10. get_recurring_tasks → Calls GET /api/{user_id}/tasks/recurrence
11. analytics_summary → Calls GET /api/{user_id}/stats

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-4 (Tools #6-11)

---

## Group 3: OpenAI Agents SDK Integration (US-CHAT-1 to US-CHAT-4)

### T-CHAT-010: Create AI Agent with OpenAI Agents SDK [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 30 minutes
**Dependencies**: T-CHAT-004 through T-CHAT-008

**Description**: Initialize OpenAI Agents SDK with instructions and MCP tools.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → US-CHAT-1, US-CHAT-7
- `specs/phase-3-chatbot/plan.md` → Component 3

**Acceptance Criteria**:
- ✅ OpenAI Agents SDK installed and configured
- ✅ Agent instructions include natural language understanding for English + Urdu
- ✅ Agent has access to all MCP tools
- ✅ Agent can process conversation history

**Implementation**:
```python
# File: phase-2/backend/agent.py
"""
OpenAI Agents SDK integration for Evolution Todo.

Task: T-CHAT-010
Spec: specs/phase-3-chatbot/spec.md
"""
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AGENT_INSTRUCTIONS = """
You are Evolution Todo Assistant, a helpful AI for managing tasks.

CAPABILITIES:
- Understand natural language in English and Urdu
- Extract task details: title, priority, due dates, tags, recurrence
- Create, update, complete, delete, and search tasks
- Provide analytics and summaries

BEHAVIOR:
- Be friendly and conversational
- Confirm destructive actions (delete)
- Format lists clearly with emojis: ✅ ⏳ 🔴
- Detect language and respond in same language
- Parse dates smartly: "tomorrow" → next day, "Friday" → next Friday

EXAMPLES:
User: "Add a task to buy groceries tomorrow"
→ add_task(title="Buy groceries", due_date=<tomorrow>)

User: "ہفتہ وار گروسری شاپنگ کا کام بنائیں"
→ add_task(title="گروسری شاپنگ", recurrence_pattern="weekly")
→ Respond: "✅ ہفتہ وار کام بنایا گیا"
"""

async def run_agent(conversation_history: list, user_message: str, user_id: str):
    """
    Run AI agent with conversation context.

    Args:
        conversation_history: Previous messages [{role, content}]
        user_message: New user message
        user_id: Current user ID (for tool calls)

    Returns:
        (assistant_response, tool_calls)
    """
    from openai.agents import Runner

    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]

    # TODO: Add MCP tools to agent configuration
    runner = Runner(
        instructions=AGENT_INSTRUCTIONS,
        model="gpt-4o-2024-11-20",
        client=client
    )

    result = await runner.run(messages=messages)
    return result.content, result.tool_calls or []
```

**Test Scenario**:
```python
GIVEN OpenAI API key is configured
WHEN run_agent is called with "Add task to test"
THEN agent processes message
AND selects add_task tool
AND returns confirmation message
```

---

## Group 4: Chat API Endpoint (US-CHAT-1 to US-CHAT-5)

### T-CHAT-011: Create Chat API Endpoint [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 45 minutes
**Dependencies**: T-CHAT-002, T-CHAT-010

**Description**: Implement POST /api/{user_id}/chat endpoint with stateless architecture.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → FR-CHAT-3, US-CHAT-5
- `specs/phase-3-chatbot/plan.md` → Component 4

**Acceptance Criteria**:
- ✅ Endpoint requires JWT authentication
- ✅ Loads conversation from database (or creates new)
- ✅ Loads message history from database
- ✅ Stores user message before processing
- ✅ Calls AI agent with full context
- ✅ Stores assistant response to database
- ✅ Returns response to client
- ✅ Server holds NO state (stateless)

**Implementation**: See `specs/phase-3-chatbot/plan.md` → Component 4 (full code)

**Test Scenario**:
```python
GIVEN user is authenticated
WHEN POST /api/{user_id}/chat with message="Test"
THEN conversation is created/loaded from DB
AND message history is loaded
AND AI agent processes message
AND response is stored to DB
AND response is returned to client

GIVEN server restarts
WHEN same user sends another message
THEN previous conversation history is loaded
AND conversation continues seamlessly
```

---

### T-CHAT-012: Register Chat Route in Main App [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 5 minutes
**Dependencies**: T-CHAT-011

**Description**: Add chat router to FastAPI main application.

**Implementation**:
```python
# File: phase-2/backend/main.py
# Add import
from routes.chat import router as chat_router

# Add router
app.include_router(chat_router)
```

---

## Group 5: ChatKit Frontend (US-CHAT-1, US-CHAT-6, US-CHAT-7)

### T-CHAT-013: Install ChatKit and OpenAI Dependencies [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**Description**: Install OpenAI ChatKit and required dependencies.

**Implementation**:
```bash
cd phase-2/frontend
npm install @openai/chatkit openai
```

**Acceptance Criteria**:
- ✅ @openai/chatkit installed
- ✅ openai SDK installed
- ✅ No dependency conflicts

---

### T-CHAT-014: Create ChatKit Page [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 40 minutes
**Dependencies**: T-CHAT-013

**Description**: Create chat page with ChatKit integration.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → US-CHAT-1, US-CHAT-6, US-CHAT-7
- `specs/phase-3-chatbot/plan.md` → Component 5

**Acceptance Criteria**:
- ✅ ChatKit component renders
- ✅ Sends messages to POST /api/{user_id}/chat
- ✅ Displays AI responses
- ✅ Persists conversation_id
- ✅ Voice input enabled
- ✅ Urdu language support configured

**Implementation**: See `specs/phase-3-chatbot/plan.md` → Component 5

---

### T-CHAT-015: Add Voice Input Support [P]

**Priority**: P2 (Bonus +200 points)
**Estimated Effort**: 30 minutes
**Dependencies**: T-CHAT-014

**Description**: Enable voice input via ChatKit voice configuration.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → US-CHAT-6

**Implementation**:
```typescript
<ChatKit
  voice={{
    enabled: true,
    language: ['en-US', 'ur-PK']  // English + Urdu
  }}
  onVoiceInput={handleVoiceTranscription}
/>
```

---

### T-CHAT-016: Configure Urdu Language Support [P]

**Priority**: P2 (Bonus +100 points)
**Estimated Effort**: 20 minutes
**Dependencies**: T-CHAT-014

**Description**: Configure ChatKit and AI agent for Urdu language detection and response.

**Spec Reference**:
- `specs/phase-3-chatbot/spec.md` → US-CHAT-7

**Implementation**: Already in agent instructions (T-CHAT-010)

---

## Group 6: Deployment and Configuration (US-CHAT-1 to US-CHAT-8)

### T-CHAT-017: Set Environment Variables [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**Description**: Configure environment variables for Phase III.

**Backend** (`.env`):
```bash
OPENAI_API_KEY=sk-...
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://...
```

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<from-openai-settings>
```

---

### T-CHAT-018: Deploy Frontend to Vercel [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 15 minutes
**Dependencies**: T-CHAT-014

**Description**: Deploy ChatKit frontend to Vercel.

**Steps**:
1. Push code to GitHub
2. Vercel auto-deploys
3. Set environment variables in Vercel
4. Get production URL

---

### T-CHAT-019: Configure OpenAI Domain Allowlist [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 10 minutes
**Dependencies**: T-CHAT-018

**Description**: Add Vercel domain to OpenAI allowlist for ChatKit security.

**Steps**:
1. Visit: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Add domain: `https://your-app.vercel.app`
3. Get domain key
4. Update `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in Vercel

---

### T-CHAT-020: Test End-to-End Flow [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 30 minutes
**Dependencies**: All previous tasks

**Description**: Test complete Phase III functionality.

**Test Cases**:
1. ✅ Natural language task creation
2. ✅ List/filter tasks via chat
3. ✅ Complete and delete tasks via chat
4. ✅ Update task details via chat
5. ✅ Server restart → conversation persists
6. ✅ Voice input → task created (Bonus)
7. ✅ Urdu input → Urdu response (Bonus)
8. ✅ Advanced features: priorities, tags, recurring (Bonus)

---

### T-CHAT-021: Record 90-Second Demo Video [S]

**Priority**: P1 (Critical)
**Estimated Effort**: 30 minutes
**Dependencies**: T-CHAT-020

**Description**: Record demo showing all Phase III features.

**Content**:
1. Intro (5s): "Phase III - AI Todo Chatbot"
2. Natural language task creation (10s)
3. List and filter tasks (10s)
4. Complete/delete via chat (10s)
5. Update tasks (10s)
6. Voice input demo (10s) - Bonus
7. Urdu language demo (10s) - Bonus
8. Advanced features (priorities, tags) (10s) - Bonus
9. Stateless restart test (10s)
10. Outro (5s): "900 points targeted!"

**Tool**: NotebookLM or screen recording

---

## Summary

### Task Count: 21 Total
- **Critical (P1)**: 17 tasks
- **Bonus (P2)**: 4 tasks

### Estimated Total Time: 6-8 hours

### Parallelization Opportunities:
- Group 2 Tasks (MCP tools 5-8) can run in parallel
- Task T-CHAT-009 (advanced tools) can run parallel with Group 3-4
- Tasks T-CHAT-015, T-CHAT-016 can run parallel with other frontend work

### Dependencies Graph:
```
T-CHAT-001 → T-CHAT-002
                ↓
T-CHAT-003 → T-CHAT-004 → T-CHAT-010 → T-CHAT-011 → T-CHAT-012
       ↓ → [T-CHAT-005 to T-CHAT-009]      ↓            ↓
                                       T-CHAT-013 → T-CHAT-014 → T-CHAT-020 → T-CHAT-021
                                                      ↓
                                              [T-CHAT-015, T-CHAT-016]
                                                      ↓
                                              [T-CHAT-017 to T-CHAT-019]
```

---

**Next Step**: Implementation via Claude Code (no manual coding per constitution)

**References**:
- Specification: `specs/phase-3-chatbot/spec.md`
- Plan: `specs/phase-3-chatbot/plan.md`
- Constitution: `.specify/memory/constitution.md`
