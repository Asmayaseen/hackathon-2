# ADR-002: MCP Server Over Direct API Calls for AI Agent

**Status**: Accepted
**Date**: 2026-01-10
**Decision Makers**: asmayaseen
**Context**: Phase III chatbot tool architecture

## Context

The AI chatbot needs to perform task operations (CRUD) on behalf of the user. The agent could either call the REST API directly or use an MCP (Model Context Protocol) server that exposes operations as tools.

## Decision

Use the **Official MCP SDK** to expose task operations as 11 standardized tools that the OpenAI Agents SDK invokes during conversations. The MCP server operates in-process (same FastAPI backend) and writes directly to the database via SQLModel.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **MCP Server (chosen)** | Standardized tool interface, composable, agent can chain tools, protocol-compliant | Additional abstraction layer, tool schemas to maintain |
| Direct REST API calls | Simpler, reuses existing endpoints | Agent must construct HTTP requests, handle auth tokens, parse responses |
| Custom function tools | Flexible, no protocol overhead | Non-standard, harder to test in isolation, no ecosystem support |

## Rationale

- MCP is the hackathon-required protocol (Official MCP SDK specified)
- Standardized tool schemas enable better AI agent behavior
- In-process execution avoids HTTP overhead and self-authentication complexity
- 11 tools cover all CRUD + search + analytics + recurring + reminders

## Consequences

- **Positive**: Clean separation between AI logic and data operations, standardized interface, easy to add new tools
- **Negative**: Two code paths for the same operations (REST routes + MCP tools)
- **Mitigated by**: MCP tools write directly to DB (no REST call duplication)

## Related

- `specs/api/mcp-tools.md`
- `phase-4/backend/mcp_server.py`
- `specs/phase-3-chatbot/spec.md`
