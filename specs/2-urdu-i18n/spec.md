# Feature Specification: Urdu (ur-PK) Language Support

**Feature Branch**: `2-urdu-i18n`
**Created**: 2026-02-12
**Status**: Draft
**Input**: User description: "Add Urdu (ur-PK) language support with i18n infrastructure, locale files, language toggle, and translations for Auth UI, Task actions, and Chat UI labels. Include RTL support, fallback rules, and backend language handling notes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Switch Interface to Urdu (Priority: P1)

An Urdu-speaking user opens the application and navigates to Settings. They select "اردو (Urdu)" from the language dropdown. The entire interface immediately switches to Urdu text with right-to-left layout direction. Labels, buttons, placeholders, and navigation items all display in Urdu. When the user refreshes the page or returns later, the language preference persists.

**Why this priority**: Core value proposition. Without the ability to switch and persist a language, all other i18n features are meaningless.

**Independent Test**: Can be fully tested by changing the language dropdown and verifying UI labels change. Delivers immediate value to Urdu-speaking users.

**Acceptance Scenarios**:

1. **Given** a user on the Settings page with language set to English, **When** they select "اردو (Urdu)" from the language dropdown, **Then** the interface text switches to Urdu and the page direction changes to RTL.
2. **Given** a user who previously selected Urdu, **When** they refresh the page or navigate away and return, **Then** the interface remains in Urdu.
3. **Given** a user with Urdu selected, **When** they switch back to English, **Then** the interface reverts to English with LTR layout.

---

### User Story 2 - Authenticate in Urdu (Priority: P1)

A user who has previously set their language to Urdu visits the sign-in or sign-up pages. All form labels (email, password, name), button text, error messages, and helper text appear in Urdu. The user can complete the entire authentication flow without encountering English-only text.

**Why this priority**: Authentication is the entry point. If the auth pages are not translated, users cannot even begin using the app in their language.

**Independent Test**: Can be tested by setting language to Urdu, visiting /auth/signin and /auth/signup, and verifying every visible string is in Urdu.

**Acceptance Scenarios**:

1. **Given** a user with Urdu preference stored, **When** they visit the sign-in page, **Then** all labels, placeholders, buttons, and links display in Urdu.
2. **Given** a user on the sign-up page in Urdu, **When** they submit a form with mismatched passwords, **Then** the error message appears in Urdu.
3. **Given** a user on the sign-in page in Urdu, **When** they submit invalid credentials, **Then** the error fallback message is in Urdu (server-returned errors may remain in English).

---

### User Story 3 - Manage Tasks in Urdu (Priority: P2)

A user with Urdu selected creates, edits, and deletes tasks. All task-related UI elements--form placeholders, priority labels, recurrence options, action buttons, filter labels, and status text--display in Urdu. User-generated content (task titles, descriptions) remains in whatever language the user typed.

**Why this priority**: Task management is the core functionality. Translating it ensures the primary workflow is fully accessible in Urdu.

**Independent Test**: Can be tested by creating a task, editing it, filtering the task list, and deleting a task--all while verifying UI chrome is in Urdu.

**Acceptance Scenarios**:

1. **Given** a user in Urdu mode, **When** they view the task creation form, **Then** the placeholder, priority options, recurrence options, and advanced options label appear in Urdu.
2. **Given** a user in Urdu mode editing a task, **When** they see the edit form, **Then** Cancel, Save, and placeholder text display in Urdu.
3. **Given** a user in Urdu mode, **When** they click delete on a task, **Then** the confirmation dialog text is in Urdu.
4. **Given** a user in Urdu mode, **When** they view the task list, **Then** filter buttons (All, Active, Done), sort labels, and status counters appear in Urdu.

---

### User Story 4 - Chat with AI in Urdu Interface (Priority: P2)

A user with Urdu selected opens the floating chat widget or the full chat page. The widget header, subtitle, input placeholder, and system prompts display in Urdu. The AI assistant itself already supports Urdu input/output (backend Whisper + LLM), so this story focuses on the UI chrome around the chat, not the AI responses.

**Why this priority**: Chat is a key differentiator (Phase III feature). Translating the chat interface chrome completes the multilingual experience.

**Independent Test**: Can be tested by opening the chat widget in Urdu mode and verifying header, subtitle, placeholder, and welcome message are in Urdu.

**Acceptance Scenarios**:

1. **Given** a user in Urdu mode, **When** they open the floating chat widget, **Then** the header shows "ایوولوشن ٹوڈو اے آئی" and the subtitle and placeholder are in Urdu.
2. **Given** a user in Urdu mode, **When** the chat widget loads with the initial assistant message, **Then** the welcome message is in Urdu.

---

### User Story 5 - Navigate in Urdu (Priority: P2)

A user with Urdu selected sees all navigation items (Tasks, Dashboard, AI Chat, History, Notifications, Settings) in Urdu. The brand name, logout button, and mobile menu items also display in Urdu.

**Why this priority**: Navigation is visible on every authenticated page. Incomplete navigation translation breaks the immersive experience.

**Independent Test**: Can be tested by logging in with Urdu preference and verifying all navbar items on both desktop and mobile views.

**Acceptance Scenarios**:

1. **Given** a user in Urdu mode on any authenticated page, **When** they view the navigation bar, **Then** all nav item labels display in Urdu.
2. **Given** a user in Urdu mode on mobile, **When** they open the mobile menu, **Then** menu items and logout text display in Urdu.

---

