# Skills & Agents Usage Guide for Phase 3

## Overview
This document shows all available custom agents and skills, which ones we've used, and which ones to use for remaining tasks.

---

## Custom Agents Used ✅

### 1. nextjs-frontend-expert ✅ USED
**Location:** `.claude/agents/nextjs-frontend-expert.md`

**When Used:** Adding AI Chat to navbar and homepage

**What It Did:**
- Modified `Navbar.tsx:41` - Added AI Chat link with cyan/fuchsia gradient
- Modified `page.tsx:122` - Added AI Assistant button in hero
- Modified `page.tsx:170-192` - Added featured AI-Powered Assistant card
- Applied cyber theme (neon glows, glassmorphism, responsive design)

**Skills It Uses:**
- building-nextjs-apps
- styling-with-shadcn
- framer-motion (for animations)

---

### 2. chatkit-backend-engineer ✅ USED
**Location:** `.claude/agents/chatkit-backend-engineer.md`

**When Used:** Initial Phase 3 implementation attempt

**What It Did:**
- Created chatkit_server.py (later commented out due to SDK unavailability)
- Designed event handlers and Store contracts
- Used OpenAI Agents SDK patterns

**Skills It Uses:**
- scaffolding-openai-agents
- building-mcp-servers

---

### 3. chatkit-frontend-engineer ✅ USED
**Location:** `.claude/agents/chatkit-frontend-engineer.md`

**When Used:** Debugging blank ChatKit widget issues

**What It Did:**
- Identified CORS issues with voice transcription
- Fixed CDN loading problems
- Debugged authentication flows

**Skills It Uses:**
- building-chat-interfaces
- systematic-debugging

---

### 4. backend-testing ⏳ ATTEMPTED (Rate Limited)
**Location:** `.claude/agents/backend-testing.md`

**When To Resume:** After rate limit resets (5pm Asia/Karachi)

**What It Should Do:**
- Create unit tests for agent.py (AI agent logic)
- Create integration tests for mcp_server.py (database operations)
- Create API tests for routes/chat.py and routes/voice.py
- Achieve 80%+ code coverage

**Agent ID to Resume:** `aa64cad`

**Skills It Uses:**
- systematic-debugging (for test case design)
- building-mcp-servers (for testing MCP tools)

---

## Custom Agents Available (Not Yet Used)

### 5. fullstack-architect 🔮 RECOMMENDED FOR DEPLOYMENT
**Location:** `.claude/agents/fullstack-architect.md`

**When To Use:**
- Before deploying to Hugging Face Spaces + Vercel
- For environment variable planning
- For CORS configuration review
- For production readiness checklist

**Capabilities:**
- Full-stack design decisions
- JWT token flow verification
- Environment configuration review
- Deployment considerations

**Next Steps:**
```bash
# Use for deployment planning
Task tool with subagent_type='fullstack-architect'
Prompt: "Review Phase 3 for production deployment to Hugging Face Spaces (backend) and Vercel (frontend)"
```

---

### 6. fastapi-backend-expert 🔮 USE FOR CODE REVIEW
**Location:** `.claude/agents/fastapi-backend-expert.md`

**When To Use:**
- Review routes/chat.py and routes/voice.py
- Verify FastAPI best practices
- Check error handling and validation
- Ensure proper dependency injection

**Next Steps:**
```bash
Task tool with subagent_type='fastapi-backend-expert'
Prompt: "Review routes/chat.py and routes/voice.py for FastAPI best practices, security, and error handling"
```

---

### 7. auth-expert 🔮 USE FOR AUTH REVIEW
**Location:** `.claude/agents/auth-expert.md`

**When To Use:**
- Review JWT authentication in middleware/auth.py
- Verify Better Auth integration
- Check token validation and expiration

**Next Steps:**
```bash
Task tool with subagent_type='auth-expert'
Prompt: "Review JWT authentication implementation in middleware/auth.py and verify Better Auth integration"
```

---

### 8. ui-ux-expert 🔮 OPTIONAL FOR POLISH
**Location:** `.claude/agents/ui-ux-expert.md`

**When To Use:**
- Polish chat UI/UX before demo
- Improve accessibility
- Refine animations and transitions

---

## Project Skills Available

### Skills We Should Use Now

#### 1. systematic-debugging ✅ USE FOR ANY ISSUES
**Skill:** `systematic-debugging`

**Invoke With:**
```bash
Skill tool: skill="systematic-debugging"
```

**When To Use:**
- Any bug appears
- Test failures
- Unexpected behavior
- **ESPECIALLY** when under time pressure

**What It Does:**
- 4-phase debugging methodology
- Root cause investigation FIRST (no random fixes)
- Pattern analysis
- Hypothesis testing

---

#### 2. neon-postgres 🔮 USE FOR DB OPTIMIZATION
**Skill:** `neon-postgres`

