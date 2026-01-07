# Phase III: AI-Powered Todo Chatbot - Specification

**Version**: 1.0.0
**Status**: Draft
**Constitution**: v1.0.0 Compliant
**Target Points**: 200 (Base) + 600 (Bonus) = **800 Total**

---

## Overview

Transform the Evolution Todo application into an AI-powered conversational interface using **OpenAI ChatKit** (frontend), **OpenAI Agents SDK** (AI logic), and **Official MCP SDK** (tool integration). The chatbot must manage tasks through natural language while maintaining **stateless architecture** with database persistence.

### Key Objectives

1. **Conversational Task Management**: "Add a task to call mom tomorrow" → Task created with due date
2. **Stateless Chat Endpoint**: Server restart must NOT lose conversation context
3. **MCP Tool Architecture**: AI agent uses standardized tools to interact with task system
4. **Multi-Modal Support**: Voice input + Urdu language support (Bonus +300 points)
5. **Advanced Features**: Priorities, tags, due dates, recurring tasks, search (Bonus +300 points)

---

## User Stories

### US-CHAT-1: Natural Language Task Creation (Priority: P1)

```
As a user
I want to create tasks using natural language
So that I can quickly add todos without clicking through forms
```

**Acceptance Criteria:**
- ✅ User can type: "Remind me to buy groceries tomorrow at 5 PM"
- ✅ AI extracts: title="Buy groceries", due_date="tomorrow 5PM"
- ✅ Task is created in database with proper due date
- ✅ AI confirms: "✅ Added task 'Buy groceries' due tomorrow at 5 PM"
- ✅ Conversation history is persisted to database

**Test Scenarios:**
```
GIVEN I am logged into the chatbot
WHEN I type "Add a task to finish the report by Friday"
THEN AI agent calls add_task MCP tool
AND task is created with title="Finish the report", due_date=<next Friday>
AND AI responds with confirmation message
AND message is saved to database

GIVEN server restarts
WHEN I reload the chat
THEN previous conversation history is loaded from database
AND I can continue the conversation
```

---

### US-CHAT-2: List and Filter Tasks (Priority: P1)

```
As a user
I want to view my tasks using natural language queries
So that I can quickly see what needs to be done
```

**Acceptance Criteria:**
- ✅ User can type: "Show me all my pending tasks"
- ✅ AI calls list_tasks MCP tool with status="pending"
- ✅ AI formats results in readable list
- ✅ User can filter: "Show high priority work tasks"
- ✅ AI applies multiple filters (priority + tags)

**Test Scenarios:**
```
GIVEN I have 10 tasks (5 pending, 5 completed)
WHEN I ask "What's on my todo list?"
THEN AI shows all 10 tasks with status indicators
AND tasks are formatted clearly

GIVEN I ask "Show only incomplete tasks"
WHEN AI processes the query
THEN only 5 pending tasks are displayed
AND completed tasks are not shown
```

---

### US-CHAT-3: Complete and Delete Tasks (Priority: P1)

```
As a user
I want to mark tasks complete or delete them via chat
So that I can manage my list conversationally
```

**Acceptance Criteria:**
- ✅ User: "Mark task 3 as done" → AI calls complete_task
- ✅ User: "Delete the grocery task" → AI searches + confirms + deletes
- ✅ AI asks for confirmation before destructive actions
- ✅ Changes are immediately reflected in database

**Test Scenarios:**
```
GIVEN I have task ID 7 titled "Call dentist"
WHEN I say "Mark task 7 as complete"
THEN AI calls complete_task(user_id, task_id=7)
AND task.completed is set to true
AND AI confirms "✅ Task 'Call dentist' marked complete"

GIVEN I want to delete a task
WHEN I say "Delete the dentist task"
THEN AI lists matching tasks and asks for confirmation
AND waits for user approval
WHEN I confirm
THEN task is deleted from database
```

---

### US-CHAT-4: Update Tasks (Priority: P1)

```
As a user
I want to modify task details through conversation
So that I can update tasks naturally
```

