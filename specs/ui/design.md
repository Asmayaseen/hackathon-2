# UI Design Specification - Evolution Todo (Phase II)

## Overview
This specification defines the exact UI design for the Evolution Todo web application, matching the reference implementation at https://evolution-todo.vercel.app/

## Design System

### Color Palette

#### Primary Colors
- **Purple Primary**: `#8B5CF6` (purple-500)
- **Blue Secondary**: `#3B82F6` (blue-500)
- **Gradient**: `linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)`

#### Theme Colors

**Light Theme:**
- Background: `#FFFFFF`
- Surface: `#F9FAFB` (gray-50)
- Card Background: `rgba(255, 255, 255, 0.7)` with backdrop-blur
- Text Primary: `#111827` (gray-900)
- Text Secondary: `#6B7280` (gray-500)
- Border: `#E5E7EB` (gray-200)

**Dark Theme:**
- Background: `#0F172A` (slate-900)
- Surface: `#1E293B` (slate-800)
- Card Background: `rgba(30, 41, 59, 0.7)` with backdrop-blur
- Text Primary: `#F8FAFC` (slate-50)
- Text Secondary: `#94A3B8` (slate-400)
- Border: `#334155` (slate-700)

#### Status Colors
- **Complete**: `#10B981` (green-500)
- **Pending**: `#F59E0B` (amber-500)
- **Overdue**: `#EF4444` (red-500)

### Typography

#### Font Family
- Primary: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Monospace: `'JetBrains Mono', 'Fira Code', monospace` (for code/IDs)

#### Font Scales
- **Heading 1**: 2.5rem (40px), font-weight: 700, line-height: 1.2
- **Heading 2**: 2rem (32px), font-weight: 600, line-height: 1.3
- **Heading 3**: 1.5rem (24px), font-weight: 600, line-height: 1.4
- **Body**: 1rem (16px), font-weight: 400, line-height: 1.5
- **Small**: 0.875rem (14px), font-weight: 400, line-height: 1.4
- **Caption**: 0.75rem (12px), font-weight: 500, line-height: 1.3

## Layout Structure

### Main Layout
```
┌─────────────────────────────────────────────────────┐
│  Header (fixed, backdrop-blur)                       │
│  ┌──────────┐  Logo  │  Theme Toggle │  User Menu   │
└─────────────────────────────────────────────────────┘
┌──────────┐ ┌─────────────────────────────────────┐
│          │ │                                       │
│ Sidebar  │ │  Main Content Area                   │
│          │ │                                       │
│ - All    │ │  ┌─────────────────────────────┐    │
│ - Active │ │  │  Task Form (Glassmorphism)  │    │
│ - Done   │ │  └─────────────────────────────┘    │
│          │ │                                       │
│ + Add    │ │  ┌───────┐ ┌───────┐ ┌───────┐     │
│          │ │  │ Card  │ │ Card  │ │ Card  │     │
│          │ │  └───────┘ └───────┘ └───────┘     │
└──────────┘ └─────────────────────────────────────┘
```

### Responsive Breakpoints
- **Mobile**: < 640px (1 column, sidebar drawer)
- **Tablet**: 640px - 1024px (1-2 columns, collapsible sidebar)
- **Desktop**: > 1024px (2-3 columns, persistent sidebar)

## Component Specifications

### 1. Header Component

**Structure:**
- Fixed position with backdrop-blur-md
- Height: 64px
- Horizontal padding: 24px
- Glassmorphism effect: `bg-white/70 dark:bg-slate-900/70`

**Elements:**
- Logo (left): Brand name with gradient text
- Theme Toggle (right): Sun/Moon icon with smooth transition
- User Menu (right): Avatar with dropdown

**Styling:**
```css
.header {
  position: fixed;
  top: 0;
  width: 100%;
  height: 64px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,0.1);
  z-index: 50;
}
```

### 2. Sidebar Component

