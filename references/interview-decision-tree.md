# Adaptive Interview and Routing Tree

The interview is a **dynamic, context-reactive conversation**, not a static questionnaire. Do not run through a fixed list of questions. Instead, follow this 4-phase expansion loop to understand the project deeply and generate proportional features.

## Phase 1: Understand & Reflect

When the user gives their initial project description:
1. **Listen and reflect**: Summarize what you understood (domain, core problem, beneficiaries, owners).
2. **State assumptions**: "I'm assuming X and Y. Correct?"
3. **Identify the domain**: Detect the domain signal (e.g., education, commerce, operations) and read `references/domain-knowledge.md` for probing amplifiers.
4. **Ask about gaps contextually**: Do not ask generic questions. Ask specific follow-ups based on the domain and the user's description.
5. **Record evidence**: Every user answer must be recorded as an evidence node (`E-xxx`). Explicit statements are `confirmed`; ambiguous or partial answers are `assumed` with a follow-up question.

*Example: If the user says "exam app", don't ask "What is the closest work type?" Instead ask "Are the exams for one school or multiple? Is it just multiple choice or essays too?"*

If the user says "just proceed," only proceed in reversible areas. For irreversible decisions (payment, data, production), push back and explain the risk.

## Phase 2: Stakeholder & Scope Mapping

Before discussing screens and features, map the landscape:
1. **Stakeholder Map**: Who pays for it? Who maintains it? Who is affected by it? Who could block it? (Don't just limit to app roles).
2. **Vision vs MVP**: What is the ultimate dream for this project? What is the Minimum Viable Product (v1) that makes it useful today?
3. **Phasing**: What must be in v1? What can definitely wait for v2?
4. **Success Criteria**: How will the user measure if this project is successful?
5. **Design & Assets**: Explicitly ask who is providing the design. Does the user already have mockups/brand guidelines, or should the AI generate the design direction?

Record each answer as evidence. Ambiguous = `assumed`, explicit = `confirmed`.

## Phase 3: Role-by-Role Deep Dive

For each role identified in the scope, run a contextual exploration to discover features. Do this sequentially, not all at once.

1. **Core Journey**: Walk through the role's typical session from start to finish. "What happens before, during, and after they use the system?"
2. **7-Dimension Probing**: Generate specific features using these universal dimensions (use domain amplifiers from `references/domain-knowledge.md` to deepen them):
   - **Lifecycle phases**: What happens before, during, and after the core task?
   - **CRUD per entity**: Who creates, reads, updates, deletes each data entity?
   - **Analytics & reporting**: What data does this role need to see or export?
   - **Communication & notification**: How does this role communicate with others?
   - **Configuration & settings**: What can this role customize?
   - **Edge cases & recovery**: What goes wrong and who fixes it?
   - **Competitor features**: What do similar apps offer? Use web search to find 2-3 competitor/reference apps. Present a brief feature comparison and ask the user which competitor features they want.
3. **Surface/Channel Decision**: After understanding the tasks, choose the right surface (native app, web, POS, kiosk, physical procedure). Do not assume everything is a screen.
4. **Between-Role Handoffs**: Where does one role's output become another's input?
5. **Capability feedback**: If a discovered feature triggers a capability from `references/capability-catalog.md` (e.g., "parent portal" → `sensitive_data`), record it immediately. Do not wait until Step 3 of the main workflow.

*Present the discovered features per role grouped clearly, with options to Include, Defer, or Skip.*

Record each included/deferred feature as a requirement node (`REQ-xxx`) with acceptance criteria.

### Handling user resistance to deep dive

If the user says "enough, just build" during Phase 3:
- Record all remaining unprobed roles/dimensions as `deferred_discovery`.
- Note the risk: "Features for [Role X] were not explored — may require change requests later."
- Proceed with what is known. Do NOT silently fill gaps with assumptions.

## Phase 4: Synthesis & Scope Lock

Before proceeding to modeling and creating artifacts:
1. **Present a Complete Feature Map**: Organize all discovered features by role with priority tags (Must/Should/Could/Won't - MoSCoW).
2. **Proactively Suggest**: Offer features the user didn't mention but are common in this domain based on your probing.
3. **Scope Lock**: Ask the user to confirm: "Is this scope complete for v1?"
4. **Record**: Create `REQ-xxx` nodes for all included and deferred features. Map MoSCoW priorities to the `criticality` field (Must = `critical`, Should = `high`, Could = `medium`, Won't = `low`). Deferred features must have a `target_release` condition.

## Batching and Stop Condition

- Group questions that decide one thing; high-risk gates get separate receipts.
- The initial batch is limited to **approximately 5 top-level questions** per response. This is not an absolute number — 3 complex questions can be heavier than 6 yes/no questions. The principle: do not overwhelm the user.
- If the user answers ambiguously or partially, **do not fill missing answers with assumptions**. Ask specific follow-ups.
- After each batch, paraphrase facts, assumptions, impact, and blockers for user correction.
- The interview loop stops when Phase 4 is confirmed by the user.
- Re-run routing when mode, archetype, capability, budget, owner, data, partner, or scope changes materially.

### Good batch example

> 1. Who is the primary target user? (buyers only, or buyers + sellers?)
> 2. Working alone or with a team? If a team, how many people?
> 3. Do you already have brand identity (logo, colors, name)?
> 4. Business model: commission, subscription, or something else?
> 5. When is the target for the first release?

This is good: each question decides one thing, the user can answer quickly, and there are no hidden sub-questions.

### Bad batch example

> Some questions to determine the project direction:
>
> 1. Target users? Platform? Budget? Timeline? Team size? Skills?
> 2. Features: search? filter? payment? chat? reviews? wishlist? notifications?
> 3. Preferences: SQL/NoSQL? REST/GraphQL? Monolith/micro? CI/CD? Testing?

This is bad: 13+ sub-questions dumped at once. The user will answer partially, and the agent will fill the rest with assumptions.

### Handling ambiguous answers

**User**: "team" (without a number)

**DO NOT**: Assume "solo dev" and mark as `confirmed`.

**DO**: "How many people on the team? This affects architecture — 1-2 people take a different approach than 5+."

## Proportional Scaling

- **Small projects** (landing page, single script): Skip Phase 3 deep dive. Use the fast path from `references/scale-detection-guide.md`.
- **Medium projects**: Run Phase 3 dimensions 1-4 (lifecycle, CRUD, analytics, communication).
- **Large/Complex projects**: Run the full 4-phase loop including competitor research.
