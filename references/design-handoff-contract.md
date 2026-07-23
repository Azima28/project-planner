# Design Handoff Contract

Use this reference when planning is complete and the coding agent will implement UI. This is not a rigid checklist — adjust depth to the project. A simple landing page does not need a 9-item handoff; a multi-role marketplace needs more.

## Division principle

The planner determines **why** and **for whom**. The coding agent determines **how it looks and feels**.

This boundary is not absolute. If the user already has a brand guide with hex codes, the planner may certainly record them. If the project is very small and the planner is also the coder, this boundary can be more flexible. But the default is: planning provides direction, coding agent provides implementation.

## What the planner provides

Adjust depth to project scale:

| Dimension | Content | When to skip |
|-----------|---------|--------------|
| Brand character | 2-4 adjectives from audience/context, not generic "modern premium" | Internal project without brand |
| Color mood | Color direction (warm/cool, light/dark), hue family, differentiation from competitors | Backend-only project |
| Typography style | Typography direction (geometric/humanist/serif), not specific font + size | Backend-only project |
| Accessibility | Minimum constraints: contrast ratio, touch target, minimum font | Never skip for user-facing |
| Platform direction | Component library to use (Material 3, HIG, custom) | Never skip for user-facing |
| Anti-requirements | Things to avoid, from competitor analysis and audience | Can be brief for small projects |
| Reference apps | 2-3 apps with similar mood to target, not to copy | Can skip for internal projects |
| Navigation model | Tab/drawer/stack — this is an architectural decision | Never skip for mobile app |
| State requirements | Loading/empty/error/success must exist | Never skip |
| Asset strategy | Photo vs illustration, placeholder approach | Can skip for MVP |

## What the coding agent produces

From the direction above, the coding agent builds:

- Color tokens (primary, secondary, neutral, semantic — scale as needed)
- Typography tokens (font family, scale, weights, line heights)
- Spacing tokens (consistent grid system)
- Component library (buttons, inputs, cards, navigation)
- Motion/animation tokens (if needed)
- Dark mode (if requested)
- Responsive behavior (if multi-platform)

## When the planner may be more specific

This boundary is not a rigid law. The planner may be more detailed if:

- User/client already has a brand guide with specific colors and fonts → record as-is
- User explicitly requests specific colors or styles → record as instruction
- Project is very small and planner = coder → boundary is not relevant, but still start from direction

What remains prohibited: **creating design independently** (hex codes, dp values, ASCII wireframes) without basis from user/brand guide, then presenting it as if it were a professional design decision.

---

## Case Example: Marketplace Mobile App

### Planning Output (CORRECT)

```markdown
## Design Direction — Marketplace

### Brand Character
Trustworthy, warm, Indonesian, accessible.

### Color Mood
Warm tones. Reddish hue is fine but DIFFERENT from Shopee (#EE4D2D)
and Tokopedia (#42B549). Neutral: clean whites and grays.

### Typography Style
Modern geometric sans-serif. Clean, readable, not rigid.
Minimum body 14sp.

### Reference Apps (mood, not copy)
- Grab: spacious, modern
- Gojek 2024: playful but organized
- Pinterest: satisfying card browsing

### Anti-Requirements
- Do not copy Shopee/Tokped — must have its own identity
- Do not use emoji as icons — use consistent icon library
- Do not use glassmorphism or neon gradients

### Navigation
Bottom tabs for buyer (4-5 max), separate bottom tabs for seller.
Stack navigation for detail screens.

### States (required)
Loading: skeleton shimmer. Empty: illustration + CTA.
Error: inline + retry. Success: confirmation + next action.

### Platform
React Native Paper (Material Design 3) as base.
```

### Planning Output (WRONG — do not do this)

```markdown
## Visual Design Spec

Primary:     #E53935  (Red-600)     ← do not specify hex
Accent:      #FFB300  (Amber)       ← do not specify hex
Font:        Inter 14sp Regular     ← do not specify font+size
Spacing:     sm=8dp, md=12dp        ← do not specify dp values
Radius:      md=8dp                 ← do not specify radius

┌──────────────────────────────────┐
│ 🔔 Marketplace Kita          🛒 │  ← do not use ASCII wireframe
├──────────────────────────────────┤  ← this is not design
│ ┌───┐ ┌───┐ ┌───┐              │  ← this is misleading
│ │EL │ │FT │ │MK │              │
│ └───┘ └───┘ └───┘              │
└──────────────────────────────────┘
```

**Why the second one is wrong:**
1. Hex codes without brand guide basis → just copied Material palette
2. Fixed font+size → becomes stale once coding agent picks a different library
3. dp values → not the planner's responsibility, this spreads accountability
4. ASCII wireframe → not a visual representation, misleading, and looks dated
5. Emoji as icons → violated by the skill's own rules

---

## Case Example: Admin Dashboard (Web)

### Planning Output (CORRECT)

```markdown
## Design Direction — Admin Panel

### Brand Character
Professional, efficient, data-informed.

### Color Mood
Cool neutral. Dark mode as default (admin uses the panel
for hours, dark mode reduces eye strain).

### Typography Style
Monospace for data/numbers, sans-serif for labels and navigation.

### Reference Apps
- Vercel Dashboard: clean, dark, minimal
- Stripe Dashboard: data-dense but organized

### Anti-Requirements
- Do not build a dashboard full of charts without actionable items
- Do not use mobile patterns (bottom tabs, gesture nav) on desktop
- Do not use small touch targets — this is a keyboard+mouse interface

### Navigation
Persistent sidebar (collapsible). Breadcrumbs for drill-down.

### States
Loading: skeleton or per-section spinner.
Empty: "No data yet" + CTA.
Error: toast/alert + retry.

### Platform
React (Vite) + Shadcn/ui or Radix as base.
```

---

## Case Example: Simple Landing Page

### Planning Output (CORRECT — minimal, proportional)

```markdown
## Design Direction — Product Landing Page

### Brand Character
Playful, young, tech-savvy.

### Color Mood
Vibrant, gradient-friendly. Dark background + bright accents.

### Reference Apps
- Linear.app: clean dark landing
- Raycast.com: gradient + modern feel

### Anti-Requirements
- No generic stock photos
- No wall of text without visual breaks

### Platform
Static HTML/CSS or Astro. No complex framework needed.
```

For a project this small, the planner does not need to specify navigation architecture, state management, or asset strategy in detail — direction and anti-requirements are sufficient.
