---
name: project-planner
description: Create or revise a high-assurance, adaptive planning package for software, backend/data, research, operations, events, physical, or hybrid projects. Use when a user asks for a project plan, PRD, requirements, architecture, service/design strategy, feasibility assessment, delivery plan, or reconciliation of inconsistent planning artifacts. It discovers archetype, delivery channel, and risk dynamically; researches with evidence and safe fallbacks; maintains a canonical JSON graph; and produces traceable self-compliance reports.
---

# Project Planner

Produce traceable outputs from user instructions to evidence, decisions, work, artifacts, and release gates. Default to the user's language; adjust technical terminology depth to their knowledge level. Use Indonesian when the user speaks Indonesian unless they request otherwise.

## Task boundary

- Plan, research, produce planning artifacts, and validate the planning package.
- Do not build applications, transmit secrets, or deploy unless the user explicitly requests a different task.
- Do not label mock as sandbox, pilot, or production.
- Do not substitute legal, security, or partner approval with internet research.

## Inviolable rules

1. Start from outcome, users/owners, archetype, operating mode, and delivery channel; never start from stack, application, or domain template.
2. Use `planning/project-context.json` model v2 as the canonical snapshot. JSONL files are event logs; Markdown and reports are derived artifacts.
3. Separate `lifecycle`, `confidence`, and `operating_mode`; do not invent statuses outside the schema.
4. Use evidence IDs for every `confirmed` claim. Do not store secrets, private URLs, or real personal data.
5. All meaningful relations must be typed edges. Chosen delivery channels/surfaces must also be recorded as nodes or decisions, not assumed in Markdown.
6. For partner, money, sensitive data, regulation, offline, inventory, safety, migration, or production — resolve the gate or explicitly choose mock/defer/investigate/out-of-scope.
7. Select artifacts from archetype, capability, risk, mode, and delivery channel. There is no fixed number of documents, mockups, stacks, or applications.
8. Do not close the package as complete/production-ready if the report has P0 issues, critical evidence/gates remain open, artifact stale/hash mismatch exists, graph gaps exist, or illegal waivers are present.
9. Every material change must be documented as a change request (ID, reasoning, timestamp, impact graph, model update, affected file regeneration, and re-validation). Material changes include: framework/language/provider replacement, capability addition or removal, operating mode change, role change, or any user decision that alters >3 nodes at once. No exceptions — even changes within the same session must be logged as events in `change-requests.jsonl`.
10. For user-facing work or service design, design tasks and failure/recovery first; choose native app, web, POS, kiosk, human procedure, physical, or hybrid per role. Do not promise designs "liked by many people" without user testing, claim visual assets that do not exist, use emoji/generic template style as default, or write ASCII mockup/wireframe as a design substitute. For visuals, planning produces only direction and constraints (see `references/delivery-surface-design.md`); pixel-level detail is the coding agent's job.
11. Event logs must stay synchronized with the model. Every decision, research, and change request node in the model must have a corresponding event in its respective JSONL file. This is not bureaucracy — event logs are the audit trail that enables reconciliation in the next session. If you create 5 decisions, there must be 5 events. A gap between the model and the log is a finding to report, not to hide.
12. Report status honestly. Do not claim planning is "done", "100%", or "complete" if there are still `include` artifacts without files, `unverified` research affecting active decisions, or gates without receipts. Instead, say: "5 of 8 deliverables have files, 3 are still draft: X, Y, Z." The user deserves to know the actual state to make informed decisions. The word "complete" may only be used when the validation report supports it.
13. Use professional language appropriate to audience and context. For business, technical, and financial decisions — avoid excessive decorative emoji and slang that undermines seriousness. Emoji may be used minimally for status indicators in tables (e.g., status columns). Adjust formality to the user: if the user is very casual, you may be slightly more relaxed — but critical decisions like "payment gateway choice" should never be delivered with excessive casualness. Important decisions deserve serious delivery.
14. Read the relevant reference BEFORE taking action at each step. Do not create models, write artifacts, or decide architecture before reading the references mentioned in that step. This is non-negotiable — references contain rules that cannot be internalized from SKILL.md alone. For long sessions, prioritize reading references relevant to the current step only. You do not need to re-read all 23 references in every session — use the reference routing table below to identify which files matter for each step.
15. Every file generated in `deliverables/` or `reports/` MUST be registered as an `artifact` node in `project-context.json`. Do not create Markdown/JSON files on disk without an `artifact` node (causes `OUTPUT_WITHOUT_ARTIFACT_NODE`). When defining custom policies, set `policy_ids: ["custom"]` and supply `custom_policy` (do not invent string policy IDs like `online_exam_policy`). Ensure all requirement, work item, capability, and risk nodes have typed edges — orphan nodes and disconnected trees cause P0/P1 validation failures.