**Structure:**
- Width: 280px (desktop), full-width drawer (mobile)
- Background: Glassmorphism card
- Padding: 24px
- Border-radius: 16px (desktop)

**Navigation Items:**
- All Tasks (default)
- Active Tasks
- Completed Tasks
- Divider
- Add New Task (primary action)

**Styling:**
```css
.sidebar-nav-item {
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.sidebar-nav-item:hover {
  transform: translateX(4px);
  background: rgba(139, 92, 246, 0.1);
}

.sidebar-nav-item.active {
  background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}
```

### 3. Task Form Component

**Structure:**
- Glassmorphism card with prominent placement
- Border-radius: 16px
- Padding: 32px
- Backdrop-blur-md
- Subtle gradient border

**Form Fields:**
1. **Title Input**
   - Floating label
   - Border: 2px solid transparent
   - Focus: gradient border
   - Height: 48px
   - Border-radius: 8px

2. **Description Textarea**
   - Floating label
   - Min-height: 120px
   - Auto-resize
   - Border-radius: 8px

3. **Submit Button**
   - Gradient background (#8B5CF6 → #3B82F6)
   - Height: 48px
   - Border-radius: 8px
   - Font-weight: 600
   - Hover: scale-105
   - Active: scale-95
   - Shadow: 0 8px 24px rgba(139, 92, 246, 0.5)

**Styling:**
```css
.task-form-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.dark .task-form-card {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.gradient-button {
  background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.gradient-button:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.5);
}

.gradient-button:active {
  transform: scale(0.95);
}
```

### 4. Task Card Component

**Structure:**
- Glassmorphism card
- Border-radius: 12px
- Padding: 20px
- Hover elevation effect
- Status indicator (left border or badge)

**Elements:**
1. **Status Badge** (top-right)
   - Pending: Amber
   - Complete: Green with checkmark
   - Pill-shaped, padding: 4px 12px

2. **Title** (H3)
   - Font-size: 1.125rem
   - Font-weight: 600
   - Margin-bottom: 8px

3. **Description** (if present)
   - Font-size: 0.875rem
   - Color: text-secondary
   - Line-clamp: 2 (ellipsis after 2 lines)

4. **Action Buttons** (bottom)
   - Complete/Uncomplete toggle
   - Edit icon button
   - Delete icon button
   - Horizontal layout with gap

**Styling:**
```css
.task-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.task-card:hover {
  transform: scale(1.02);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  border-color: rgba(139, 92, 246, 0.3);
}

.dark .task-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark .task-card:hover {
  border-color: rgba(139, 92, 246, 0.5);
}

.task-card-complete {
  opacity: 0.7;
}

.task-card-complete .task-title {
  text-decoration: line-through;
  color: var(--text-secondary);
}
```

### 5. Status Badge Component

**Variants:**
1. **Pending**
   - Background: `rgba(245, 158, 11, 0.1)`
   - Color: `#F59E0B`
   - Border: `1px solid rgba(245, 158, 11, 0.2)`

2. **Complete**
   - Background: `rgba(16, 185, 129, 0.1)`
   - Color: `#10B981`
   - Border: `1px solid rgba(16, 185, 129, 0.2)`
   - Icon: Checkmark

**Styling:**
```css
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.025em;
}
```

### 6. Theme Toggle Component

**Structure:**
- Circular button (40px × 40px)
- Background: glassmorphism
- Icon: Sun (light mode) / Moon (dark mode)
- Smooth rotation transition

**Styling:**
```css
.theme-toggle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  transform: rotate(180deg);
  background: rgba(139, 92, 246, 0.2);
}

.theme-toggle svg {
  transition: opacity 0.3s ease;
}
```

## Animation Specifications

### Transitions
- **Default Duration**: 200ms
- **Easing**: cubic-bezier(0.4, 0, 0.2, 1)
- **Hover Scale**: scale(1.02) - scale(1.05)
- **Active Scale**: scale(0.95)

### Entrance Animations
- **Task Cards**: Fade-in + slide-up (stagger 50ms)
- **Forms**: Fade-in + scale (0.95 → 1)
- **Modals**: Fade-in + scale (0.9 → 1) with backdrop blur

### Micro-Interactions
- **Button Ripple**: Radial gradient expanding from click point
- **Checkbox**: Checkmark draw animation (300ms)
- **Theme Toggle**: Icon cross-fade + rotation
- **Sidebar**: Slide-in from left (mobile)

## Effects & Visual Enhancements

### Glassmorphism
```css
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .glass {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Gradient Overlays
- **Primary Gradient**: `linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)`
- **Background Accent**: Subtle radial gradient in corners
  ```css
  .bg-accent {
    background: radial-gradient(
      circle at top right,
      rgba(139, 92, 246, 0.05) 0%,
      transparent 50%
    );
  }
  ```

### Shadows
- **Card Shadow**: `0 8px 32px rgba(0, 0, 0, 0.1)`
- **Hover Shadow**: `0 12px 40px rgba(0, 0, 0, 0.15)`
- **Button Shadow**: `0 8px 24px rgba(139, 92, 246, 0.5)`
- **Floating Shadow**: `0 20px 60px rgba(0, 0, 0, 0.3)`

## Responsive Design

### Mobile (< 640px)
- Sidebar: Full-screen drawer overlay
- Task cards: Single column, full width
- Form: Reduced padding (16px)
- Header: Compact with hamburger menu

### Tablet (640px - 1024px)
- Sidebar: Collapsible, 240px width
- Task cards: 1-2 columns grid
- Form: Moderate padding (24px)

### Desktop (> 1024px)
- Sidebar: Persistent, 280px width
- Task cards: 2-3 columns grid
- Form: Full padding (32px)
- Hover effects enabled

## Accessibility

### Color Contrast
- All text must meet WCAG AA standards (4.5:1 for normal text)
- Status indicators must have text labels, not just colors

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Focus indicators: 2px solid purple outline with offset
- Tab order: logical flow (header → sidebar → main content)

### Screen Readers
- Proper ARIA labels on all icons and controls
- Status announcements for task updates
- Landmark regions: header, nav, main, complementary

### Focus States
```css
*:focus-visible {
  outline: 2px solid #8B5CF6;
  outline-offset: 2px;
  border-radius: inherit;
}
```

## Implementation Notes

### Technology Stack
- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS 4.x
- **Components**: shadcn/ui
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Theme**: next-themes

### Key Libraries
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "tailwindcss": "^4.0.0",
    "@radix-ui/react-*": "latest",
    "lucide-react": "latest",
    "framer-motion": "latest",
    "next-themes": "latest"
  }
}
```

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        purple: {
          primary: '#8B5CF6',
        },
        blue: {
          secondary: '#3B82F6',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

## Design Checklist

- [ ] Dark/Light theme toggle functional
- [ ] Purple gradient buttons (#8B5CF6 → #3B82F6)
- [ ] Glassmorphism cards with backdrop-blur-md
- [ ] Hover animations (scale-105 on cards)
- [ ] Responsive grid (sm:grid-cols-2, lg:grid-cols-3)
- [ ] shadcn/ui components integrated
- [ ] Sidebar navigation with active states
- [ ] Smooth transitions (200ms default)
- [ ] Focus indicators for accessibility
- [ ] Mobile-responsive drawer sidebar
- [ ] Gradient overlay background accents
- [ ] Status badges with proper colors
- [ ] Floating labels on form inputs
- [ ] Icon buttons with hover effects
- [ ] Loading states and skeletons

## References

- **Live Reference**: https://evolution-todo.vercel.app/
- **Design System**: Based on Tailwind CSS default palette
- **Component Library**: shadcn/ui
- **Accessibility**: WCAG 2.1 AA compliance
