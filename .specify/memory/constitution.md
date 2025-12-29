<!--
SYNC IMPACT REPORT
==================
Version change: [NEW] → 1.0.0
This is the initial constitution for the Evolution of Todo hackathon project.

Added sections:
- Core Principles (7 principles defined)
- Technology Stack Requirements
- Development Workflow
- Governance

Templates requiring updates:
✅ plan-template.md - Constitution Check section aligns with principles
✅ spec-template.md - User scenarios and requirements align with spec-driven approach
✅ tasks-template.md - Task structure supports independent testing and TDD when required

Follow-up TODOs: None
-->

# Evolution of Todo Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All development MUST follow the Spec-Driven Development workflow: Specify → Plan → Tasks → Implement.

- No code may be written without a completed and approved specification
- Every implementation task MUST reference a Task ID from tasks.md
- Specifications MUST be refined iteratively until Claude Code generates correct output
- Manual coding is prohibited; Claude Code MUST generate all implementation code
- All architectural decisions MUST be documented in plan.md before implementation

**Rationale**: Ensures alignment across agents, prevents "vibe coding," and guarantees
traceability from requirements to implementation. Critical for AI-driven development where
specifications guide code generation.

### II. Phased Evolution

Features MUST be developed incrementally following the hackathon phase structure:

- Phase I: In-memory console application (Python, Basic Level features)
- Phase II: Full-stack web application (Next.js, FastAPI, Neon DB, Basic Level)
- Phase III: AI-powered chatbot (OpenAI Agents SDK, MCP Server, Basic Level)
- Phase IV: Local Kubernetes deployment (Minikube, Helm, kubectl-ai, Basic Level)
- Phase V: Advanced cloud deployment (Event-driven with Kafka/Dapr, Advanced Level)

Each phase MUST be complete and functional before advancing to the next. No phase may be
skipped. Each phase builds upon the previous phase's functionality.

**Rationale**: Mimics real-world software evolution from prototype to production-grade
distributed system. Ensures learning progression and allows independent validation at each stage.

### III. Technology Stack Adherence

The following technology stack is mandatory and MUST NOT be substituted:

**Phase I:**
- Language: Python 3.13+
- Package Manager: UV
- Development: Claude Code + Spec-Kit Plus

**Phase II:**
- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT

**Phase III:**
- Frontend: OpenAI ChatKit
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK
- Database: Same as Phase II (Neon)

**Phase IV & V:**
- Containerization: Docker (Docker Desktop with Gordon AI Agent)
- Orchestration: Kubernetes (Minikube local, DOKS/GKE/AKS cloud)
- Package Manager: Helm Charts
- AI DevOps: kubectl-ai, kagent
- Event Streaming (Phase V): Kafka (Redpanda Cloud or Strimzi self-hosted)
- Application Runtime (Phase V): Dapr

Additional tools and libraries may be added but core stack MUST remain as specified.

**Rationale**: Ensures consistent evaluation criteria across all hackathon participants and
provides hands-on experience with modern AI-native, cloud-native technology stack.

### IV. Independent User Stories

User stories MUST be:

- Prioritized (P1, P2, P3...) with P1 being most critical
- Independently implementable without requiring other stories
- Independently testable with clear acceptance criteria
- Capable of delivering standalone value as an MVP increment

Each user story MUST include:
- Clear priority level and justification
- Independent test description
- Given/When/Then acceptance scenarios

**Rationale**: Enables iterative delivery, parallel development when possible, and ensures
each story can be validated independently. Critical for spec-driven approach where each
story maps to distinct task groups.

### V. Test-Driven Development (Conditional)

When tests are explicitly requested in specifications:

- Tests MUST be written BEFORE implementation
- Tests MUST fail initially (Red phase)
- Implementation proceeds only after tests fail (Green phase)
- Refactoring follows successful implementation (Refactor phase)
- Red-Green-Refactor cycle is strictly enforced

When tests are NOT requested:
- TDD is optional
- Focus remains on functional requirements and acceptance criteria

**Rationale**: Enforces test-first discipline when quality assurance is prioritized, but
recognizes that hackathon velocity may prioritize feature delivery over comprehensive
test coverage in some phases.

### VI. Stateless Architecture

Backend services MUST be stateless:

- All state MUST be persisted to database (Neon PostgreSQL)
- No in-memory session storage on server
- Conversation state stored in database tables (Phase III+)
- Server restarts MUST NOT lose user data or context
- Horizontal scalability MUST be possible

