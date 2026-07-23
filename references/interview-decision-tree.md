# Adaptive Interview and Routing Tree

Ask questions that change the next decision. Do not run a long questionnaire or require the user to understand technical jargon.

```text
Input / existing artifacts
  → restore or initialize snapshot v2
  → outcome + archetype + mode
  → capability/risk detection
  → evidence and critical-gate loop
  → proportional artifact candidates
  → graph + validation
  → next highest-risk gap, change request, or final report
```

## Initial batch (always relevant)

1. What problem should change, for whom, and how is success measured?
2. Is this for exploration, sandbox testing, limited operations, or real service?
3. What is the closest work type: software, backend/data, research, operations/event, physical, or hybrid?
4. What are the real constraints: deadline, budget, team/owner, language, location, device, connectivity, allowed channels, and accessibility?
5. Is there money, personal data, partners, regulation, offline use, safety, legacy systems, or automated decision-making involved?

Answers trigger capabilities and follow-up questions. If the user doesn't know, store as unknown and offer a safe mode/fallback. If the user says "just proceed," only proceed in reversible areas.

## Channel routing and service design

If there are direct users, multiple roles, physical processes, or design requests, ask:

1. What task must each role perform, under what conditions, and how quickly/frequently?
2. Does the role use a personal phone, browser, shared device, POS/kiosk, card/QR, or staff assistance?
3. Must one channel serve all roles? If not, which channel is safest and simplest per role?
4. What happens when device, network, identity, or stock/authorization fails; who handles recovery?
5. What proof does the user and operator receive: digital receipt, printed slip, audit log, or procedure?

Do not ask about colors, fonts, or mockups before these answers lock in the required tasks, surfaces, and states. If the user requests design "liked by many users," convert it into a hypothesis tested with a prototype and user sessions, not a planner claim.

## Batching and stop condition

- Group questions that decide one thing; high-risk gates get separate receipts.
- Initial batch is limited to **approximately 5 top-level questions** per response. This is not an absolute number — 3 complex questions can be heavier than 6 yes/no questions. The principle: do not overwhelm the user.
- If the user answers ambiguously or partially, **do not fill missing answers with assumptions**. Ask specific follow-ups.
- After each batch, paraphrase facts, assumptions, impact, and blockers for user correction.
- Do not proceed to pilot/production if critical gates are unresolved. Prototype may proceed if simulation boundaries are clear.
- Re-run routing when mode, archetype, capability, budget, owner, data, partner, or scope changes.

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
