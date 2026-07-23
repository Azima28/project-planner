# Adaptive Interview and Routing Tree

The interview is a **dynamic, context-reactive conversation**, not a static questionnaire. Do not run through a fixed list of questions. Instead, follow this 4-phase expansion loop to understand the project deeply and generate proportional features.

## Phase 1: Understand & Reflect

When the user gives their initial project description:
1. **Listen and reflect**: Summarize what you understood (domain, core problem, beneficiaries, owners).
2. **State assumptions**: "I'm assuming X and Y. Correct?"
3. **Identify the domain**: Detect the domain signal (e.g., education, commerce, operations) and read `references/domain-knowledge.md` for probing amplifiers.
4. **Ask about gaps contextually**: Do not ask generic questions. Ask specific follow-ups based on the domain and the user's description.

*Example: If the user says "exam app", don't ask "What is the closest work type?" Instead ask "Are the exams for one school or multiple? Is it just multiple choice or essays too?"*

## Phase 2: Stakeholder & Scope Mapping

Before discussing screens and features, map the landscape:
1. **Stakeholder Map**: Who pays for it? Who maintains it? Who is affected by it? Who could block it? (Don't just limit to app roles).
2. **Vision vs MVP**: What is the ultimate dream for this project? What is the Minimum Viable Product (v1) that makes it useful today?
3. **Phasing**: What must be in v1? What can definitely wait for v2?
4. **Success Criteria**: How will the user measure if this project is successful?

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
   - **Competitor features**: What do similar apps offer? (Research 2-3 reference apps).
3. **Surface/Channel Decision**: After understanding the tasks, choose the right surface (native app, web, POS, kiosk, physical procedure). Do not assume everything is a screen.
4. **Between-Role Handoffs**: Where does one role's output become another's input?

*Present the discovered features per role grouped clearly, with options to Include, Defer, or Skip.*

## Phase 4: Synthesis & Scope Lock

Before proceeding to modeling and creating artifacts:
1. **Present a Complete Feature Map**: Organize all discovered features by role with priority tags (Must/Should/Could/Won't - MoSCoW).
2. **Proactively Suggest**: Offer features the user didn't mention but are common in this domain based on your probing.
3. **Scope Lock**: Ask the user to confirm: "Is this scope complete for v1?"
4. **Record**: Create `REQ-xxx` nodes for all included and deferred features. Deferred features must have a `target_release` condition.

## Batching and Stop Condition

- Group questions logically. Do not overwhelm the user with 10+ questions at once.
- The initial batch is limited to approximately 5 top-level conceptual questions.
- If the user answers ambiguously, ask specific follow-ups. Do not assume.
- The interview loop stops when Phase 4 is confirmed by the user.

## Proportional Scaling

- **Small projects** (landing page, single script): Skip Phase 3 deep dive. Use the fast path from `references/scale-detection-guide.md`.
- **Medium projects**: Run Phase 3 dimensions 1-4.
- **Large/Complex projects**: Run the full 4-phase loop including competitor research.
