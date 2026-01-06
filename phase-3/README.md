# Phase III: AI-Powered Todo Chatbot

**Status**: 🚧 In Progress
**Target Points**: 200 (Base) + 600 (Bonus) = **800 Total**
**Constitution**: v1.0.0 Compliant

---

## Overview

Phase III transforms the Evolution Todo application into an AI-powered conversational interface using:
- **OpenAI ChatKit** (Frontend UI)
- **OpenAI Agents SDK** (AI Logic)
- **Official MCP SDK** (Tool Integration)
- **Stateless Architecture** (Database-backed conversation persistence)

## Key Features

### Base Features (200 points)
- ✅ Natural language task creation
- ✅ Conversational task management (list, complete, delete, update)
- ✅ Stateless chat endpoint (conversation persistence)
- ✅ MCP Server with 11 standardized tools

### Bonus Features (600 points)
- 🔄 Voice input support (+200 points)
- 🔄 Urdu language support (+100 points)
- 🔄 Advanced task features via chat (+300 points)
- 🔄 Reusable Intelligence (MCP tools as components) (+200 points)
- 🔄 Cloud-Native Blueprints (K8s-ready stateless design) (+200 points)

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | OpenAI ChatKit | Latest |
| **AI Framework** | OpenAI Agents SDK | Latest |
| **MCP Server** | Official MCP Python SDK | 1.25.0+ |
| **Backend** | FastAPI | 0.115.0+ |
| **Database** | Neon PostgreSQL | (Phase II) |
| **ORM** | SQLModel | 0.0.31+ |
| **Voice** | OpenAI Whisper API | Latest |

## Project Structure

```
phase-3/
├── backend/
│   ├── mcp_server.py          # MCP Server with 11 tools ✅
│   ├── agent.py               # OpenAI Agents SDK integration ⏳
│   ├── models.py              # Conversation + Message models ✅
│   ├── routes/
│   │   └── chat.py            # Chat endpoint ⏳
│   ├── migrations/
│   │   └── 003_add_chat_tables.py  # DB migration ✅
│   ├── main.py                # FastAPI app
│   ├── db.py                  # Database connection
│   └── requirements.txt       # Dependencies (+ mcp, openai, httpx)
├── frontend/
│   ├── app/
│   │   ├── chat/              # ChatKit page ⏳
│   │   └── ...                # Existing Phase II pages
│   └── package.json           # Dependencies (+ ChatKit)
└── README.md                  # This file
```

## Implementation Status

### Group 1: Database Foundation ✅
- ✅ T-CHAT-001: Conversation and Message models (models.py:119-156)
- ✅ T-CHAT-002: Database migration (migrations/003_add_chat_tables.py)

### Group 2: MCP Server ⏳
- ✅ T-CHAT-003: MCP Server foundation (mcp_server.py)
- ✅ T-CHAT-004: add_task MCP tool
- ⏳ T-CHAT-005: list_tasks MCP tool
- ⏳ T-CHAT-006: complete_task MCP tool
- ⏳ T-CHAT-007: delete_task MCP tool
- ⏳ T-CHAT-008: update_task MCP tool
- ⏳ T-CHAT-009: Advanced MCP tools (6-11) - Bonus

### Group 3: OpenAI Agents SDK ⏳
- ⏳ T-CHAT-010: AI Agent integration

### Group 4: Chat API ⏳
- ⏳ T-CHAT-011: Chat endpoint
- ⏳ T-CHAT-012: Register route in main app

### Group 5: ChatKit Frontend ⏳
- ⏳ T-CHAT-013: Install ChatKit dependencies
- ⏳ T-CHAT-014: Create ChatKit page
- ⏳ T-CHAT-015: Voice input support (Bonus)
- ⏳ T-CHAT-016: Urdu language support (Bonus)