**Acceptance Criteria:**
- ✅ User: "Change task 5 title to 'Team meeting at 3 PM'"
- ✅ AI calls update_task MCP tool
- ✅ User: "Add work tag to task 3"
- ✅ AI updates task tags
- ✅ Changes persist across server restarts

**Test Scenarios:**
```
GIVEN task 2 has title "Buy milk"
WHEN I say "Change task 2 to 'Buy milk and eggs'"
THEN AI calls update_task(task_id=2, title="Buy milk and eggs")
AND task is updated in database
AND AI confirms the change
```

---

### US-CHAT-5: Stateless Conversation Persistence (Priority: P1)

```
As a system
I want conversation state stored in database
So that server restarts don't lose context
```

**Acceptance Criteria:**
- ✅ All messages stored in `messages` table
- ✅ Conversations tracked in `conversations` table
- ✅ Server restart → conversation history loaded from DB
- ✅ User can resume conversation seamlessly
- ✅ No in-memory state on server

**Test Scenarios:**
```
GIVEN I have an active conversation (conversation_id=42)
WHEN I send 5 messages
AND server restarts
AND I reload the chatbot
THEN conversation_id=42 is restored from database
AND all 5 previous messages are displayed
AND I can continue chatting without losing context
```

---

### US-CHAT-6: Voice Input Support (Priority: P2 - Bonus)

```
As a user
I want to use voice commands to manage tasks
So that I can operate hands-free
```

**Acceptance Criteria:**
- ✅ Microphone button in ChatKit UI
- ✅ Voice transcribed to text via OpenAI Whisper
- ✅ Transcription sent to AI agent
- ✅ Works same as text input
- ✅ Supports both English and Urdu

**Test Scenarios:**
```
GIVEN I click the microphone button
WHEN I speak "Add a task to pay bills tomorrow"
THEN speech is transcribed to text
AND processed as normal text input
AND task is created correctly
```

---

### US-CHAT-7: Urdu Language Support (Priority: P2 - Bonus)

```
As an Urdu-speaking user
I want to manage tasks in Urdu language
So that I can use my native language
```

**Acceptance Criteria:**
- ✅ AI detects Urdu input automatically
- ✅ Responds in Urdu when user speaks Urdu
- ✅ Handles mixed English/Urdu input
- ✅ Task titles can be in Urdu or English

**Test Scenarios:**
```
GIVEN I type "ایک کام شامل کریں: کل دوپہر 3 بجے کلائنٹ کال"
WHEN AI processes the message
THEN task is created: title="کل دوپہر 3 بجے کلائنٹ کال", due_date=<tomorrow 3PM>
AND AI responds in Urdu: "✅ کام شامل کیا گیا"
```

---

### US-CHAT-8: Advanced Task Features (Priority: P2 - Bonus)

```
As a user
I want to use advanced features via natural language
So that I can create sophisticated task workflows
```

**Acceptance Criteria:**
- ✅ Priorities: "Add high priority task to review code"
- ✅ Tags: "Add work and urgent tags to task 5"
- ✅ Recurring: "Weekly team meeting every Monday"
- ✅ Search: "Find all tasks with 'client' in title"
- ✅ Sorting: "Show tasks sorted by due date"

**Test Scenarios:**
```
GIVEN I say "Create a weekly grocery shopping task"
WHEN AI processes the command
THEN task is created with recurrence_pattern="weekly"
AND AI confirms "✅ Recurring task created for every week"

GIVEN I ask "Search for all urgent tasks"
WHEN AI searches tasks
THEN all tasks with tag="urgent" or priority="high" are shown
```

---

## Functional Requirements

### FR-CHAT-1: Conversation Model

```python
class Conversation(SQLModel, table=True):
    id: int (primary key)
    user_id: str (foreign key → users.id)
    created_at: datetime
    updated_at: datetime
```

### FR-CHAT-2: Message Model

```python
class Message(SQLModel, table=True):
    id: int (primary key)
    conversation_id: int (foreign key → conversations.id)
    user_id: str (foreign key → users.id)
    role: str ("user" | "assistant")
    content: str (message text)
    created_at: datetime
```

