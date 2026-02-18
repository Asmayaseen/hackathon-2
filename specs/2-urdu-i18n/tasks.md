# Tasks: Urdu i18n (Feature Branch: 2-urdu-i18n)

**Created**: 2026-02-17
**Status**: All Complete

## T-I18N-001: Expand Locale Files [DONE]
- [x] Add ~150 new keys to en.json (dashboard, landing, history, notifications, login, settings)
- [x] Add matching Urdu translations to ur.json
- [x] Verify key parity between en.json and ur.json
- **Test**: JSON parse both files, assert same key count

## T-I18N-002: Navbar i18n [DONE]
- [x] Import useTranslation hook
- [x] Replace nav item labels with t() calls
- [x] Replace auth-related strings
- **Test**: Toggle language, verify all 8 nav strings change

## T-I18N-003: Landing Page i18n [DONE]
- [x] Import useTranslation hook
- [x] Replace 58 hardcoded strings with t() calls
- [x] Cover: hero, features, steps, CTA, footer sections
- **Test**: No hardcoded English visible when locale=ur

## T-I18N-004: Dashboard Page i18n [DONE]
- [x] Import useTranslation hook
- [x] Replace dashboard analytics strings
- [x] Cover: stats cards, priority matrix, upcoming actions
- **Test**: All 22 dashboard strings translated

## T-I18N-005: Tasks Page i18n [DONE]
- [x] Replace header, data ops, stats labels
- **Test**: Mission Control section fully translated

## T-I18N-006: Chat Page i18n [DONE]
- [x] Replace AI Assistant, New Chat, conversations
- [x] Cover: sidebar, main chat area, input section
- **Test**: All 18 chat strings translated

## T-I18N-007: History Page i18n [DONE]
- [x] Replace 7 history strings
- **Test**: Neural Logs section fully translated

## T-I18N-008: Notifications Page i18n [DONE]
- [x] Replace 13 notification strings
- [x] Cover: header, empty state, notification cards, generateMessage
- **Test**: All notification strings translated

## T-I18N-009: Settings Page i18n [DONE]
- [x] Replace 48 settings strings
- [x] Cover: all 4 tabs (General, Appearance, Notifications, Security)
- [x] Cover: password modal, sessions modal
- **Test**: Every label/button in settings translated

## T-I18N-010: ChatWidget i18n [DONE]
- [x] Replace floating chat widget strings
- **Test**: Chat widget title and placeholder translated

## T-I18N-011: ProgressBar i18n [DONE]
- [x] Replace 3 progress strings
- **Test**: Progress text translated

## T-I18N-012: TaskList i18n [DONE]
- [x] Replace 30+ TaskList strings
- [x] Cover: filters, sort options, empty states, loading states
- **Test**: All filter/sort/empty labels translated

## T-I18N-013: Login Page i18n [DONE]
- [x] Replace 7 login page strings
- **Test**: Legacy login page fully translated

## T-I18N-014: RTL CSS Rules [DONE]
- [x] Add [dir="rtl"] base text alignment
- [x] Add space-x utility reversal for RTL
- [x] Add [lang="ur"] font family (Noto Nastaliq Urdu)
- [x] Add Urdu heading line-height adjustments
- **Test**: Urdu mode shows RTL layout with proper font

## T-I18N-015: Layout RTL Fix [DONE]
- [x] Change dir="ltr" to dir="auto" in layout.tsx
- **Test**: No hydration mismatch when switching languages

## T-I18N-016: Phase-5 Locale Sync [DONE]
- [x] Copy updated en.json and ur.json to phase-5/frontend/src/locales/
- **Test**: Phase-5 locale files match phase-4
