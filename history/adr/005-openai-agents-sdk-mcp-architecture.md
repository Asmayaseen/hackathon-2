# ADR-005: OpenAI Agents SDK + MCP for AI Chatbot Architecture

**Status**: Accepted
**Date**: 2026-02-11
**Decision Makers**: asmayaseen
**Context**: Phase III AI chatbot agent framework and tool integration

## Context

Phase III transforms the Todo web application into an AI-powered conversational interface. Users interact with a chatbot that can create, query, update, and delete tasks through natural language. This requires three architectural decisions:

1. **AI framework**: How to orchestrate LLM calls, tool invocations, and conversation state.
2. **Tool integration**: How the AI agent accesses task operations (CRUD, search, analytics).
3. **LLM provider**: Which model serves the chat completions.

The hackathon mandates OpenAI Agents SDK, Official MCP SDK, and OpenAI ChatKit as the Phase III stack.

## Decision

### Architecture

```
User Message
    |
    v
Intent Classifier (rule-based pre-filter)
    |
    v
OpenAI Agents SDK (AsyncOpenAI + function calling)
    |
    v
MCP Server (11 tools, in-process, direct DB access)
    |
    v
Neon PostgreSQL (via SQLModel)
```

### Specific Choices

1. **OpenAI Python SDK** (`AsyncOpenAI`) with function calling as the agent runtime. The lower-level `chat.completions.create()` API is used rather than the higher-level `Agent`/`Runner` classes from the Agents SDK.

2. **Official MCP Python SDK** (`mcp.server.Server`) exposing 11 tools: `list_tasks`, `create_task`, `update_task`, `delete_task`, `search_tasks`, `get_task_stats`, `mark_complete`, `set_reminder`, `get_overdue`, `get_upcoming`, `complete_recurring`.

3. **Dual LLM provider strategy**:
   - **Primary**: Groq (`llama-3.3-70b-versatile`) -- free, fast inference.
   - **Fallback**: OpenAI (`gpt-4o` or `gpt-4o-mini`) -- higher quality, paid.
   - Selection via environment variable: `GROQ_API_KEY` takes priority over `OPENAI_API_KEY`.

4. **Safety layers**: intent classifier pre-filters messages, tool validator sanitizes arguments, `user_id` injected by the agent (never LLM-supplied), conversation context limited to 10 messages.

## Alternatives Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **OpenAI SDK + function calling (chosen)** | Full control over tool dispatch, works with any OpenAI-compatible API (Groq), transparent prompt engineering | Lower-level than Agent/Runner, manual conversation management | Chosen for Groq compatibility and control |
| Agents SDK `Agent`/`Runner` classes | Higher-level abstraction, built-in tool dispatch, handoff support | Requires OpenAI API (no Groq), opaque orchestration, harder to debug | Rejected: incompatible with free Groq provider |
| LangChain Agent | Large ecosystem, many integrations, memory abstractions | Heavy dependency, abstraction overhead, version churn, slower | Rejected: over-engineered for 11 tools |
| Custom agent loop (no SDK) | Maximum control, no dependencies | Reinvents function calling, error-prone, no ecosystem | Rejected: unnecessary when OpenAI SDK exists |

### MCP vs Alternatives (see also ADR-002)

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **MCP Server (chosen)** | Standardized tool interface, hackathon requirement, composable | Extra abstraction layer | Mandated and architecturally sound |
| Direct REST calls from agent | Reuses existing endpoints | Agent must manage HTTP, auth tokens, error parsing | Rejected: fragile and duplicative |
| Embedded functions (no protocol) | Simplest | Non-standard, untestable in isolation | Rejected |

### LLM Provider Strategy

| Provider | Cost | Speed | Quality | Verdict |
|----------|------|-------|---------|---------|
| **Groq (primary)** | Free | ~200ms TTFT | Good (Llama 3.3 70B) | Default for development and hackathon demo |
| **OpenAI (fallback)** | $2.50-15/M tokens | ~500ms TTFT | Excellent (GPT-4o) | Available when Groq quota exhausted |
| Anthropic Claude | $3-15/M tokens | ~400ms TTFT | Excellent | Not OpenAI-compatible API, would need separate client |
| Local Ollama | Free | Slow (~2-5s) | Variable | Unacceptable latency for chat UX |

## Consequences

### Positive

- **Zero LLM cost**: Groq's free tier handles all hackathon demo traffic.
- **Fast inference**: Groq's ~200ms time-to-first-token enables responsive chat UX.
- **Provider-agnostic**: `AsyncOpenAI` client works with any OpenAI-compatible API (Groq, Together, Fireworks) by changing `base_url`.
- **MCP standardization**: 11 tools follow a protocol that other MCP-compatible agents can consume.
- **Safety**: four-layer defense (intent classifier, tool validator, user_id injection, context window limit) prevents prompt injection from accessing other users' data.

### Negative

- **Two code paths**: REST routes and MCP tools perform the same operations on the same database. Business logic is partially duplicated.
- **Groq limitations**: free tier has rate limits (30 RPM on some models); Llama 3.3 occasionally hallucinates tool arguments.
- **No streaming**: current implementation waits for full LLM response before returning. Streaming would improve perceived latency.

### Risks

- Groq may change free tier terms, requiring migration to paid OpenAI or self-hosted models.
- MCP SDK is evolving; breaking changes may require tool schema updates.
- Function calling with 5 exposed tools occasionally produces malformed JSON arguments, requiring retry logic.

## Related

- ADR-002: `history/adr/002-mcp-over-direct-api.md` (MCP over direct API)
- Agent implementation: `phase-4/backend/agent.py`
- MCP server: `phase-4/backend/mcp_server.py`
- Chatbot spec: `specs/features/chatbot.md`
- Phase III spec: `specs/phase-3-chatbot/spec.md`
- Safety architecture: `AGENTS.md`
