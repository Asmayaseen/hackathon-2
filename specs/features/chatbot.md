# Feature Specification: AI Chatbot Interface

**Feature ID**: FEAT-CHAT-001
**Created**: 2026-01-10
**Updated**: 2026-02-10
**Status**: Implemented (Phase III - V)
**Source Files**: `routes/chat.py`, `routes/chatkit.py`, `routes/voice.py`, `agent.py`, `mcp_server.py`, `chatkit_server.py`

---

## Overview

The AI Chatbot enables users to manage tasks through natural language conversation. The system uses **OpenAI Agents SDK** for AI logic, an **MCP Server** (11 tools) for task operations, and **OpenAI ChatKit** for the frontend widget. The architecture is **stateless** — all conversation state is persisted to the database, enabling server restarts and horizontal scaling.

### Architecture

```
┌──────────────┐     POST /api/{user_id}/chat     ┌──────────────────────────────┐
│  ChatKit UI  │ ──────────────────────────────── │  FastAPI Backend              │
│  (Frontend)  │                                   │  ┌────────────────────────┐  │
│              │                                   │  │ Chat Route             │  │
│  Voice Input │ ─ POST /api/{user_id}/transcribe─│  │ (load history from DB) │  │
│  (Whisper)   │                                   │  └──────────┬─────────────┘  │
│              │                                   │             │                 │
│              │ <── { response, tool_calls } ──── │  ┌──────────▼─────────────┐  │
│              │                                   │  │ OpenAI Agents SDK      │  │
│              │                                   │  │ (agent.py)             │  │
│              │                                   │  └──────────┬─────────────┘  │
│              │                                   │             │                 │
│              │                                   │  ┌──────────▼─────────────┐  │
│              │                                   │  │ MCP Server (11 tools)  │──┤──> Neon DB
│              │                                   │  │ (mcp_server.py)        │  │
│              │                                   │  └────────────────────────┘  │
└──────────────┘                                   └──────────────────────────────┘
```

---

## User Stories

### US-CHAT-01: Natural Language Task Management (P1)

As a user, I want to create, list, update, delete, and complete tasks using natural language.

```gherkin
Scenario: Create task via chat
  Given I am authenticated
  When I type "Add a task to buy groceries tomorrow at 5pm"
  Then the agent calls add_task MCP tool
  And a task is created with extracted title and due_date
  And the agent confirms with a friendly message

Scenario: List tasks via chat
  When I type "What's on my todo list?"
  Then the agent calls list_tasks tool
  And displays formatted task list

Scenario: Complete task via chat
  When I type "Mark task 3 as done"
  Then the agent calls complete_task with task_id=3
  And confirms completion
```

### US-CHAT-02: Conversation Persistence (P1)

As a user, I want my chat history to survive server restarts.

```gherkin
Scenario: Resume conversation after restart
  Given I had a conversation with id=1
  When the server restarts
  And I send a message with conversation_id=1
  Then previous messages are loaded from database
  And the agent has full conversation context
```

### US-CHAT-03: Voice Input (Bonus)

As a user, I want to speak commands instead of typing.

```gherkin
Scenario: Voice transcription
  When I record audio saying "Add a task to call mom"
  Then the audio is sent to POST /api/{user_id}/transcribe
  And Whisper transcribes it to text
  And the text is sent to the chat endpoint
```

---

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-CHAT-01 | System MUST provide a stateless chat endpoint at POST /api/{user_id}/chat |
| FR-CHAT-02 | System MUST persist conversations and messages to database |
| FR-CHAT-03 | System MUST load conversation history from database on each request |
| FR-CHAT-04 | System MUST expose 11 MCP tools for the AI agent |
| FR-CHAT-05 | System MUST use OpenAI Agents SDK for natural language understanding |
| FR-CHAT-06 | System MUST return tool_calls array showing which tools were invoked |
| FR-CHAT-07 | System MUST support creating new conversations (omit conversation_id) |
| FR-CHAT-08 | System MUST support continuing existing conversations (provide conversation_id) |
| FR-CHAT-09 | System MUST provide ChatKit session endpoint for frontend integration |
| FR-CHAT-10 | System MUST provide ChatKit SSE streaming endpoint |
| FR-CHAT-11 | System MUST provide voice transcription endpoint using Whisper |
| FR-CHAT-12 | System MUST enforce JWT auth on all chat endpoints |

---

## MCP Tools (11 Total)

| Tool | Purpose | Required Params |
|---|---|---|
| `add_task` | Create task | user_id, title, description, due_date |
| `list_tasks` | List/filter tasks | user_id |
| `complete_task` | Toggle completion | user_id, task_id |
| `delete_task` | Remove task | user_id, task_id |
| `update_task` | Modify task | user_id, task_id |
| `search_tasks` | Full-text search | user_id, query |
| `set_priority` | Change priority | user_id, task_id, priority |
| `add_tags` | Append tags | user_id, task_id, tags |
| `schedule_reminder` | Set reminder | user_id, task_id, reminder_time |
| `get_recurring_tasks` | List recurring | user_id |
| `analytics_summary` | Get stats | user_id |

Full tool schemas: `specs/api/mcp-tools.md`

---

## Database Models

| Model | Fields | Purpose |
|---|---|---|
| Conversation | id, user_id, created_at, updated_at | Chat session |
| Message | id, conversation_id, user_id, role, content, created_at | Chat message |

---

## Stateless Request Cycle

1. Receive user message
2. Fetch conversation history from database
3. Build message array (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state

---

## Related Specs

- `specs/api/mcp-tools.md` — Full MCP tool schemas
- `specs/api/rest-endpoints.md` — Chat/ChatKit/Voice endpoints
- `specs/phase-3-chatbot/spec.md` — Detailed Phase III specification

---

## Revision History

| Date | Change | Author |
|---|---|---|
| 2026-01-10 | Initial draft | spec-kit |
| 2026-02-10 | Formalized from implemented code; added architecture diagram, all 11 MCP tools, stateless cycle | claude-code |
