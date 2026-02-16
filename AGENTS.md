# AGENTS.md

> Governs all AI agent behavior in the Evolution Todo repository.
> Aligned with `.specify/memory/constitution.md` (v1.1.0), `CLAUDE.md`, and the OpenAI Agents SDK.

---

## 1. Purpose of Agents

This project is built entirely through **Spec-Driven Development (SDD)** — a workflow where no agent may write code until the specification is complete and approved. Agents are the primary implementation workforce. They read specs, plan implementations, execute tasks, and record decisions. Humans set direction; agents execute.

The operating model:

```
Human (Architext)
    │
    │  Intent, requirements, approvals
    v
Orchestrator Agent (Claude Code)
    │
    │  Delegates to specialized sub-agents
    v
┌─────────────────────────────────────────────────────┐
│  Sub-Agents                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Backend  │ │ Frontend │ │ AI/Chat  │  ...        │
│  │ Expert   │ │ Expert   │ │ Engineer │            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘            │
│       │             │            │                   │
│       v             v            v                   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Runtime Agents (in-app)                     │   │
│  │  agent.py + MCP Server + Intent Classifier   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Two categories of agents exist:**

1. **Development-time agents** — Claude Code sub-agents (`.claude/agents/`) that write, test, and deploy code.
2. **Runtime agents** — The AI chatbot (`agent.py`), MCP server (`mcp_server.py`), and autonomous services (`notification-service`, cron handlers) that run in production.

---

## 2. Spec-Kit Lifecycle (Binding on All Agents)

Every agent MUST follow this lifecycle. No exceptions.

```
Specify → Plan → Tasks → Implement → Record
```

| Phase | Artifact | Command | Agent Role |
|---|---|---|---|
| **Specify** | `specs/*/spec.md` | `/sp.specify` | Document WHAT to build |
| **Plan** | `specs/*/plan.md` | `/sp.plan` | Document HOW to build |
| **Tasks** | `specs/*/tasks.md` | `/sp.tasks` | Break into atomic work units |
| **Implement** | Source code | `/sp.implement` | Execute tasks with Task ID references |
| **Record** | `history/prompts/` | `/sp.phr` | Capture prompt history |
| **Decide** | `history/adr/` | `/sp.adr` | Document architectural decisions |

**The golden rule: No task = No code.**

---

## 3. Document Hierarchy

When conflicts arise between governance documents, this precedence applies:

```
Constitution (.specify/memory/constitution.md)    ← Highest authority
    │
    v
Specifications (specs/*/spec.md)
    │
    v
Plans (specs/*/plan.md)
    │
    v
Tasks (specs/*/tasks.md)
    │
    v
AGENTS.md (this file)
    │
    v
CLAUDE.md (runtime guidance)
    │
    v