### User Story 6 - Fallback for Missing Translations (Priority: P3)

When a translation key is missing from the Urdu locale file, the system falls back to the English translation. If the English translation is also missing, the raw key string is displayed. This ensures the application never crashes or shows blank text due to missing translations.

**Why this priority**: Safety net. Without fallback rules, any missing key would break the UI.

**Independent Test**: Can be tested by temporarily removing a key from the Urdu locale file and verifying English text appears instead.

**Acceptance Scenarios**:

1. **Given** a translation key exists in English but not Urdu, **When** the user is in Urdu mode, **Then** the English text is displayed for that key.
2. **Given** a translation key exists in neither English nor Urdu, **When** the system requests that key, **Then** the raw key string (e.g., "tasks.unknownField") is displayed.
3. **Given** all required keys are present in both locale files, **When** the user is in Urdu mode, **Then** no English fallback text is visible.

---

### Edge Cases

- What happens when the browser has no localStorage (private browsing)? Language defaults to English.
- How does the system handle RTL layout for mixed-direction content (Urdu labels with English user input)? CSS `dir="rtl"` is applied at the document level; individual input fields inherit LTR for English text entry naturally.
- What happens when a user changes language mid-session while on a page with dynamic content? All rendered text updates immediately via React re-render; data fetched from the backend remains in its original language.
- What happens to backend API error messages? Server-returned error strings remain in English; only client-side fallback messages are translated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide locale files for English (en) and Urdu (ur) containing all translatable UI strings organized by domain (auth, tasks, chat, nav, settings, common).
- **FR-002**: System MUST provide a language context/provider that stores the active locale and exposes a translation function to all components.
- **FR-003**: System MUST persist the selected language in client-side storage so it survives page refreshes and new sessions.
- **FR-004**: System MUST apply RTL text direction (`dir="rtl"`) to the document when Urdu is selected and LTR when English is selected.
- **FR-005**: System MUST update the HTML `lang` attribute to match the selected locale (`en` or `ur`).
- **FR-006**: System MUST translate all Auth UI strings: sign-in page labels, sign-up page labels, form placeholders, button text, error messages, and navigation links.
- **FR-007**: System MUST translate all Task UI strings: creation form, edit form, task item actions, filter/sort labels, priority labels, recurrence options, and status counters.
- **FR-008**: System MUST translate Chat UI chrome: widget header, subtitle, input placeholder, welcome message, and error prefix.
- **FR-009**: System MUST translate Navigation bar items: all nav links, brand name, logout text, and mobile menu items.
- **FR-010**: System MUST implement a three-tier fallback chain: current locale -> English -> raw key string.
- **FR-011**: System MUST NOT alter any business logic, API contracts, data models, or backend behavior.
- **FR-012**: System MUST NOT break existing English language support; English must remain fully functional and be the default language.
- **FR-013**: System MUST sync the language preference with the backend user preferences API (language field accepts "en" or "ur").
- **FR-014**: System MUST provide a language selection control in the Settings page that immediately switches the interface language.

### Key Entities

- **Locale File**: A JSON file mapping dot-notation keys to translated strings, organized by domain (auth, tasks, chat, nav, settings, common). One file per supported language.
- **Language Preference**: A user setting stored both client-side (localStorage) and server-side (user_preferences table, language column). Valid values: "en", "ur".
- **Translation Key**: A dot-notation string (e.g., "auth.emailAddress") that maps to a localized string in a locale file.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Auth UI visible strings (labels, placeholders, buttons, error fallbacks, links) display in Urdu when Urdu is selected.
- **SC-002**: 100% of Task management UI chrome (form labels, filter buttons, sort options, action buttons, status text) displays in Urdu when Urdu is selected.
- **SC-003**: 100% of Chat widget and navigation bar UI strings display in Urdu when Urdu is selected.
- **SC-004**: Language preference persists across page refreshes with zero user intervention.
- **SC-005**: Switching between English and Urdu completes in under 1 second with no page reload required.
- **SC-006**: Zero regressions in English-language functionality: all pages render identically in English as they did before i18n was added.
- **SC-007**: Missing Urdu translations fall back to English text (never blank or broken UI).
- **SC-008**: RTL layout direction is applied correctly when Urdu is selected, with no overlapping or misaligned UI elements.

## Assumptions

- User-generated content (task titles, descriptions, chat messages) is not translated; it displays in whatever language the user typed.
- Backend API error messages (`detail` field in HTTP responses) remain in English. Only client-side fallback messages are translated.
- The existing Settings page language dropdown (already present with "en"/"ur" options) serves as the primary language toggle; no additional UI widget is needed.
- The Noto Nastaliq Urdu font or system Urdu fonts are assumed to be available on user devices; no custom font bundling is required.
- Only two languages (English and Urdu) are in scope. The architecture should support adding more languages, but only these two are implemented.

## Scope Boundaries

**In scope**:
- Frontend locale files (en.json, ur.json)
- i18n provider/hook/context infrastructure
- Translation of Auth, Tasks, Chat, Nav, and Settings UI strings
- RTL layout support
- Language persistence (localStorage + backend preferences sync)
- Fallback chain (ur -> en -> raw key)
- Backend language handling documentation

**Out of scope**:
- Translating backend API error messages
- Translating user-generated content
- Date/number formatting localization (handled by existing date-fns)
- Adding languages beyond English and Urdu
- Server-side rendering of translated content
- Translating the landing page (page.tsx) or other non-authenticated pages
