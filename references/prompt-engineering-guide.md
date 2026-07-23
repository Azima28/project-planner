# Handoff Prompt Contract

Use only when the user requests handoff to a coding agent or executing agent. The prompt must not expand scope or raise the project mode.

```text
Context
- Project model/version: [version]
- Source IDs and affected graph nodes: [IDs]
- Archetype / operating mode: [values]
- Existing state and dependencies: [evidence-backed summary]

Task
- Implement or revise exactly: [work/delivery IDs]
- Acceptance criteria: [copied from model]
- Explicit exclusions / mock boundaries: [IDs]
- Security, privacy, operational, and rollback constraints: [IDs]

Verification
- Automated and manual checks: [test IDs]
- Expected artifacts/paths: [artifact IDs]
- Update request: report changed IDs; do not silently change decisions or dependencies.
```

Prompt granularity follows the dependency graph, not document numbers. One prompt may handle one coherent work item or a small verifiable change. If implementation discovers a conflict, the agent must open a change request instead of silently altering the plan.

## Preamble for the coding agent

Include this context block at the start of every handoff prompt so the coding agent understands the planning system:

```text
Preamble
- This project was planned using a structured planning skill. The source of truth is `planning/project-context.json`.
- READ `planning/project-context.json` FIRST before writing any code.
- Node ID conventions: E-xxx (evidence), I-xxx (instruction), D-xxx (decision), R-xxx (research), CAP-xxx (capability), REQ-xxx (requirement), W-xxx (work item), RISK-xxx (risk), ART-xxx (artifact), INT-xxx (integration).
- `operating_mode` determines what you can build: `prototype_mock` = no real integrations, `sandbox` = sandbox APIs only, `pilot` = limited real usage, `production` = full production.
- Do NOT upgrade the operating mode or add capabilities without creating a change request.
```