Phase-specific CLAUDE.md files                    ← Lowest authority
```

---

## 4. Development-Time Agents

### 4.1 Orchestrator: Claude Code

**Role**: Primary agent. Receives user intent, delegates to sub-agents, enforces SDD lifecycle, creates PHRs and ADR suggestions.

**Responsibilities**:
- Parse and confirm user intent before acting
- Route work to the appropriate sub-agent
- Enforce the Specify → Plan → Tasks → Implement lifecycle
- Create Prompt History Records after every interaction
- Surface ADR suggestions when architectural decisions are detected
- Invoke the human when requirements are ambiguous

**Decision Boundaries**:
- CAN delegate implementation to sub-agents
- CAN create PHRs and suggest ADRs
- CANNOT create ADRs without user consent
- CANNOT skip the SDD lifecycle
- CANNOT commit code without explicit user request

**Governance**: `CLAUDE.md` (root)

---

### 4.2 Sub-Agent Registry

Twelve sub-agents are defined in `.claude/agents/`. Each has a bounded scope, specific skills, and explicit constraints.

#### Architecture & Planning

| Agent | File | Scope | Skills |
|---|---|---|---|
| **fullstack-architect** | `.claude/agents/fullstack-architect.md` | System architecture decisions, API contract design, data flow, auth flow, integration patterns | nextjs, fastapi, better-auth-ts, better-auth-python, drizzle-orm, neon-postgres |

**Decision boundary**: Can propose architecture. Cannot implement without approved plan.

#### Backend

| Agent | File | Scope | Skills |
|---|---|---|---|
| **backend-expert** | `.claude/agents/backend-expert.md` | FastAPI routes, SQLModel/SQLAlchemy, JWT integration, dependency injection | fastapi, better-auth-python |
| **fastapi-backend-expert** | `.claude/agents/fastapi-backend-expert.md` | Production-grade APIs, security-first patterns (user isolation, parameterized queries) | fastapi, better-auth-python, neon-postgres |
| **backend-testing** | `.claude/agents/backend-testing.md` | Pytest unit/integration/API tests, 80% coverage target | pytest |
| **auth-expert** | `.claude/agents/auth-expert.md` | Better Auth (TypeScript + Python), JWT, OAuth, sessions | better-auth-ts, better-auth-python |

#### Frontend

| Agent | File | Scope | Skills |
|---|---|---|---|
| **nextjs-frontend-expert** | `.claude/agents/nextjs-frontend-expert.md` | Next.js 16 App Router, Server/Client Components, accessibility (WCAG 2.1 AA), dark mode | nextjs |
| **frontend-feature-builder** | `.claude/agents/frontend-feature-builder.md` | Rapid UI implementation, pattern-driven, shadcn + Tailwind | nextjs, shadcn |
| **ui-ux-expert** | `.claude/agents/ui-ux-expert.md` | Visual design, component design, a11y, Framer Motion | shadcn |

#### AI / Chatbot

| Agent | File | Scope | Skills |
|---|---|---|---|
| **chatkit-backend-engineer** | `.claude/agents/chatkit-backend-engineer.md` | ChatKitServer, event handlers, Store/FileStore, multi-agent orchestration, streaming | ai.chatkit.backend, ai.chatkit.widgets |
| **chatkit-frontend-engineer** | `.claude/agents/chatkit-frontend-engineer.md` | ChatKit widget embedding, CDN script loading, auth flow | ai.chatkit.frontend, ai.chatkit.widgets |

#### Phase 1 (Console)

| Agent | File | Scope | Constraints |
|---|---|---|---|
| **logic-agent** | `.claude/agents/logic-agent.md` | Business logic (`src/core/`), Pydantic models, TodoManager | MUST NOT import from `src/ui/`. `mypy --strict`. |
| **ui-agent** | `.claude/agents/ui-agent.md` | CLI UI (`src/ui/`), Typer + Rich | MUST NOT duplicate business logic. |

---

### 4.3 Sub-Agent Constraints (Universal)

Every sub-agent MUST:

1. **Reference a Task ID** in every code change
2. **Read the relevant spec** before writing code
3. **Follow the constitution** — no substitutions to the mandatory tech stack
4. **Include code comments** linking to Task ID and Spec section
5. **Prefer the smallest viable diff** — do not refactor unrelated code
6. **Never hardcode secrets** — use `.env` and environment variables
7. **Never invent features** — if it is not in the spec, do not build it
8. **Stop and ask** if requirements are ambiguous or underspecified

Every sub-agent MUST NOT:

1. Skip specs to write code directly
2. Create tasks autonomously (tasks come from `/sp.tasks`)
3. Alter stack choices without constitution amendment
4. Add endpoints, fields, or flows not in the spec
5. Produce "creative" implementations that violate the plan
6. Generate or guess missing requirements

---

## 5. Runtime Agents

These agents run inside the deployed application. They are not development tools — they serve end users.

### 5.1 AI Chatbot Agent (`agent.py`)

**Role**: Conversational task management assistant. Translates natural language into tool calls.

**Source**: `phase-4/backend/agent.py` (223 lines)

**LLM Provider**: Groq (`llama-3.3-70b-versatile`) preferred, OpenAI (`gpt-4o`) fallback.

**Invocation flow**:
```
User message
  → Language validation (English/Urdu only)
  → Intent classification (rule-based, multilingual)
  → LLM call with 5 function-calling tools
  → Argument validation + user_id injection
  → MCP tool dispatch
  → Tool result fed back to LLM for response
  → Final response to user