**Invoke With:**
```bash
Skill tool: skill="neon-postgres"
```

**When To Use:**
- Before deployment to optimize database queries
- Connection pooling configuration
- Database branching for dev/prod
- Serverless driver optimization

**What It Does:**
- Neon-specific optimization patterns
- Serverless connection handling
- Branching workflow guidance

---

#### 3. building-mcp-servers 🔮 USE FOR MCP REVIEW
**Skill:** `building-mcp-servers`

**Invoke With:**
```bash
Skill tool: skill="building-mcp-servers"
```

**When To Use:**
- Review mcp_server.py implementation
- Verify tool design best practices
- Check authentication patterns

**What It Does:**
- MCP protocol best practices
- Tool naming conventions
- Context management
- Actionable error messages

---

#### 4. scaffolding-openai-agents 🔮 USE FOR AGENT REVIEW
**Skill:** `scaffolding-openai-agents`

**Invoke With:**
```bash
Skill tool: skill="scaffolding-openai-agents"
```

**When To Use:**
- Review agent.py implementation
- Verify OpenAI Agents SDK patterns
- Check function calling patterns

---

#### 5. streaming-llm-responses ⭐ RECOMMENDED FOR ENHANCEMENT
**Skill:** `streaming-llm-responses`

**Invoke With:**
```bash
Skill tool: skill="streaming-llm-responses"
```

**When To Use:**
- Add streaming responses to chat (better UX)
- Implement SSE (Server-Sent Events)
- Show tokens as they're generated

**What It Does:**
- Token streaming patterns
- SSE implementation
- Frontend integration for streaming

---

#### 6. building-nextjs-apps ✅ ALREADY USED
**Skill:** `building-nextjs-apps`

**Used By:** nextjs-frontend-expert agent

**What It Covered:**
- Next.js 16 App Router patterns
- Async params handling
- Server vs Client Components
- proxy.ts for authentication

---

#### 7. building-chat-interfaces ✅ ALREADY USED
**Skill:** `building-chat-interfaces`

**Used By:** chatkit-frontend-engineer agent

**What It Covered:**
- Chat UI patterns
- Message list rendering
- Markdown formatting
- Streaming message display

---

#### 8. styling-with-shadcn ✅ ALREADY USED
**Skill:** `styling-with-shadcn`

**Used By:** nextjs-frontend-expert agent

**What It Covered:**
- Shadcn UI components
- TailwindCSS patterns
- Cyber theme styling (cyan/fuchsia gradients)

---

### Skills for Future Enhancements

#### 9. containerizing-applications 🚀 FOR DEPLOYMENT
**Skill:** `containerizing-applications`

**When To Use:**
- Dockerize backend for Hugging Face Spaces
- Create docker-compose for local dev
- Write Dockerfile with best practices

---

#### 10. deploying-cloud-k8s 🚀 OPTIONAL
**Skill:** `deploying-cloud-k8s`

**When To Use:**
- If deploying to Kubernetes instead of Hugging Face/Vercel
- CI/CD pipeline setup

---

## Spec-Kit Commands

### 1. sp.phr ✅ USED
**Command:** `/sp.phr` or `Skill tool: skill="sp.phr"`

**Used:** Created PHR after debugging ChatKit issues

**Created:** `history/prompts/phase-3-chatbot/003-phase3-chatkit-debugging.green.prompt.md`

**Auto-creates PHR after work:**
- Detects stage (constitution, spec, plan, tasks, red, green, etc.)
- Routes to correct directory
- Captures full prompt and response

---

### 2. sp.git.commit_pr ⏳ NEXT TO USE
**Command:** `Skill tool: skill="sp.git.commit_pr"`

**When To Use:** After testing is complete

**What It Does:**
- Autonomous Git workflow
- Analyzes repository state
- Creates intelligent commit messages
- Creates feature branch if needed
- Pushes to remote
- Creates PR with description

**Workflow:**
```bash
# 1. Agent analyzes changes
git status --porcelain
git diff --stat

# 2. Decides branch strategy
# 3. Generates commit message based on actual changes
# 4. Creates commit
# 5. Pushes to remote
# 6. Creates PR with gh CLI
```

---

### 3. sp.adr 🔮 SHOULD DOCUMENT DECISIONS
**Command:** `Skill tool: skill="sp.adr"`

**When To Use:**
- Document architecturally significant decisions
- After choosing Groq vs OpenAI
- After deciding on MCP direct DB access vs HTTP

**Example ADR Topics:**
- "Why we chose direct database access for MCP tools instead of HTTP endpoints"
- "Why we use Groq API instead of OpenAI for AI agent"
- "Why we created backend Whisper proxy instead of direct browser calls"

---

### 4. sp.implement 🔮 FOR FEATURE IMPLEMENTATION
**Command:** `Skill tool: skill="sp.implement"`

**When To Use:**
- Execute implementation from tasks.md
- After planning is complete

---

