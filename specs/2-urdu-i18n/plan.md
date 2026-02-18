# Implementation Plan: Urdu i18n (Feature Branch: 2-urdu-i18n)

**Created**: 2026-02-17
**Status**: Complete
**Feature**: Full Urdu internationalization with RTL support

## Architecture

### i18n System Design
- **Pattern**: React Context + JSON locale files
- **Provider**: `LanguageProvider` wraps entire app in `layout.tsx`
- **Hook**: `useTranslation()` returns `{ locale, setLocale, t, dir, isRTL }`
- **Key Resolution**: Dot-notation (e.g., `t('nav.tasks')`)
- **Fallback**: Current locale → English → raw key
- **Persistence**: localStorage key `app_language`
- **RTL**: `document.documentElement.dir` set dynamically

### File Structure
```
frontend/src/
├── lib/i18n.tsx          # LanguageProvider + useTranslation hook
├── locales/
│   ├── en.json           # English (~317 keys)
│   └── ur.json           # Urdu (~317 keys)
└── app/globals.css       # RTL CSS rules
```

### Key Decisions
1. **No server-side i18n routing** - all client-side via Context
2. **Single JSON per locale** - simple flat structure with dot-notation sections
3. **RTL via CSS** - `[dir="rtl"]` selectors + `[lang="ur"]` font override
4. **Urdu font stack**: Noto Nastaliq Urdu → Jameel Noori Nastaleeq → system fallback

## Components Modified

| Component | Keys Used | Section |
|-----------|-----------|---------|
| Navbar | 8 | nav.*, auth.*, common.* |
| Landing page | 58 | landing.* |
| Dashboard | 22 | dashboard.* |
| Tasks page | 30+ | tasks.* |
| Chat page | 18 | chat.* |
| History page | 7 | history.* |
| Notifications | 13 | notifications.* |
| Settings page | 48 | settings.* |
| ChatWidget | 5 | chat.* |
| ProgressBar | 3 | progress.* |
| TaskList | 30+ | tasks.* |
| Login page | 7 | login.* |
| TaskItem | (pre-existing) | tasks.* |
| TaskForm | (pre-existing) | tasks.* |
| Auth pages | (pre-existing) | auth.* |

## Verification
- [x] Toggle to Urdu in Settings
- [x] All pages render Urdu text
- [x] RTL layout applies correctly
- [x] English still works (no regressions)
- [x] Language persists across refresh
- [x] Phase-5 locale files synced
