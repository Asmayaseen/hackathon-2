# Evolution Todo — Hackathon II

**From CLI to Cloud-Native AI Chatbot in 5 Phases**

A production-grade todo application that evolves from a Python console app into a fully-featured, event-driven, AI-powered chatbot deployed on Kubernetes. Built using **Spec-Driven Development** with Claude Code and Spec-Kit Plus.

---

## Project Structure

```
hackathon-2/
├── phase-1/                 # Phase I: Python Console App
│   ├── src/core/            # TodoManager, TodoItem, Presets
│   ├── interactive_life_manager.py  # 15 life categories, 49 tasks
│   └── tests/               # Unit tests
├── phase-2/                 # Phase II: Full-Stack Web App
│   ├── frontend/            # Next.js 16 (App Router, Tailwind, dark/light theme)
│   └── backend/             # FastAPI + SQLModel + Neon PostgreSQL
├── phase-3/                 # Phase III: AI Chatbot
│   ├── frontend/            # ChatKit UI + Voice input
│   └── backend/             # OpenAI Agents SDK + MCP Server (11 tools)
├── phase-4/                 # Phase IV: Kubernetes Deployment
│   ├── frontend/            # Dockerized Next.js
│   ├── backend/             # Dockerized FastAPI + events
│   ├── helm/                # Helm charts
│   ├── docker-compose.yml
│   └── scripts/             # Deploy scripts
├── phase-5/                 # Phase V: Cloud + Event-Driven
│   ├── kafka/               # Strimzi Kafka cluster
│   ├── dapr-components/     # Pub/Sub, State, Secrets, Cron, Service Invocation
│   ├── notification-service/# Reminder microservice
│   ├── helm/                # Cloud Helm charts
│   ├── monitoring/          # Prometheus + Grafana + Loki
│   └── scripts/             # Cloud setup scripts
├── specs/                   # All specifications
│   ├── features/            # task-crud.md, authentication.md
│   ├── api/                 # rest-endpoints.md, mcp-tools.md
│   ├── database/            # schema.md
│   └── ui/                  # design.md
├── .spec-kit/               # Spec-Kit configuration
├── .specify/                # Constitution and templates
├── .github/workflows/       # CI/CD pipeline
├── history/prompts/         # Prompt History Records
├── CLAUDE.md                # Claude Code instructions
└── AGENTS.md                # Agent behavior rules
```

---

## Phases

### Phase I: Console App (100 pts)
Python in-memory todo manager with 5 core features + Interactive Life Manager with 15 categories and 49 predefined tasks.

```bash
cd phase-1
uv run python interactive_life_manager.py
```

### Phase II: Full-Stack Web App (150 pts)
Next.js 16 frontend + FastAPI backend + Neon PostgreSQL + JWT authentication.

```bash
# Backend
cd phase-2/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd phase-2/frontend
npm install
npm run dev
```

### Phase III: AI Chatbot (200 pts)
Natural language task management via OpenAI Agents SDK + 11 MCP tools + ChatKit UI + Voice input (Whisper).

```bash
# Backend (includes chat + MCP + voice)
cd phase-3/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (includes ChatKit widget)
cd phase-3/frontend
npm install
npm run dev
```

### Phase IV: Kubernetes (250 pts)
Docker containers + Helm charts + Minikube deployment.

```bash
# Docker build
cd phase-4
docker-compose up --build

# Minikube deploy
./scripts/deploy-minikube.sh
```

### Phase V: Cloud + Events (300 pts)
Kafka (Strimzi) + Dapr (5 building blocks) + Notification service + CI/CD + Monitoring.

```bash
# Local with Minikube
./phase-5/scripts/setup-minikube.sh

# Cloud deployment
./phase-5/scripts/setup-cloud.sh
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, Tailwind CSS, OpenAI ChatKit |
| Backend | FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK |
| Database | Neon Serverless PostgreSQL |
| Auth | JWT (HS256, 7-day expiry) |
| AI | OpenAI Agents SDK + 11 MCP tools |
| Voice | OpenAI Whisper / Groq |
| Containers | Docker (multi-stage builds) |
| Orchestration | Kubernetes (Minikube + Cloud) |
| Package Manager | Helm Charts |
| Events | Apache Kafka (Strimzi operator) |
| App Runtime | Dapr (Pub/Sub, State, Bindings, Secrets, Service Invocation) |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana + Loki |
| Spec-Driven | Claude Code + Spec-Kit Plus |

---

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host/dbname
JWT_SECRET=your-secret-key-min-32-characters
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...          # Optional: for voice transcription
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## API Overview

30+ REST endpoints across 16 domains. Full documentation: `specs/api/rest-endpoints.md`

| Domain | Key Endpoints |
|---|---|
| Auth | `POST /api/auth/signup`, `POST /api/auth/signin` |
| Tasks | `GET/POST /api/{user_id}/tasks`, `PUT/DELETE /api/{user_id}/tasks/{id}` |
| Chat | `POST /api/{user_id}/chat` |
| Search | `GET /api/{user_id}/search?q=...` |
| Stats | `GET /api/{user_id}/stats` |
| Voice | `POST /api/{user_id}/transcribe` |

---

## Specifications

All development follows Spec-Driven Development. Key specs:

| Spec | Path |
|---|---|
| Task CRUD | `specs/features/task-crud.md` |
| Authentication | `specs/features/authentication.md` |
| REST API | `specs/api/rest-endpoints.md` |
| MCP Tools | `specs/api/mcp-tools.md` |
| Database | `specs/database/schema.md` |
| UI Design | `specs/ui/design.md` |
| Phase III | `specs/phase-3-chatbot/spec.md` |
| Constitution | `.specify/memory/constitution.md` |

---

## Development Workflow

```
Specify -> Plan -> Tasks -> Implement -> Record (PHR)
```

1. Write specification in `specs/`
2. Generate plan
3. Break into atomic tasks
4. Implement via Claude Code
5. Record Prompt History in `history/prompts/`

See `AGENTS.md` for agent behavior rules and `CLAUDE.md` for Claude Code instructions.

---

## License

Hackathon project for Panaversity PIAIC/GIAIC.