### 5. sp.analyze 🔮 FOR QUALITY CHECK
**Command:** `Skill tool: skill="sp.analyze"`

**When To Use:**
- Cross-artifact consistency check
- After completing spec, plan, and tasks
- Before deployment

---

## Recommended Workflow for Remaining Tasks

### Task 1: Complete Backend Testing (When Rate Limit Resets)
```bash
# Resume the backend-testing agent
Task tool with resume="aa64cad"
```

**Skills It Will Use:**
- systematic-debugging
- building-mcp-servers

---

### Task 2: Review Code Quality
```bash
# 1. Review FastAPI code
Task tool with subagent_type='fastapi-backend-expert'
Prompt: "Review routes/chat.py and routes/voice.py for best practices"

# 2. Review MCP implementation
Skill tool: skill="building-mcp-servers"
# Then ask: "Review mcp_server.py for MCP best practices"

# 3. Review AI agent
Skill tool: skill="scaffolding-openai-agents"
# Then ask: "Review agent.py for OpenAI Agents SDK patterns"
```

---

### Task 3: Document Architecture Decisions
```bash
Skill tool: skill="sp.adr"

# Document:
1. Direct DB access for MCP tools (vs HTTP endpoints)
2. Groq API choice (vs OpenAI)
3. Backend Whisper proxy (vs direct browser calls)
4. OpenAI Agents SDK integration pattern
```

---

### Task 4: Optimize Database
```bash
Skill tool: skill="neon-postgres"

# Ask: "Review database configuration for Neon PostgreSQL production deployment"
```

---

### Task 5: Commit and Create PR
```bash
Skill tool: skill="sp.git.commit_pr"

# Autonomous workflow will:
1. Analyze all changes
2. Create feature branch (if needed)
3. Generate commit message
4. Create PR with description
```

---

### Task 6: Deployment Planning
```bash
Task tool with subagent_type='fullstack-architect'

Prompt: "Review Phase 3 for production deployment:
- Backend to Hugging Face Spaces
- Frontend to Vercel
- Environment variable configuration
- CORS setup
- JWT flow in production"
```

---

### Task 7: OPTIONAL - Add Streaming Responses
```bash
Skill tool: skill="streaming-llm-responses"

# Ask: "Add streaming responses to chat endpoint for better UX"
```

---

## Summary of Skills/Agents by Use Case

### ✅ Already Used (Completed Work)
1. nextjs-frontend-expert - Added AI Chat to navbar/homepage
2. chatkit-backend-engineer - ChatKit server (commented out)
3. chatkit-frontend-engineer - Debugging
4. sp.phr - Created PHR

### ⏳ In Progress
1. backend-testing - Creating comprehensive tests (rate limited, resume: aa64cad)

### 🔮 Recommended Next Steps
1. fastapi-backend-expert - Code review
2. auth-expert - Auth review
3. fullstack-architect - Deployment planning
4. sp.git.commit_pr - Commit and PR
5. sp.adr - Document decisions
6. neon-postgres - DB optimization
7. building-mcp-servers - MCP review
8. scaffolding-openai-agents - Agent review

### ⭐ Optional Enhancements
1. streaming-llm-responses - Add streaming
2. ui-ux-expert - Polish UI
3. containerizing-applications - Dockerize

---

## How to Invoke Skills vs Agents

### Agents (Use Task Tool)
```bash
Task tool:
  subagent_type: "nextjs-frontend-expert"
  description: "Add feature to chat UI"
  prompt: "Detailed task description..."
```

### Skills (Use Skill Tool)
```bash
Skill tool:
  skill: "systematic-debugging"

# Then in next message, describe what to debug
```

### Commands (Use Skill Tool with sp. prefix)
```bash
Skill tool:
  skill: "sp.git.commit_pr"

# Autonomous workflow executes
```

---

## Current Status Summary

### ✅ Completed
- Backend running (port 8000) with Groq API
- Frontend running (port 3000) with AI Chat in navbar/homepage
- Voice transcription endpoint working
- MCP tools working (direct DB access)
- AI agent working with OpenAI Agents SDK
- Conversation persistence working

### ⏳ In Progress
- Backend testing (rate limited, resume after 5pm)

### 🔮 Next Steps
1. Wait for rate limit reset OR proceed with manual testing
2. Use fastapi-backend-expert for code review
3. Use sp.git.commit_pr to commit work
4. Use fullstack-architect for deployment planning
5. Deploy to Hugging Face Spaces + Vercel
6. Record demo video

### 📋 Files Created
- TEST_CHECKLIST.md - 10 comprehensive test cases
- READY_FOR_TESTING.md - User testing guide
- SKILLS_AND_AGENTS_USAGE.md - This file

---

**Created:** 2026-01-06
**Agent Session:** Phase 3 Chatbot Implementation
**Next Action:** Test chatbot manually OR wait for rate limit reset to run backend-testing agent