**Rationale**: Prepares for Kubernetes deployment (Phase IV-V) where pods can be
terminated and rescheduled. Enables resilient, scalable architecture essential for
cloud-native applications.

### VII. Documentation and Traceability

All work MUST maintain comprehensive documentation:

- Constitution (this file): Project principles and constraints
- Spec files (specs/*/spec.md): WHAT to build with user stories and acceptance criteria
- Plan files (specs/*/plan.md): HOW to build with architecture and technical decisions
- Tasks files (specs/*/tasks.md): Breakdown into testable, atomic work units
- CLAUDE.md: Runtime guidance for Claude Code
- Prompt History Records (history/prompts/): Every significant user interaction
- Architecture Decision Records (history/adr/): All significant architectural decisions

Code files MUST include comments linking to Task IDs and relevant spec sections.

**Rationale**: Ensures traceability from requirements through implementation, enables
knowledge transfer, and provides learning artifacts for hackathon evaluation.

## Technology Stack Requirements

### Mandatory Technologies by Phase

See Principle III (Technology Stack Adherence) for complete stack requirements.

### MCP Server Architecture (Phase III+)

The MCP server MUST:
- Expose task operations as standardized tools using Official MCP SDK
- Be stateless with all state persisted to database
- Implement tools: add_task, list_tasks, complete_task, delete_task, update_task
- Accept user_id parameter for all operations to ensure data isolation
- Return structured responses with task_id, status, and title

### Event-Driven Architecture (Phase V)

Kafka topics MUST follow this structure:
- task-events: All CRUD operations on tasks
- reminders: Scheduled reminder triggers
- task-updates: Real-time client synchronization events

Dapr building blocks MUST be used for:
- Pub/Sub: Kafka abstraction
- State Management: Conversation and task state
- Service Invocation: Inter-service communication
- Bindings/Jobs API: Scheduled reminders
- Secrets Management: API keys and credentials

## Development Workflow

### Spec-Driven Development Lifecycle

1. **Specify** (/sp.specify or manual spec creation):
   - Document user stories with priorities
   - Define functional requirements
   - Establish acceptance criteria
   - Capture edge cases

2. **Plan** (/sp.plan):
   - Research existing codebase and dependencies
   - Design architecture and component structure
   - Define data models and API contracts
   - Document technical decisions

3. **Tasks** (/sp.tasks):
   - Break plan into atomic, testable tasks
   - Organize by user story for independent implementation
   - Mark parallelizable tasks with [P]
   - Link tasks to spec sections

4. **Implement** (/sp.implement or manual with Claude Code):
   - Execute tasks in dependency order
   - Generate code via Claude Code (no manual coding)
   - Reference Task IDs in all code
   - Validate against acceptance criteria

5. **Record** (automated PHR creation):
   - Capture prompts and responses in history/prompts/
   - Route by stage (constitution, spec, plan, tasks, etc.)
   - Maintain complete audit trail

### Commit and Deployment Standards

- Commits MUST be created when explicitly requested by user
- Commit messages MUST end with: "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
- Co-authored by: "Claude Sonnet 4.5 <noreply@anthropic.com>"
- Pull requests MUST include summary and test plan
- Each phase MUST be deployable and demonstrable independently

### Hackathon Submission Requirements

Each phase submission MUST include:
- Public GitHub repository with all source code
- /specs folder with specification files
- CLAUDE.md with Claude Code instructions
- README.md with setup instructions
- Deployed application links (Vercel for frontend, Phase III+ for chatbot)
- Demo video (maximum 90 seconds)
- WhatsApp number for presentation invitation

## Governance

### Amendment Procedure

This constitution supersedes all other project practices and conventions.

Amendments require:
1. Documented rationale for change
2. Impact analysis on existing specs, plans, and tasks
3. Version increment following semantic versioning:
   - MAJOR: Breaking changes to principles or workflow
   - MINOR: New principles or expanded guidance
   - PATCH: Clarifications, typo fixes, non-semantic refinements
4. Update to all dependent template files
5. Sync Impact Report documenting changes

### Compliance

- All pull requests and code reviews MUST verify compliance with constitution
- Any violation of NON-NEGOTIABLE principles MUST be rejected
- Complexity that violates principles MUST be explicitly justified in plan.md
- Constitution takes precedence over: Specify > Plan > Tasks in case of conflicts

### Runtime Guidance

For runtime development guidance and agent-specific instructions, refer to CLAUDE.md.
For project-specific implementation patterns, refer to phase-specific documentation
in specs/*/plan.md files.

**Version**: 1.0.0 | **Ratified**: 2025-12-24 | **Last Amended**: 2025-12-24
