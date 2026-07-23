# Validation, Synchronization, and Reconciliation Protocol

Passing must be falsifiable: not "file exists," but rules provable from model, graph, evidence, and actual files.

1. **Schema:** model v2 valid with JSON Schema; schema engine unavailable means production not ready.
2. **Graph:** IDs/edges valid, two-way trace, tree gaps must not be disguised as N/A.
3. **Policy:** every active capability has a `requires` edge and triggers appropriate candidate artifacts, gates, and tests — even when the project is still `draft`. Artifacts may be `skip` only with rationale and condition for when it becomes required.
4. **Evidence:** every `confirmed` node, waiver, production access, and release gate has valid evidence with sufficient freshness.
5. **Output:** completed `include` artifacts have path, envelope, hash, model version, matching source IDs, and all referenced local links/assets are available.
6. **Event log:** logs exist, ID/timestamp/actor/model/revision/affected IDs are valid, and active change requests have traceable receipt/impact.
7. **Adversarial:** test happy/failure/abuse/stale/concurrent/change scenarios per policy.

## Three required reports

- `planner-execution-report.json`: instruction, decision, research, evidence, policy, blocker, eligibility.
- `synchronization-report.json`: planned-but-missing, output-without-plan, stale/hash mismatch, decision violation, orphan.
- `tree-coverage-report.json`: total/covered/gap/blocked/orphan per tree; `not_applicable` only with rationale.

All three reports must be read together with `issues`, `policy_coverage`, `event_log`, and `asset_link_integrity` sections when available. `issues: []` only means the validator found no programmed violations; it is not a certificate of semantic completeness or user acceptance.

Eligibility is only `allowed` or `not_ready`. Production `allowed` requires a verified release gate and no P0, critical open nodes, stale/invalid artifacts, illegal waivers, or policy gaps.

If existing output is out of alignment, freeze as `draft_invalid`, inventory model and actual files, create a change request, update graph, regenerate all affected artifacts, then re-audit. Do not change design/Markdown alone to cover channel, role, policy, or service flow gaps.

## Planned-but-missing detection

The synchronization report MUST check: every artifact node with `disposition: include` and `lifecycle` ≠ `draft` must have a `path` pointing to an existing file. `include` artifacts that are still `draft` without a file are allowed, but the agent **must not claim planning is "complete" or "100% done"** while `include` artifacts without files still exist. Premature completeness claims violate rule #8 of SKILL.md.