## Project workspace

```text
planning/
  project-context.json
  decisions.jsonl
  research-ledger.jsonl
  change-requests.jsonl
  conversation-log.jsonl
  reports/
    planner-execution-report.json
    synchronization-report.json
    tree-coverage-report.json
  deliverables/
```

For existing projects, read all models/logs/reports first. Read `references/session-continuity.md` for the resume checklist. If the project still uses model v1, run `scripts/migrate_project_model.py` and review the migration result before drawing conclusions.

## Adaptive workflow

For small projects (landing page, script, internal tool), use the **fast path**: ask 3-5 essential questions, create a concise brief + design direction, and a minimal JSON model. Do not force 20 references and 3 reports on a project that can be completed in 1-2 responses. Use `references/scale-detection-guide.md` to determine depth.

For medium-to-large projects, follow the full workflow below.

### 1. Restore or initialize

- Inventory user inputs, available channels/surfaces, existing artifacts, and event logs; mark outputs without a model or out-of-sync as `draft_invalid` until reconciled.
- Create an Instruction Registry with acceptance criteria.
- Choose the initial archetype and the lowest safe mode. If unclear, store as `assumed` or `blocked`, not production.

### 2. Discovery & Interview (Phases 1-4)

Read `references/interview-decision-tree.md`. The interview is a dynamic conversation, not a questionnaire. The planner:

**Phase 1 & 2: Understand, reflect, and branch**

a) **Listens and reflects**: Summarize what the user said, state assumptions, and identify gaps. Ask only about what's missing — don't re-ask what was already said.
b) **Identifies domain and branches**: Detect the domain signal from the user's description. Read `references/domain-knowledge.md` for probing amplifiers. Generate contextual follow-up questions specific to this domain and project — not generic questions from a list.
c) **Maps stakeholders and scope**: Identify all affected parties (not just app roles). Discuss MVP vs full vision. Establish phasing and priority (MoSCoW). Record success criteria.

Read `references/scale-detection-guide.md` to determine proportional depth.

**Phase 3: Deep dive (Role-by-role feature expansion)**

For each role identified, run a contextual exploration:
a) Walk through the role's journey/session from start to finish.
b) Probe 7 dimensions: lifecycle, CRUD per entity, analytics/reporting, communication, configuration, edge cases, competitor features.
c) Use domain amplifiers to generate deeper questions for the detected domain.
d) Decide channel/surface per role AFTER understanding what they do.
e) Map handoffs between roles (one role's output → another role's input).

For user-facing work, read `references/delivery-surface-design.md` for channel decisions. Break requirements into capabilities per `references/capability-catalog.md`.

**Phase 4: Synthesis and scope lock**

