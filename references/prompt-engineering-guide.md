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
