# Dynamic Artifact Manifest

For every artifact candidate, create an `artifact` node with `include` or `skip`. A `skip` must state trigger, rationale, impact, and the condition that makes it required later. An `include` artifact is only valid if the actual file, metadata envelope, hash, source IDs, and model version match.

## Proportional baseline

| Trigger | Artifacts to evaluate |
|---|---|
| All projects | brief/scope, decision-assumption register, risk-unknown register, three control reports |
| Requirement or work item | traceability view and acceptance evidence |
| External fact/gap | research ledger summary |
| User-facing work | channel decision, journey/flow, states, accessibility/error handling, usability test plan |
| Multi-role, UX/UI, physical/digital handoff | service blueprint, interaction spec, role/task and recovery map |
| Native app | permission/device/offline states and platform accessibility |
| Web/PWA | responsive, keyboard/focus, session/browser behavior |
| POS/kiosk/physical card/procedure | shift/device ownership, receipt/SOP, failure and human fallback |
| Backend/data/migration | contract, data/rollback, test strategy |
| Money/partner/offline | readiness, lifecycle/recovery/reconciliation, ownership/runbook |
| Sensitive/regulated | classification, permission, retention, threat/abuse and compliance boundary |
| Physical/event/operations | procedure, safety/contingency, staffing/ownership, field acceptance |
| Pilot/production | release gate, monitoring, incident/rollback, support handoff |
| Material change | change-impact map and regenerated-file list |
| Feature expansion completed (Phase 3-4) | feature map per role with MoSCoW priorities |
| Deferred discovery exists | deferred discovery register (unprobed roles/dimensions and associated risks) |

For visual design, evaluate `visual_design_spec` only if needed. During planning, its content is **direction and constraints** (brand character, color mood, typography style, accessibility, anti-requirements, reference apps) — not hex codes, dp values, or ASCII wireframes. Implementation details (design tokens, component styling, mockups) are the coding agent's job. See `references/delivery-surface-design.md` §"Visual design spec boundary in planning". Every local image/asset referenced in Markdown must exist and be modeled as its own artifact or clearly covered by its parent artifact, and must exist when validated.

Control reports (`planner_execution_report`, `synchronization_report`, `tree_coverage_report`) remain `include` artifacts even though their files are in `reports/`, not `deliverables/`.

There is no fixed number of documents. Choose depth from archetype, mode, capability, irreversibility, and evidence.
