# Phase 3 Chatbot - End-to-End Test Checklist

## Test Date: 2026-01-06

## Prerequisites ✅
- [✅] Backend running on http://localhost:8000
- [✅] Frontend running on http://localhost:3000
- [✅] Database connected (Neon PostgreSQL)
- [✅] Environment variables configured (.env files)
- [✅] GROQ_API_KEY configured for AI agent

## Component Status

### Backend Components
- [✅] FastAPI server: Running
- [✅] Database connection: Connected
- [✅] All tables loaded: users, tasks, task_history, user_preferences, tags, notifications, conversations, messages
- [✅] Voice transcription endpoint: `/api/{user_id}/transcribe`
- [✅] Chat endpoint: `/api/{user_id}/chat`
- [✅] Conversations endpoint: `/api/{user_id}/conversations`
- [✅] Messages endpoint: `/api/{user_id}/conversations/{conversation_id}/messages`

### Frontend Components
- [✅] Next.js 16 App Router: Running
- [✅] API URL configured: http://localhost:8000
- [✅] AI Chat navbar link: Added (line 41 Navbar.tsx)
- [✅] Homepage AI Assistant button: Added (line 122 page.tsx)
- [✅] Featured AI card: Added (lines 170-192 page.tsx)

### MCP Tools (AI Agent Capabilities)
- [✅] `add_task` - Create new tasks
- [✅] `list_tasks` - Search/filter tasks
- [✅] `complete_task` - Mark tasks as done
- [✅] Direct database access (no HTTP/auth issues)
- [✅] inputSchema validation fixed

## End-to-End Test Plan

### Test 1: User Authentication
**Steps:**
1. Navigate to http://localhost:3000/
2. Click "Sign In" or "Get Started"
3. Create account or sign in with existing credentials
4. Verify JWT token stored in localStorage

**Expected Result:**
- User redirected to `/tasks` page
- localStorage contains: `auth_token`, `user_id`, `user_email`, `user_name`

**Status:** ⏳ PENDING - Requires user to manually test

---

### Test 2: Navigate to AI Chat
**Steps:**
1. Click "AI Chat" in navbar (should have cyan/fuchsia gradient highlight)
2. Verify chat page loads at `/chat`

**Expected Result:**
- Chat interface appears with:
  - "Evolution AI Assistant" title
  - Message input field
  - Voice input button (microphone icon)
  - Send button

**Status:** ⏳ PENDING - User needs to hard refresh (Ctrl + Shift + R)

---

### Test 3: Text Chat - Task Creation (English)
**Input:** "Add a task to buy milk tomorrow"

**Expected AI Response:**
```
✅ Task created: 'Buy milk' due tomorrow
```

**Expected Backend Behavior:**
1. Agent receives message
2. Agent calls `add_task` tool via MCP
3. Tool writes directly to database (no 401 error)
4. Task created in `tasks` table with user_id, title, due_date
5. Agent responds with confirmation

**Status:** ⏳ PENDING - Requires manual test

---

### Test 4: Text Chat - Task Listing
**Input:** "Show me all my tasks"

**Expected AI Response:**
```
📋 Found 1 task(s):
⬜ Buy milk - Due: 2026-01-07
```

**Expected Backend Behavior:**
1. Agent calls `list_tasks` tool
2. Tool queries database with user_id filter
3. Returns tasks in formatted list

**Status:** ⏳ PENDING

---

### Test 5: Text Chat - Task Completion
**Input:** "Mark task 1 as done"

**Expected AI Response:**
```
✅ Task marked as completed
```

**Expected Backend Behavior:**
1. Agent calls `complete_task` tool
2. Tool updates task status to "completed" in database
3. Confirms success

**Status:** ⏳ PENDING

---

### Test 6: Voice Input (English)
**Steps:**
1. Click microphone button
2. Allow browser microphone access
3. Say: "Add a task to call dentist"
4. Stop recording

