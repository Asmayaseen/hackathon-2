---
id: "001"
title: "Phase III AI Chatbot Specification Creation"
stage: "spec"
date: "2026-01-05"
surface: "agent"
model: "claude-sonnet-4-5"
feature: "phase-3-chatbot"
branch: "main"
user: "asmayaseen"
command: "none"
labels: ["phase3", "chatbot", "mcp", "openai-agents-sdk", "chatkit", "specification"]
links:
  spec: "/specs/phase-3-chatbot/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/phase-3-chatbot/spec.md"
tests: []
---

# Prompt History Record: Phase III Specification

## Context

Evolution of Todo Hackathon - Phase II (Full-Stack Web Application) is complete with:
- ✅ Next.js 16 frontend with authentication
- ✅ FastAPI backend with RESTful API
- ✅ Neon PostgreSQL database with Task CRUD
- ✅ Advanced features already implemented (priorities, tags, due dates, recurring tasks, search)

**Next Phase**: Phase III - AI-Powered Todo Chatbot

**Target Points**: 200 (base) + 600 (bonus) = 800 total

## Prompt (User Input)

```text
bismillah karen phase3 ko start krte hain

ap check kijiye tamam requirment is project ki complete hai k nhi?

@hackathon.md main phase3 ko achi trhan se read karo
.specify/memory/constitution.md ki file ko achi trahan se read karen

🚀 Professional Phase III + Advanced Level Implementation Prompt for Claude Code
(Constitution v1.0.0 Compliant + Bonus Points Maximized)

**🧠 CLAUDE CODE ARCHITECT EXECUTION MODE ACTIVATED**

You are implementing **PHASE III: AI-Powered Todo Chatbot** + **ADVANCED LEVEL FEATURES**
for Evolution of Todo Hackathon.

[... detailed requirements for ChatKit, OpenAI Agents SDK, MCP Server, Voice + Urdu support, 11 MCP tools, etc.]
```

## Response (Assistant Output)

### Actions Taken

1. **Read Constitution** (`.specify/memory/constitution.md`):
   - Confirmed Spec-Driven Development is NON-NEGOTIABLE
   - Verified technology stack requirements for Phase III:
     - Frontend: OpenAI ChatKit
     - AI Framework: OpenAI Agents SDK
     - MCP Server: Official MCP SDK
     - Database: Neon PostgreSQL (existing)
   - Confirmed stateless architecture requirement

2. **Analyzed Phase II State**:
   - Backend already has: User, Task models with advanced features
   - Routes exist for: auth, tasks, bulk, export, history, notifications, preferences, recurrence, search, stats
   - **Missing**: Conversation/Message models, Chat endpoint, MCP Server, ChatKit frontend

3. **Created Phase III Specification**:
   - File: `specs/phase-3-chatbot/spec.md`
   - 8 User Stories (US-CHAT-1 through US-CHAT-8)
   - 5 Functional Requirements (FR-CHAT-1 through FR-CHAT-5)
   - 4 Non-Functional Requirements
   - 11 MCP Tools specification
   - Bonus features breakdown (+700 points target)

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Stateless Architecture** | Per constitution requirement - all state in database for K8s readiness |
| **11 MCP Tools** | Extended from 5 basic to 11 advanced for bonus points |
| **Conversation/Message Models** | New database tables for persistent chat history |
| **Voice + Urdu Support** | Target +300 bonus points |
| **OpenAI Agents SDK** | Required by hackathon specs for Phase III |

### Specification Highlights

**User Stories (Priority P1):**
1. Natural language task creation
2. List and filter tasks
3. Complete and delete tasks
4. Update task details
5. Stateless conversation persistence

**Bonus Features (Priority P2):**
6. Voice input support (+200 points)
7. Urdu language support (+100 points)
8. Advanced task features (+300 points)

**Database Models Added:**
```python
class Conversation(SQLModel, table=True):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

class Message(SQLModel, table=True):
    id: int
    conversation_id: int
    user_id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime
```

**Chat API Endpoint:**
```
POST /api/{user_id}/chat
- Request: {conversation_id?, message}
- Response: {conversation_id, response, tool_calls}
```

**11 MCP Tools:**
1. add_task (with advanced params: priority, due_date, tags, recurring)
2. list_tasks (with filtering: status, priority, tags, search, sort)
3. complete_task
4. delete_task
5. update_task
6. search_tasks (semantic search)
7. set_priority
8. add_tags
9. schedule_reminder
10. get_recurring_tasks
11. analytics_summary

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | OpenAI ChatKit | Conversational UI with voice support |
| AI Logic | OpenAI Agents SDK | Natural language understanding + tool orchestration |
| MCP Server | Official MCP Python SDK | Standardized tool interface for AI agent |
| Backend | FastAPI | Chat endpoint + MCP server hosting |
| Database | Neon PostgreSQL | Stateless persistence (conversations + messages) |
| Voice | OpenAI Whisper API | Speech-to-text for voice commands |

### Success Criteria

✅ **Phase III Complete When:**
- Natural language task management working
- All 11 MCP tools implemented
- Conversation persists across server restarts
- ChatKit deployed with domain allowlist configured
- Voice + Urdu support functional (bonus +300)
- Advanced features accessible via chat (bonus +300)
- 90-second demo video recorded

### Bonus Points Target

| Feature | Points | Implementation |
|---------|--------|----------------|
| Reusable Intelligence | +200 | MCP tools as reusable components |
| Cloud-Native Blueprints | +200 | Stateless K8s-ready design |
| Urdu Language | +100 | Bilingual AI agent |
| Voice Commands | +200 | Whisper API integration |
| **Total Bonus** | **+700** | **Target: 900 total** |

## Next Steps

Following Spec-Driven Development workflow:

1. ✅ **Specify** - COMPLETE (this document)
2. ⏳ **Plan** - Create `specs/phase-3-chatbot/plan.md`
   - MCP Server architecture
   - OpenAI Agents SDK integration design
   - Database migration for Conversation/Message models
   - ChatKit setup with voice + Urdu support
3. ⏳ **Tasks** - Create `specs/phase-3-chatbot/tasks.md`
   - Break down into atomic, testable tasks
   - Define implementation order with dependencies
4. ⏳ **Implement** - Execute via Claude Code (no manual coding)

## Outcome

**Status**: ✅ Specification Phase Complete

**Deliverable**: `specs/phase-3-chatbot/spec.md`

**Validation**:
- ✅ Follows constitution v1.0.0 requirements
- ✅ Adheres to Phase III technology stack
- ✅ Includes all 8 user stories with acceptance criteria
- ✅ Defines stateless architecture
- ✅ Targets bonus points for maximum score
- ✅ References existing Phase II implementation

**Eval Criteria Met**:
- Clear user stories with Given/When/Then scenarios
- Functional and non-functional requirements specified
- Technology stack aligned with hackathon requirements
- Success criteria measurable and testable
- Bonus features clearly defined for extra points

---

**Prompt Record**: Phase III Specification Creation
**Agent**: Claude Sonnet 4.5 via Claude Code
**Constitution**: v1.0.0 Compliant
**Next**: Proceed to Planning Phase