### FR-CHAT-3: Chat API Endpoint

```
POST /api/{user_id}/chat
Authorization: Bearer <JWT>
Content-Type: application/json

Request Body:
{
  "conversation_id": int | null,  // null = create new
  "message": string
}

Response:
{
  "conversation_id": int,
  "response": string,
  "tool_calls": [{tool: string, args: object}]
}
```

### FR-CHAT-4: MCP Tools

**11 Required Tools:**
1. `add_task(user_id, title, description?, priority?, due_date?, tags?, recurring?)`
2. `list_tasks(user_id, status?, priority?, tags?, sort_by?, search?)`
3. `complete_task(user_id, task_id)`
4. `delete_task(user_id, task_id)`
5. `update_task(user_id, task_id, title?, description?, priority?, due_date?, tags?)`
6. `search_tasks(user_id, query, filters?)`
7. `set_priority(user_id, task_id, priority)`
8. `add_tags(user_id, task_id, tags)`
9. `schedule_reminder(user_id, task_id, datetime)`
10. `get_recurring_tasks(user_id, pattern?)`
11. `analytics_summary(user_id)` → stats, completion rate

### FR-CHAT-5: Stateless Architecture

- **No in-memory session storage** on server
- **All state in database**: conversations, messages, tasks
- **Server restart resilience**: Load conversation history from DB
- **Horizontal scalability**: Any server instance can handle any request

---

## Non-Functional Requirements

### NFR-CHAT-1: Performance

- Chat response time: < 2 seconds (includes AI processing)
- Database query time: < 100ms
- Message storage: < 50ms

### NFR-CHAT-2: Scalability

- Support 100+ concurrent users
- Handle 1000+ messages per minute
- Stateless design enables load balancing

### NFR-CHAT-3: AI Quality

- Natural language understanding: 90%+ accuracy
- Tool selection accuracy: 95%+
- Multi-turn conversation context: 5+ turns

### NFR-CHAT-4: Security

- JWT authentication on all endpoints
- User isolation: Only access own conversations
- Input sanitization: Prevent injection attacks
- Rate limiting: 10 requests/second per user

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | OpenAI ChatKit | Latest |
| **AI Framework** | OpenAI Agents SDK | Latest |
| **MCP Server** | Official MCP Python SDK | Latest |
| **Backend** | FastAPI | 0.115.0+ |
| **Database** | Neon PostgreSQL | (existing) |
| **ORM** | SQLModel | 0.0.31+ |
| **Voice** | OpenAI Whisper API | Latest |

---

## Out of Scope (Phase III)

❌ **Not included:**
- Kubernetes deployment (Phase IV)
- Kafka/Dapr integration (Phase V)
- WebSocket real-time updates (Phase V)
- Multi-agent collaboration (Phase V)
- CI/CD pipelines (Phase V)

**Focus**: Conversational interface with MCP tools and stateless architecture.

---

## Success Criteria

✅ **Phase III Complete when:**
- User can manage tasks via natural language
- All 11 MCP tools implemented and working
- Conversation state persists across server restarts
- ChatKit frontend deployed and functional
- Voice + Urdu support working (Bonus +300)
- Advanced features accessible via chat (Bonus +300)
- 90-second demo video showing all features

---

## Bonus Points Breakdown

| Feature | Points | Status |
|---------|--------|--------|
| **Reusable Intelligence** | +200 | MCP tools as reusable components |
| **Cloud-Native Blueprints** | +200 | K8s-ready stateless design |
| **Urdu Language Support** | +100 | Bilingual AI agent |
| **Voice Commands** | +200 | Whisper API integration |
| **Total Bonus** | **+700** | **Target: 900 total points** |

---

**References:**
- Constitution: `/.specify/memory/constitution.md`
- Phase II Spec: `/specs/features/task-crud.md`
- Hackathon Guide: `/hackathon.md` (Phase III section)
- Database Schema: `/specs/database/schema.md`