```

**Tools exposed to LLM** (5 of 11):
`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`

**Safety constraints**:
- `user_id` is injected by the agent, never supplied by the LLM
- Tool arguments are validated and sanitized before execution (`tool_validation.py`)
- Intent classification prevents tool misuse (e.g., calling `update_task` when user means `add_task`)
- Language validation rejects unsupported languages before reaching the LLM
- Conversation context limited to last 10 messages

---

### 5.2 MCP Server (`mcp_server.py`)

**Role**: Exposes 11 task management operations as MCP tools. Executes database operations and REST API calls on behalf of the AI agent.

**Source**: `phase-4/backend/mcp_server.py` (695 lines)

**Server name**: `evolution-todo-mcp`

**SDK**: Official MCP Python SDK (`mcp.server.Server`)

**Tools** (11 total):

| # | Tool | Access | Mutates | Events |
|---|---|---|---|---|
| 1 | `add_task` | DB direct | Yes | `CREATED` |
| 2 | `list_tasks` | DB direct | No | — |
| 3 | `complete_task` | DB direct | Yes | `COMPLETED` |
| 4 | `delete_task` | REST API | Yes | — |
| 5 | `update_task` | DB direct | Yes | — |
| 6 | `search_tasks` | REST API | No | — |
| 7 | `set_priority` | DB direct | Yes | — |
| 8 | `add_tags` | DB direct | Yes | — |
| 9 | `schedule_reminder` | REST API | Yes | — |
| 10 | `get_recurring_tasks` | REST API | No | — |
| 11 | `analytics_summary` | REST API | No | — |

**Safety constraints**:
- Every tool requires `user_id`; ownership verified on every DB operation
- Unknown tool names return an error, not an exception
- All errors caught and returned as `TextContent` (never thrown)
- Event publishing is fire-and-forget; tool execution succeeds even if events fail
- REST API calls have a 10-second timeout

**Full specification**: `specs/api/mcp-tools.md`

---

### 5.3 Intent Classifier (`intent_classifier.py`)

**Role**: Rule-based pre-filter that classifies user intent before the LLM call. Prevents common tool misuse.

**Source**: `phase-4/backend/intent_classifier.py` (215 lines)

**Intent types**: `ADD_TASK`, `UPDATE_TASK`, `DELETE_TASK`, `LIST_TASKS`, `COMPLETE_TASK`, `SEARCH`, `ANALYTICS`, `UNCLEAR`

**Languages**: English, Roman Urdu, Urdu script

**Confidence scoring**: Returns 0.0–1.0 per classification.

---

### 5.4 Tool Validator (`tool_validation.py`)

**Role**: Defensive sanitization layer between the LLM and MCP tools. Prevents null values, invalid enums, and missing required fields.

**Source**: `phase-4/backend/tool_validation.py` (292 lines)

**Validations**:
- Null value removal from all tool arguments
- Description auto-generation for `add_task` when missing
- Recurrence pattern sanitization (removes `"none"`, `null`, `""`)
- Priority enum validation (defaults to `"none"`)
- ISO 8601 date normalization
- Tags array type enforcement
- Language detection and rejection of unsupported languages

---

### 5.5 Notification Service (`phase-5/notification-service/main.py`)

**Role**: Autonomous microservice. Consumes reminder events from Kafka via Dapr pub/sub and delivers notifications.

**Source**: `phase-5/notification-service/main.py` (261 lines)

**Port**: 8001

**Dapr topic**: `reminders`

**Behavior**: Fully autonomous. Runs independently, processes events asynchronously. No user interaction required.

---

### 5.6 Cron Handlers (`routes/cron_handlers.py`)

**Role**: Scheduled task handlers triggered by Dapr cron bindings. No user interaction.

**Jobs**:
- **Reminder cron** (every 5 min): Checks for tasks with due reminders
- **Recurring task cron** (hourly): Creates next occurrences for recurring tasks
- **Cleanup**: Removes stale data

---

## 6. Tool Access Rules

### 6.1 Development-Time Tools

| Tool | Who Can Use | Constraint |
|---|---|---|
| `Read`, `Glob`, `Grep` | All agents | Read-only; no restrictions |
| `Write`, `Edit` | All agents | Must reference a Task ID |
| `Bash` (git) | Orchestrator only | Only on explicit user request |
| `Bash` (tests) | backend-testing, orchestrator | After implementation |
| `Bash` (kubectl, helm) | orchestrator | Phase IV+ only |
| `WebSearch`, `WebFetch` | All agents | For documentation lookup only |
| `/sp.*` commands | Orchestrator | SDD lifecycle management |

### 6.2 Runtime Tools (MCP)

| Tool | Who Can Invoke | User Isolation |
|---|---|---|
| All 11 MCP tools | `agent.py` via `call_tool()` | `user_id` injected by agent, not LLM |
| Event publishing | MCP server (internal) | Scoped to task owner |
| Dapr service invocation | `dapr_client.py` | Service-to-service only |
| Cron handlers | Dapr cron binding | System-level, no user context |

### 6.3 LLM Tool Visibility

The LLM (Groq/OpenAI) sees **5 tools** via OpenAI function calling format. The LLM CANNOT:
- See or call the remaining 6 MCP tools directly
- Supply `user_id` (injected by the agent)
- Bypass argument validation
- Execute arbitrary code

---

## 7. Memory Usage

### 7.1 Development-Time Memory

| Memory Type | Location | Purpose | Persistence |
|---|---|---|---|
| Constitution | `.specify/memory/constitution.md` | Project principles and constraints | Permanent; amendment requires version bump |
| Specifications | `specs/*/spec.md` | Feature requirements | Permanent per phase |
| Plans | `specs/*/plan.md` | Architecture decisions | Permanent per phase |
| Tasks | `specs/*/tasks.md` | Atomic work units | Permanent per phase |
| Prompt History | `history/prompts/` | Audit trail of all interactions | Append-only |
| ADRs | `history/adr/` | Architectural decision records | Append-only |
| Config | `.spec-kit/config.yaml` | Project metadata, phase status | Updated per phase |

**Routing rules for PHRs** (all under `history/prompts/`):
- Constitution work → `history/prompts/constitution/`
- Feature work → `history/prompts/<feature-name>/`
- General work → `history/prompts/general/`

### 7.2 Runtime Memory

| Memory Type | Store | Scope | Persistence |
|---|---|---|---|
| Task data | Neon PostgreSQL | Per-user (`user_id` column) | Persistent |
| Conversation history | Neon PostgreSQL | Per-user, per-conversation | Persistent |
| LLM context window | In-memory (agent.py) | Last 10 messages | Session only |
| Event payloads | Kafka (via Dapr) | Per-topic | Configurable retention |
| Notification records | Neon PostgreSQL | Per-user | Persistent |

**Runtime agents are stateless.** All durable state is persisted to the database. Server restarts do not lose data. This enables horizontal scaling in Kubernetes (Constitution Principle VI).

---

## 8. Safety and Constraints

### 8.1 Non-Negotiable Rules (from Constitution)

1. **Spec-Driven Development**: No code without a completed specification
2. **Technology Stack Adherence**: Mandatory stack per phase; no substitutions
3. **Stateless Architecture**: No in-memory session storage; all state in database
4. **Documentation and Traceability**: Every change links to a Task ID and Spec section

### 8.2 Agent-Specific Safety

| Concern | Mitigation |
|---|---|
| LLM hallucinating tool calls | Intent classifier pre-filters; argument validator sanitizes |
| Cross-user data access | `user_id` injected by agent (not LLM); ownership verified per query |
| Secret exposure | Environment variables only; never in tool schemas, responses, or code |
| Unbounded LLM context | Conversation history capped at 10 messages |
| Event publish failure | Fire-and-forget; tool execution succeeds regardless |
| REST API timeout | 10-second timeout on all httpx calls |
| Dapr sidecar unavailable | Graceful degradation; `ConnectError` silently skipped |
| Invalid tool arguments | `ToolValidator` strips nulls, validates enums, normalizes dates |
| Unknown tool name | Returns error `TextContent`, not exception |
| Unsupported language | Rejected before reaching LLM |

### 8.3 What Agents MUST Avoid

- Freestyle code or architecture without spec backing
- Generating missing requirements instead of asking
- Creating tasks autonomously
- Altering stack choices without documented justification
- Adding endpoints, fields, or flows not in the spec
- Ignoring acceptance criteria
- Committing secrets, credentials, or API keys
- Force-pushing, resetting, or destructive git operations without explicit user request

---

## 9. Agent Collaboration

### 9.1 Escalation Rules

Agents escalate to the human (Architext) when:

1. **Ambiguous requirements** — Ask 2–3 targeted clarifying questions, then wait
2. **Unforeseen dependencies** — Surface the dependency, ask for prioritization
3. **Architectural uncertainty** — Present options with tradeoffs, get preference
4. **Completion checkpoint** — Summarize what was done, confirm next steps
5. **Constitution conflict** — If a request violates a non-negotiable principle, refuse and explain

Agents NEVER escalate by:
- Guessing and proceeding
- Asking "Is this plan okay?" without a concrete proposal
- Generating placeholder code to be "filled in later"

### 9.2 Development-Time Collaboration

```
User (Architext)
    │
    │  "Add reminder notifications"
    v
Orchestrator (Claude Code)
    │
    ├── 1. Reads specs/features/phase-v-integration.md
    ├── 2. Identifies tasks from specs/phase-5/tasks.md
    ├── 3. Delegates backend work to fastapi-backend-expert
    ├── 4. Delegates frontend work to nextjs-frontend-expert
    ├── 5. Delegates ChatKit integration to chatkit-backend-engineer
    ├── 6. Runs tests via backend-testing
    ├── 7. Creates PHR via /sp.phr
    └── 8. Suggests ADR if architectural decision detected
```

**Handoff protocol**: When delegating, the orchestrator provides:
- Task ID and spec reference
- Relevant code file paths
- Constraints from constitution
- Expected output format

### 9.3 Runtime Collaboration

```
User message ("Add a task to buy groceries tomorrow")
    │
    v
FastAPI Route (routes/chat.py or routes/chatkit.py)
    │  Load conversation from DB
    v
AI Agent (agent.py)
    │
    ├── Language Validator → reject if unsupported
    ├── Intent Classifier → ADD_TASK (confidence: 0.95)
    ├── LLM (Groq/OpenAI) → returns tool_call: add_task
    ├── Tool Validator → sanitize arguments
    ├── MCP Server → call_tool("add_task", {...})
    │       │
    │       ├── SQLModel → INSERT INTO tasks
    │       └── Dapr Pub/Sub → publish CREATED event
    │                               │
    │                               v
    │                   Kafka → notification-service
    │                               │
    │                               v
    │                   Reminder scheduled
    │
    ├── Tool result fed back to LLM
    └── LLM generates natural language response
         │
         v
    Response to user: "Task 'Buy groceries' created for tomorrow!"
```

### 9.4 Cross-Agent Boundaries

| Boundary | Rule |
|---|---|
| Frontend ↔ Backend | Communicate via REST API only. No shared runtime state. |
| Agent ↔ MCP Server | Agent calls `call_tool()` in-process. No wire transport. |
| MCP Server ↔ Database | Direct SQLModel sessions for 6 tools; REST API for 5 tools. |
| Backend ↔ Notification Service | Kafka events via Dapr pub/sub. No direct calls. |
| Cron Handlers ↔ Database | Direct DB access within the backend process. |
| Development agent ↔ Runtime agent | No runtime dependency. Development agents write code that runtime agents execute. |

---

## 10. Coding and Documentation Rules

### 10.1 Code Standards

- **Every code file** must include a comment with Task ID and Spec reference:
  ```python
  """
  Task: T-CHAT-004
  Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-4)
  """
  ```
- **Smallest viable diff** — do not refactor unrelated code
- **No manual coding** — Claude Code generates all implementation code (Constitution Principle I)
- **Type hints** required on all public functions (Python), strict TypeScript (frontend)
- **Secrets** via environment variables only; never committed

### 10.2 Documentation Standards

- PHRs created after every significant interaction (routed by stage)
- ADRs suggested (never auto-created) when architectural decisions are detected
- Spec/Plan/Tasks updated before implementation begins
- Commit messages must end with:
  ```
  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

### 10.3 Testing Standards

- Tests reference Task IDs via pytest markers (e.g., `@pytest.mark.mcp`)
- Backend: pytest with unit + integration layers. Target 80% coverage.
- Frontend: Component tests where specified
- TDD enforced only when explicitly requested in specs (Constitution Principle V)

---

## 11. Alignment Matrix

| Constitution Principle | AGENTS.md Enforcement |
|---|---|
| I. Spec-Driven Development | No task = No code. All agents follow Specify → Plan → Tasks → Implement. |
| II. Phased Evolution | Agents work within the current phase. No phase skipping. |
| III. Technology Stack Adherence | Sub-agents use only approved technologies per phase. |
| IV. Independent User Stories | Tasks are independently implementable and testable. |
| V. Test-Driven Development | TDD when specs request it; otherwise optional. |
| VI. Stateless Architecture | Runtime agents store nothing in memory. All state in Neon PostgreSQL. |
| VII. Documentation and Traceability | PHRs, ADRs, Task ID references in all code. |
| VIII. Cloud-Native Architecture | Containers, Helm, health checks, resource limits, Dapr integration. |

---

## 12. Quick Reference

### Before Every Session

Agents must re-read:
1. `.specify/memory/constitution.md` — Principles
2. Relevant spec in `specs/features/` or `specs/phase-*/` — Requirements
3. `CLAUDE.md` — Runtime guidance
4. This file — Agent governance

### Decision Tree

```
Is there a spec for this work?
├── No  → Stop. Run /sp.specify first.
└── Yes → Is there a plan?
          ├── No  → Stop. Run /sp.plan first.
          └── Yes → Are there tasks?
                    ├── No  → Stop. Run /sp.tasks first.
                    └── Yes → Find the Task ID. Implement. Record PHR.
```

### File Governance Map

| File | Governs | Updated By |
|---|---|---|
| `.specify/memory/constitution.md` | All project principles | Amendment procedure only |
| `AGENTS.md` (this file) | All agent behavior | Orchestrator with user consent |
| `CLAUDE.md` | Claude Code runtime guidance | Orchestrator with user consent |
| `specs/api/mcp-tools.md` | MCP tool contracts | Backend agents |
| `.spec-kit/config.yaml` | Project metadata | Orchestrator |
| `.claude/agents/*.md` | Sub-agent personas | Orchestrator with user consent |
| `.claude/commands/sp.*.md` | Workflow commands | Orchestrator with user consent |

---

**Version**: 2.0.0 | **Ratified**: 2026-02-10 | **Aligned with**: Constitution v1.1.0
