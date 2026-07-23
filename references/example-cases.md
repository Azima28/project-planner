# Skill Rule Application Examples

The examples below show how the skill rules work in real situations. These are not templates — adapt to your project.

## Case 1: User requests marketplace planning

**User**: "I want to build a marketplace for buying and selling goods, Android first."

**What to do:**
1. Do not immediately determine stack/architecture. Start from outcome: what does the user want to achieve?
2. Read `interview-decision-tree.md`, ask a small batch (~5): who is the audience, solo or team, do you have design/brand?, what is the business model?, when is the target launch?
3. Record each answer as evidence. Ambiguous answers = `assumed`, not `confirmed`.
4. Read `capability-catalog.md` — a marketplace triggers: `limited_inventory`, `money_movement`, `identity_access`.
5. Read `critical-decision-gates.md` — `money_movement` triggers a gate. Display receipt: "Payment will be mock/sandbox first because of pilot mode."
6. Only after this, model and graph.

**What NOT to do:**
- Immediately say "OK, we'll use Flutter + Firebase + Midtrans" without an interview.
- Send 13 questions at once.
- Write a DB schema before planning is complete.
- Claim "Planning 100% done" before the validation report is clear.

## Case 2: User requests build before planning is complete

**User**: "Enough planning, let's just code."

**What to do (step 6b):**

> "Of 8 deliverables, 5 have files and 3 are still draft (API contract, role matrix, access policy). There is 1 research item still unverified (R-003: backend language). Do you want to complete these 3 gaps first, or continue building with them noted as open?"

If the user says "just continue":
- Record as evidence: user chose to proceed with known gaps.
- Run `implementation-artifact-generation.md` to generate scaffold from model.
- Do not ignore gaps — record in the report.

## Case 3: Design handoff — marketplace mobile app

**Correct planning output:**

```markdown
## Design Direction

### Brand Character
Trustworthy, warm, Indonesian, accessible.

### Color Mood
Warm tones. Hue coral/terracotta/amber — but DIFFERENT from
Shopee (#EE4D2D) and Tokopedia (#42B549). Neutral: clean whites.

### Typography Style
Modern geometric sans-serif. Clean, readable. Min body 14sp.

### Reference Apps (mood)
Grab (spacious), Gojek 2024 (playful), Pinterest (cards).

### Anti-Requirements
- Do not copy Shopee/Tokped
- Do not use emoji as icons
- Do not use glassmorphism/neon gradients

### Navigation
Bottom tabs for buyer (4-5), separate seller tabs.

### States
Loading: skeleton. Empty: illustration + CTA. Error: inline + retry.

### Platform
React Native Paper (MD3).
```

**WRONG planning output:**

```markdown
## Visual Design Spec

Primary:  #E53935     ← inventing hex without brand guide
Font:     Inter 14sp  ← fixing font+size without context
Spacing:  8dp/12dp    ← dp values are not the planner's job

┌─────────────┐
│ 🔔 App   🛒 │       ← ASCII wireframe is not design
├─────────────┤       ← this is misleading and dated
│ ┌──┐ ┌──┐  │
│ │  │ │  │  │
│ └──┘ └──┘  │
└─────────────┘
```

Why it's wrong: hex without basis, fixed font that will become stale, dp values not in the planner's domain, ASCII wireframe is misleading. See `references/design-handoff-contract.md` for more complete examples.

## Case 4: Design handoff — admin dashboard (web)

**Correct planning output:**

```markdown
## Design Direction — Admin Panel

### Brand Character
Professional, efficient, data-informed.

### Color Mood
Cool neutral. Dark mode default (admin uses it for hours).

### Typography Style
Monospace for data, sans-serif for labels. Dense but readable.

### Reference Apps
Vercel Dashboard (clean dark), Stripe Dashboard (organized data-dense).

### Anti-Requirements
- No dashboard full of charts without actionable items
- No mobile patterns (bottom tabs) on desktop
- No small touch targets — this is keyboard+mouse

### Navigation
Persistent sidebar (collapsible). Breadcrumbs for drill-down.

### Platform
React (Vite) + Shadcn/ui or Radix.
```

Different project, different depth. An admin dashboard does not need brand character as detailed as a consumer marketplace. Adjust proportions with `references/scale-detection-guide.md`.

## Case 5: Multi-session continuity

**Scenario**: A new agent enters session 2. The `planning/` folder already exists from the previous session.

**What to do:**
1. Read `session-continuity.md` — follow the resume checklist
2. Read `project-context.json`, `conversation-log.jsonl`, event logs, reports
3. Communicate status to the user before doing anything:

> "From the previous session: 11 decisions (9 confirmed, 2 assumed), 5/8 deliverables have files, 2 P1 open. Not yet completed: [list]. Where would you like to continue?"

4. Do not repeat interviews that were already answered
5. Do not change old decisions without a change request

## Case 6: Small project (landing page)

**User**: "Build a landing page for my new product."

**What to do (fast path):**
1. Ask 3-4 essential questions: what is the product, who is the audience, do you have a brand?
2. Immediately create a brief + design direction (1 file is enough)
3. Minimal JSON model — only evidence, instructions, decisions, artifacts
4. Skip: service blueprint, interaction spec, usability test plan — `scale-detection-guide.md` allows this for small projects
5. Deliver something useful in 1-2 responses, do not wait until the model is complete

**What NOT to do:**
- Create a 2000-line model for a landing page
- Force running the validator and 3 reports
- Ask 15 questions before producing anything