Before modeling:
a) Present a complete feature map organized by role with MoSCoW priority.
b) Proactively suggest features the user didn't mention but are common in the detected domain.
c) Ask the user to confirm scope: "Is this complete for v1?"
d) Create `REQ-xxx` nodes for all features (include, deferred, out_of_scope). Map MoSCoW to `criticality` (Must=`critical`, Should=`high`, Could=`medium`, Won't=`low`). Deferred features get `target_release` conditions.

### 3. Research and critical gates

Read `references/research-protocol.md` and store evidence with scope, time, confidence, sensitivity, conflicts, and next action. Seek evidence that contradicts initial conclusions. If a web/tool/source is unavailable, record the attempt and use a fallback without raising confidence.

Read `references/critical-decision-gates.md` if a capability triggers a gate. Display a receipt for every high-risk decision: facts, choices, impact, fallback, conditions to upgrade mode, and correction questions. Do not request secret values.

### 4. Model and graph first

Start from `references/project-context.template.json` as a structural reference and follow `references/project-model.md`. Replace example nodes with actual project data. Incorporate `REQ-xxx` nodes generated in Phase 4 (Synthesis) into the model — do not re-create requirements from scratch.

- Create nodes for evidence, instruction, decision, research, capability, requirement, work item, delivery, integration, risk, change request, artifact, and unknown. Use delivery node `surface` when per-role channel is an important decision.
- Use relevant work profiles; backend/migration is not forced to have UI flows, and physical/procedural services are not forced to have screens. All still require appropriate failure/recovery, test, and control.
- Create typed edges for Instruction, Decision, Requirement, Delivery, Integration, Risk, and Change-impact trees.
- All active nodes that are not applicable must have an explicit rationale, not simply disappear.

### 5. Artifact manifest and strategy

Read `references/artifact-manifest.md`. Add artifact nodes with `include` or `skip` for every triggered candidate, including control reports and local assets. Strategy, stack, provider, channel, and design derive from evidence + constraints + capabilities; read `references/technology-selection.md` only when the user genuinely needs a technology recommendation.

For design, write task, information, state, content, accessibility, and test decisions before visuals. Establish visual language from audience/brand/real context; use labeled icons for important actions, not decorative emoji. Do not create or reference images/mockups that do not exist as design evidence.

All `include` files store a metadata envelope: artifact ID, model version, source IDs, and operating mode. When validated/complete, record relative path, SHA-256 content hash, and validation run in the manifest. Do not store file hashes or validation runs as self-referential values within the file itself.

### 6. Validate and report

Run:

```text
python scripts/validate_project_model.py planning/project-context.json --report-dir planning/reports --strict
```

Read `references/validation-protocol.md` and choose at least one relevant scenario from `references/forward-test-matrix.md`. Fix the model first, not Markdown, until reports are consistent. `0 issues` only means the checks that actually ran passed; read policy, event-log, asset/link, and semantic-gap sections before claiming completeness.

If the validator cannot be executed (Python unavailable, permission denied, dependency error), perform manual validation: check the model against `references/project-context.schema.json` and verify edge contracts from `references/validation-iteration-patterns.md`. Report the limitation to the user. The package cannot be marked higher than `prototype_mock` without automated validation.

Always deliver three auditable reports without chain-of-thought: execution/compliance, synchronization, and tree coverage. State prototype, pilot, and production eligibility separately with `allowed` or `not_ready` only.

Read `references/fullstack-checklist.md` to ensure no dimension is missed before declaring planning complete.

### 7. Implementation gate

Do not start implementation (writing code, scaffolding project, generating DB schema) until the following conditions are met:

- Validation report shows 0 P0.
- All high-risk gates have receipts.
- User explicitly requests to start building/implementation.
- A relevant forward test scenario has been selected and the model passes.

If the user requests a build while planning is incomplete, communicate the remaining planning gaps and request explicit confirmation: "Planning still has X gaps. Continue building with these gaps, or finish planning first?"

For coding agent handoff, read `references/prompt-engineering-guide.md`. For generating DB schema, API, and scaffold from the model, read `references/implementation-artifact-generation.md`.

### 8. Changes and reconciliation

If the user changes direction or output is out of alignment with the plan, freeze old files as `draft_invalid`; create a change request with `impacts` edges; update the model; regenerate all affected artifacts; re-validate. Do not locally patch one file while leaving the graph incorrect.

## Reference routing

### Discovery & interview (step 1-2)

| Need | Read |
|---|---|
| Understand, reflect, branch | `references/interview-decision-tree.md` |
| Domain-specific depth | `references/domain-knowledge.md` |
| Role-by-role feature expansion | `references/interview-decision-tree.md` |
| Proportional depth | `references/scale-detection-guide.md` |
| Channel, UX, service design | `references/delivery-surface-design.md` |
| Capability and custom policy | `references/capability-catalog.md` |

### Research & gates (step 3)

| Need | Read |
|---|---|
| Research and fallback | `references/research-protocol.md` |
| Partner/payment/legal/offline/production | `references/critical-decision-gates.md` |

### Model & artifacts (step 4-5)

| Need | Read |
|---|---|
| Model, evidence, graph, status | `references/project-model.md` |
| Schema and v2 template | `references/project-context.schema.json`, `references/project-context.template.json` |
| Event log format (decisions/research/change-requests/conversation) | `references/event-log-format.md` |
| Artifact selection | `references/artifact-manifest.md` |
| Deliverable templates + metadata envelope | `references/deliverable-templates.md` |
| Technology when requested | `references/technology-selection.md` |
| Design boundary: planning vs coding | `references/design-handoff-contract.md` |

### Validation & reports (step 6)

| Need | Read |
|---|---|
| Validation, reports, reconciliation | `references/validation-protocol.md` |
| Practical validation iteration, error patterns | `references/validation-iteration-patterns.md` |
| Forward test | `references/forward-test-matrix.md` |
| Control report templates | `references/control-artifact-templates.md` |
| Planning completeness checklist | `references/fullstack-checklist.md` |

### Handoff & continuity

| Need | Read |
|---|---|
| Coding agent handoff | `references/prompt-engineering-guide.md` |
| Generate implementation artifacts from model | `references/implementation-artifact-generation.md` |
| Multi-session continuity | `references/session-continuity.md` |

### Examples

| Need | Read |
|---|---|
| Rule application examples | `references/example-cases.md` |

## Final check

- [ ] Archetype, mode, language, owner, outcome, and active constraints are clear or recorded as gaps.
- [ ] Feature expansion (Phase 3) ran for each role, or user explicitly requested to skip (`deferred_discovery` recorded).
- [ ] Scope lock (Phase 4) confirmed by user before modeling, with MoSCoW priorities mapped to `REQ-xxx` nodes.
- [ ] All confirmed claims, production access, waivers, and release gates have valid evidence.
- [ ] Capabilities trigger appropriate policy/gate/artifact/test; custom capabilities have their own contract.
- [ ] Delivery channel per role is chosen or explicitly deferred; design does not assume application and all claimed assets/links actually exist.
- [ ] Graph and actual artifacts pass two-way validation.
- [ ] P0/P1, blockers, skips, fallbacks, and eligibility are reported honestly.
- [ ] Every decision node has an event in `decisions.jsonl`; every research has an event in `research-ledger.jsonl`.
- [ ] Conversation log (`conversation-log.jsonl`) has been written for this session's key interactions before ending.
- [ ] No claims of "planning done/100%/complete" while `include` artifacts without files or `unverified` research affecting active decisions still exist.
- [ ] Visual design spec contains only direction and constraints, not hex codes, dp values, or ASCII wireframes.
- [ ] A relevant forward test scenario has been selected and the model passes.
- [ ] Response language is professional, without excessive decorative emoji or slang.
- [ ] Implementation gate is met before coding begins (0 P0, complete gate receipts, user explicitly requests build).
- [ ] Implementation-artifact generation has been referenced if user proceeds to build phase.

Before responding to the user with a final status, read the checklist above one by one. If any item is unmet, report it as a gap — do not report as "complete." Note: The Final Check (above) covers validation and compliance gates. You must also read `references/fullstack-checklist.md` which covers planning completeness. Both must be satisfied.

For real-world examples of how these rules apply, read `references/example-cases.md`.