**Expected Result:**
1. Audio uploaded to backend `/api/{user_id}/transcribe`
2. Whisper API transcribes audio
3. Transcribed text appears in input field: "Add a task to call dentist"
4. User can edit or send directly

**Status:** ⏳ PENDING

---

### Test 7: Bilingual Support - Urdu (اردو)
**Input (Text):** "ایک کام بنائیں - گروسری شاپنگ"
(Translation: "Create a task - grocery shopping")

**Expected AI Response (Urdu):**
```
✅ کام بنایا گیا: 'گروسری شاپنگ'
```

**Expected Backend Behavior:**
- Agent detects Urdu language
- Responds in Urdu
- Task created successfully

**Status:** ⏳ PENDING

---

### Test 8: Voice Input (Urdu)
**Steps:**
1. Click microphone button
2. Say in Urdu: "کل میری میٹنگ ہے" (Tomorrow I have a meeting)
3. Stop recording

**Expected Result:**
- Whisper auto-detects Urdu language
- Transcribes correctly
- AI responds in Urdu

**Status:** ⏳ PENDING

---

### Test 9: Conversation History
**Steps:**
1. Send multiple messages
2. Refresh page
3. Verify conversation persists

**Expected Result:**
- Conversations stored in `conversations` table
- Messages stored in `messages` table
- On page load, previous conversation loads

**Status:** ⏳ PENDING

---

### Test 10: Error Handling
**Test Case 1: Invalid Date**
- Input: "Add task due yesterday"
- Expected: AI asks for clarification or sets today

**Test Case 2: Ambiguous Task**
- Input: "Add task"
- Expected: AI asks "What task would you like to add?"

**Status:** ⏳ PENDING

---

## Known Issues to Verify Fixed

### Issue 1: 401 Unauthorized (demo-user-id)
**Previous Error:** Frontend hardcoded "demo-user-id" which doesn't exist
**Fix Applied:** Use real user_id from localStorage
**Verification:** ⏳ Check backend logs show no more "demo-user-id" 401 errors

### Issue 2: MCP Tools inputSchema Validation
**Previous Error:** `Field required [type=missing, input_value={'name': 'add_task'...`
**Fix Applied:** Changed `input_schema` to `inputSchema` in mcp_server.py and agent.py
**Verification:** ✅ Fixed (no validation errors in logs)

### Issue 3: Voice Transcription CORS
**Previous Error:** CORS blocked OpenAI Whisper API calls from browser
**Fix Applied:** Created backend proxy endpoint `/api/{user_id}/transcribe`
**Verification:** ⏳ PENDING - Test voice input

### Issue 4: Browser Cache Showing Old Code
**Issue:** Hard refresh required to see navbar/homepage changes
**Solution:** User must press Ctrl + Shift + R
**Verification:** ⏳ User needs to confirm they see "AI Chat" in navbar

---

## Deployment Readiness

### Backend Deployment (Hugging Face Spaces)
- [ ] Test all endpoints respond correctly
- [ ] Verify environment variables configured
- [ ] Check CORS allows frontend origin
- [ ] Test database connection from deployed environment

### Frontend Deployment (Vercel)
- [ ] Verify NEXT_PUBLIC_API_URL points to deployed backend
- [ ] Test authentication flow
- [ ] Verify all pages load correctly
- [ ] Check responsive design on mobile

---

## Next Steps After Testing

1. ✅ If all tests pass → Proceed with deployment
2. ❌ If tests fail → Debug issues and retest
3. 📹 Record 90-second demo video showing:
   - Homepage with AI Assistant
   - Creating task via text chat
   - Creating task via voice input (English)
   - Creating task via voice input (Urdu)
   - Listing tasks
   - Completing task

---

## Test Results Summary

**Total Tests:** 10
**Passed:** 0
**Failed:** 0
**Pending:** 10

**Blocker Issues:** None currently identified

**Ready for Demo:** ⏳ AWAITING USER TESTING