### Group 6: Deployment ⏳
- ⏳ T-CHAT-017: Environment variables
- ⏳ T-CHAT-018: Deploy frontend to Vercel
- ⏳ T-CHAT-019: Configure OpenAI domain allowlist
- ⏳ T-CHAT-020: End-to-end testing
- ⏳ T-CHAT-021: Record 90-second demo video

## Database Schema (Phase III Additions)

### Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_conversations_user_id ON conversations(user_id);
```

### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    role VARCHAR NOT NULL,  -- "user" | "assistant"
    content VARCHAR NOT NULL,
    tool_calls JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
CREATE INDEX ix_messages_user_id ON messages(user_id);
```

## Setup Instructions

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd phase-3/backend
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Add:
   # OPENAI_API_KEY=your_openai_api_key
   # DATABASE_URL=your_neon_postgres_url
   # API_BASE_URL=http://localhost:8000
   ```

3. **Run database migration:**
   ```bash
   python migrations/003_add_chat_tables.py
   ```

4. **Start backend server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd phase-3/frontend
   npm install
   ```

2. **Set environment variables:**
   ```bash
   # .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_CHATKIT_API_KEY=your_chatkit_key
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

## API Endpoints (Phase III)

### Chat Endpoint
```
POST /api/{user_id}/chat
Authorization: Bearer <JWT>
Content-Type: application/json

Request:
{
  "conversation_id": int | null,  // null = create new conversation
  "message": string               // User's message
}

Response:
{
  "conversation_id": int,
  "response": string,             // AI assistant's response
  "tool_calls": [{                // Tools executed by AI
    "tool": string,
    "args": object
  }]
}
```

## MCP Tools (11 Total)

1. **add_task** - Create task with priority, due date, tags, recurrence
2. **list_tasks** - List tasks with filtering and sorting
3. **complete_task** - Mark task as completed
4. **delete_task** - Delete a task
5. **update_task** - Update task details
6. **search_tasks** - Semantic search across tasks
7. **set_priority** - Change task priority
8. **add_tags** - Add tags to task
9. **schedule_reminder** - Schedule task reminder
10. **get_recurring_tasks** - List recurring tasks
11. **analytics_summary** - Get task statistics

## Testing

### Manual Test Scenario
```
User: "Add a task to buy groceries tomorrow at 5 PM"
Expected: Task created with due_date set to tomorrow 5 PM

User: "Show me all high priority tasks"
Expected: List of tasks filtered by priority="high"

User: "Mark task 3 as done"
Expected: Task 3 marked as completed
```

### Urdu Support Test
```
User: "ایک کام شامل کریں: کل دوپہر 3 بجے کلائنٹ کال"
Expected: Task created with Urdu title, AI responds in Urdu
```

## Deployment

### Backend (Hugging Face Spaces)
- Update `Dockerfile` for Phase III dependencies
- Add `OPENAI_API_KEY` to Hugging Face secrets
- Deploy backend with MCP server and agent

### Frontend (Vercel)
- Add ChatKit configuration
- Set `NEXT_PUBLIC_API_URL` to deployed backend URL
- Configure OpenAI domain allowlist

## Success Criteria

✅ Phase III complete when:
- User can manage tasks via natural language
- All 11 MCP tools implemented and working
- Conversation state persists across server restarts
- ChatKit frontend deployed and functional
- Voice + Urdu support working (Bonus)
- Advanced features accessible via chat (Bonus)
- 90-second demo video recorded

---

## References

- **Specification**: `/specs/phase-3-chatbot/spec.md`
- **Implementation Plan**: `/specs/phase-3-chatbot/plan.md`
- **Tasks Breakdown**: `/specs/phase-3-chatbot/tasks.md`
- **Constitution**: `/.specify/memory/constitution.md`
- **Hackathon Guide**: `/hackathon.md`

---

**🤖 Generated with Claude Code (Constitution v1.0.0)**
**Task**: T-CHAT-REF001 - Phase III folder structure creation
