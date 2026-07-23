# Validation Iteration Patterns

Practical patterns for iterating through validator issues on `project-context.json`. Use these after running step 6 of the main SKILL.md workflow.

## The Three-Phase Fix Cycle

```
write model → validate → batch-fix → re-validate → spot-fix → done
```

Validator rarely passes on the first run for a fresh model. This is normal. Plan for 2-4 iterations.

## Strategy: Batch-fix with Python, not manual patching

Do NOT fix issues one-by-one with `patch` or manual JSON editing — there are too many, and fixing one can cascade. Instead:

1. Run validator once to see all issues
2. Write a Python script that reads `project-context.json`, applies ALL fixes, and writes back
3. Re-validate
4. If remaining issues, run a second smaller batch fix

Write the script as a temp file (`planning/_fix.py`), execute it from the planning directory, then delete it after the cycle is clean.

## Common Error Patterns & Quick Fixes

| Error Code | Cause | Fix |
|---|---|---|
| `BROKEN_EVIDENCE_REFERENCE` | `evidence_ids` references a non-existent evidence node | Add the evidence node |
| `CONFIRMED_WITHOUT_EVIDENCE` | Node is `confidence: confirmed` but has no `evidence_ids` | Add evidence or lower confidence to `assumed` |
| `INVALID_EDGE_RELATION` | Edge type doesn't match the contract (source→target) | See the contract table below |
| `POLICY_ARTIFACT_UNMODELED` | A capability's policy requires an artifact type with no node | Add `include` or `skip` artifact node |
| `DELIVERY_PROFILE_GAP` | Work item missing required delivery categories (flow, test, screen, etc.) | Add `delivers` or `verified_by` edges to matching delivery nodes |
| `WORK_WITHOUT_ORIGIN` | Work item has no incoming `implemented_by`, `constrains`, or `decides` edge | Add edge from a requirement or decision |
| `DECISION_WITHOUT_IMPACT` | Decision has no outgoing `decides`, `constrains`, or `impacts` edge | Add impact edge to a work item, requirement, or delivery node |
| `RISK_TREE_GAP` | Risk missing `mitigated_by` OR `verified_by` edge (both required for P0/P1) | Add both types of outgoing edges |
| `ORPHAN_NODE` | Active node has zero edges in or out | Connect it to the graph |
| `DEFERRED_WITHOUT_TARGET` | Lifecycle=deferred without `target_release` field | Add `target_release: "vX.Y"` |
| `DEFERRED_DISCOVERY_WITHOUT_ACTION` | Lifecycle=deferred_discovery without `next_action` | Add `next_action` describing what roles/dimensions remain unprobed |
| `EVENT_LOG_MISSING_FIELD` | JSONL event missing required fields | Each event needs `id`, `timestamp`, `actor`, `action`, `model_version_before`, `model_version_after`, `affected_ids` |
| `OUTPUT_WITHOUT_ARTIFACT_NODE` | File exists in `reports/` or `deliverables/` not claimed by any artifact | Known bootstrap issue (see below) |
| `DUPLICATE_EDGE_CONTENT` | You added an edge that semantically duplicates an existing one (same from_id, to_id, relation) | Eliminate batch-fix `ne` calculation bug: use `max(re.findall(r'EDGE-(\\d+)', ...))` not `len(edges)+1`. Remove the duplicate. |
| `ARTIFACT_METADATA_MISMATCH` | Report/deliverable artifact set to `validated` with content_hash that doesn't match the metadata envelope in the file on disk | Keep draft artifacts at `lifecycle: draft` with no `content_hash` or `validation_run`. Setting `validated` before the file has proper envelope metadata causes cascading P0s. |
| `UNTRUSTED_PRODUCTION_ACCESS` | INT-001 or other integration has `access_status: production_confirmed` but the project's `operating_mode` is `pilot` (or evidence insufficient) | Set `access_status` to `sandbox_only` or `claimed_unverified` to match actual evidence level. Only use `production_confirmed` when ALL evidence gates are complete. |

## Edge Relation Contract (Quick Reference)

The validator enforces typed edges between specific node groups. This is the contract at runtime:

| Relation | Allowed Sources (from) | Allowed Targets (to) |
|---|---|---|
| `informs` | instructions, decisions, research, evidence | requirements, decisions, capabilities, work_items, risks |
| `decides` | decisions | requirements, work_items, delivery_nodes, integrations, risks, artifacts |
| `constrains` | instructions, decisions, research, risks | requirements, work_items, delivery_nodes, integrations, artifacts |
| `implemented_by` | requirements | work_items |
| `delivers` | work_items | delivery_nodes |
| `requires` | capabilities | work_items, delivery_nodes, integrations, artifacts |
| `mitigated_by` | risks | decisions, work_items, delivery_nodes, artifacts |
| `verified_by` | requirements, work_items, risks, integrations | delivery_nodes |
| `documented_by` | instructions, decisions, requirements, work_items, risks, capabilities, change_requests | artifacts |
| `impacts` | decisions, change_requests | any node group |
| `supersedes` | any node group | any node group |
| `evidences` | evidence | any non-evidence node |

**Most common violations in practice:**
- `informs` from instructions to delivery_nodes → change target to a requirement or work_item
- `requires` from work_items to delivery_nodes → change to `delivers`
- `requires` from work_items to integrations → remove (covered by capability→integration)
- `mitigated_by` from risks to instructions → change target to a work_item or delivery_node
- `verified_by` from delivery_nodes to delivery_nodes → change source to a work_item or risk

## Known Bootstrap Issue: Auto-Generated Reports & Deliverable Files

The validator scans the workspace for existing files and flags any file in `reports/` or `deliverables/` that doesn't have a matching artifact node. This creates a persistent bootstrap problem for two file types:

### Auto-generated reports (`reports/*.json`)

The validator generates three report JSON files, then checks that they contain metadata envelopes (`Artifact ID: ART-004`, `Project Model: 2.1.0`, matching validation run). Since the validator generates these files, they can't contain the envelope BEFORE validation runs — creating a circular bootstrap.

**Approach:** Leave the report artifacts with `lifecycle: draft` and no `path`. Accept the 3+ P1 `OUTPUT_WITHOUT_ARTIFACT_NODE` warnings as expected bootstrap artifacts. When the package graduates to `validated` or `complete`, you can:
1. Run validator → captures VAL-xxx
2. Update artifacts with path, hash, and validation_run
3. Run validator again to confirm
4. The third run will surface `ARTIFACT_METADATA_MISMATCH` because auto-generated reports lack the envelope — accept this as inherent to auto-generated reports

### Manually-written deliverables (`deliverables/*.md`)

These pose a different problem: the files exist on disk and have matching artifact nodes with `path` set, but `lifecycle: draft` with no `content_hash`. The validator flags them as `OUTPUT_WITHOUT_ARTIFACT_NODE` (P1). If you set them to `lifecycle: validated` and add their SHA-256 hash, the validator then demands a matching metadata envelope inside the actual `.md` file — which doesn't exist — creating `ARTIFACT_METADATA_MISMATCH` (P0).

**Three approaches:**

| Approach | Effect | When to use |
|---|---|---|
| **Leave at `draft` + `path`** (default) | Persistent P1 `OUTPUT_WITHOUT_ARTIFACT` | During planning — P1 doesn't block `prototype` eligibility |
| **Set `validated` + add envelope** to the `.md` file | Clean both checks, but adds metadata boilerplate to every deliverable | Before production release or handoff to coding agent |
| **Remove `path` from artifact node** while files stay on disk | No P1, but artifact is incomplete | Not recommended — files become untracked |

**Recommended approach during planning:** Keep deliverable artifacts at `lifecycle: draft` with `path` set. The 5-10 P1 warnings are cosmetic and don't block prototype.

## Eligibility Semantics

| Eligibility | Meaning |
|---|---|
| `allowed` | No P0 blockers at this mode level. The model is internally consistent enough to proceed. |
| `not_ready` | Has P0 issues, critical open nodes, or policy gaps. Fix those before claiming this mode. |

A `prototype_mock: allowed` + `pilot: not_ready` + `production: not_ready` combination is NORMAL for a draft package. The critical open nodes (TBD decisions, unverified integrations) keep it from graduating — this is correct.

## Cleanup After Iteration

After the validation cycle is clean enough:
```bash
rm planning/_fix.py planning/_fix2.py  # temp scripts
rm planning/project-context.schema.json  # copied schema (lives in skill)
```

Don't leave temporary fix scripts in the project workspace.

## Edge Relation Gotchas (Runtime Validation)

The schema allows many relations, but the validator rejects specific combinations that look intuitive but fail:

| Pattern | Looks Correct | Validator Says | Fix |
|---|---|---|---|
| Risk → Decision informing | `risk -> decision (informs)` | `INVALID_EDGE_RELATION` — `informs` from risk to decision violates the contract | Use `risk -> decision (mitigated_by)` — the risk is mitigated by the decision |
| Risk → Unknown cross-linking | `risk -> unknown (informs)` | `INVALID_EDGE_RELATION` — risk to unknown not allowed | Remove the edge. Link risk to a decision or work_item instead |
| Requirement → Work Item constraining | `requirement -> work_item (constrains)` | `INVALID_EDGE_RELATION` — `constrains` from requirement to work_item rejected | Use `requirement -> work_item (implemented_by)` |
| Requirement → Work Item informing | `requirement -> work_item (informs)` | `INVALID_EDGE_RELATION` — `informs` from requirement to work_item also rejected | Same fix — `implemented_by` is the only valid requirement→work_item relation |
| Decision → Work Item informing | `decision -> work_item (informs)` | `WORK_WITHOUT_ORIGIN` — `informs` doesn't count as a valid origin | Use `decision -> work_item (decides)` or `(constrains)` |

**Rule of thumb:** Only `implemented_by` goes from requirement to work_item. Only `decides` or `constrains` goes from decision to work_item. `informs` is for instructions/evidence/research → requirements or decisions, not into work_items directly.

### Batch-adding delivery nodes: the orphan trap

When you batch-fix `DELIVERY_PROFILE_GAP` by adding delivery nodes (SCREEN-XXX, FLOW-XXX, PROC-XXX), every new node needs an incoming `delivers` edge from a work item — otherwise the next validation run flags them as `ORPHAN_NODE`.

```python
# Pattern: batch-fix that avoids orphans
# 1. Add delivery nodes
model["delivery_nodes"].extend([
    {"id": "SCREEN-004", "title": "...", "category": "screen", ...},
    {"id": "FLOW-006", "title": "...", "category": "flow", ...},
])

# 2. Add edges for each one in the SAME script
new_edges = []
ne = max_id + 1
for screen_id in ["SCREEN-004", "SCREEN-005"]:
    new_edges.append({"id": f"EDGE-{ne:03d}", "from_id": "W-010", "to_id": screen_id, "relation": "delivers", ...})
    ne += 1
model["edges"].extend(new_edges)
```

Forgetting to connect a SCREEN, FLOW, or PROC node in the same batch is the most common cause of residual P1 orphans after a round of delivery-profile fixes.

## Event Log Format (JSONL)

Each JSONL file has specific required fields. The validator checks `action` in every event entry.

### `decisions.jsonl` — Required fields

| Field | Required | Typical Value |
|---|---|---|
| `id` | yes | `EVT-D-001` |
| `timestamp` | yes | ISO 8601 |
| `actor` | yes | `user` or `planner` |
| `action` | yes | `decide` (for decisions), `assume` (for planner assumptions) |
| `event_type` | yes | `decision_made`, `decision_assumed` |
| `model_version_before` | yes | e.g., `2.1.0` |
| `model_version_after` | yes | e.g., `2.1.0` |
| `project_revision_before` | yes | Integer |
| `project_revision_after` | yes | Integer (increment per batch) |
| `affected_ids` | yes | Array of node IDs touched |
| `summary` | yes | Human-readable description |

### `research-ledger.jsonl` — Required fields

Same shape as decisions, but:
- `action` → `identify` (for new research), `resolve` (when completed), `update`
- `event_type` → `research_identified`, `research_resolved`

### `change-requests.jsonl` — Required fields

- `action` → `create`, `apply`, `reject`

### Common pitfall: missing `action`

The most common JSONL validation error is `EVENT_LOG_MISSING_FIELD` because the `action` field was omitted. Every single event entry — even the first one — must have it. The validator does NOT infer a default.

```json
// WRONG — will fail with EVENT_LOG_MISSING_FIELD
{"id": "EVT-D-001", "timestamp": "...", "actor": "user", "event_type": "decision_made", ...}

// RIGHT
{"id": "EVT-D-001", "timestamp": "...", "actor": "user", "action": "decide", "event_type": "decision_made", ...}
```

---

## Supersede Pattern (Work Items & Decisions)

When a work item, decision, or requirement is superseded by a newer one, the validator checks BOTH of these must exist:

1. A **supersedes edge** FROM the **old** node TO the **new** node
2. A **`superseded_by` field** on the old node pointing to the new node's ID

### Example

```json
// Old work item (add superseded_by field)
{"id": "W-005", "title": "Old Dashboard", "lifecycle": "active", 
 "confidence": "assumed", ..., "superseded_by": "W-010"}

// Edge: old -> new with supersedes
{"id": "EDGE-116", "from_id": "W-005", "to_id": "W-010", 
 "relation": "supersedes", "lifecycle": "active", "confidence": "confirmed"}
```

**Common mistake:** Adding the edge in the wrong direction. The `supersedes` relation goes FROM the **old/superseded** node TO the **new/superseding** node. Think: "W-005 is superseded by W-010" → edge `W-005 -> W-010` with `relation: supersedes`.

**Validator error if missing either:**
- `SUPERSEDED_WITHOUT_TARGET` — no `superseded_by` field on the old node
- `SUPERSEDED_WITHOUT_EDGE` — no `supersedes` edge from old to new node

---

## Production Mode Artifact Completeness

When `project.operating_mode` is set to `production`, the validator becomes significantly stricter about artifacts:

| Check | Pilot/Prototype | Production |
|---|---|---|
| Draft artifacts with no path/hash | ✅ Allowed | ❌ `INCOMPLETE_INCLUDED_ARTIFACT` on every `include` artifact |
| Validated artifacts with content_hash | ✅ Nice-to-have | ✅ **Required** for every `include` artifact |
| Metadata envelope in actual files | ⏳ Optional | ✅ **Required** — the file on disk must contain matching `Artifact ID`, `Model Version` |
| Output file without artifact node | ⚠️ P1 warning | ❌ P0 `OUTPUT_WITHOUT_ARTIFACT_NODE` |
| Policy artifact unmodeled | ❌ P0 always | ❌ P0 always |

### Practical guidance

**Do NOT flip to production mode during the planning phase.** Keep it at `pilot` until:
- All `include` artifacts have actual written files
- Those files have the correct metadata envelope inside them
- All content hashes are computed from the actual files
- The validation report matches cleanly

The production gate (operational owner, monitoring, rollback, incident route) is a necessary but NOT sufficient condition. Even with the gate resolved, all artifacts must be fully validated.

The pattern: **resolve gates during planning → keep mode at pilot → build artifacts → validate at pilot → flip to production and re-validate** after all artifacts are materially complete.

---

## Edge ID Numbering in Batch-Fix Scripts

When using the batch-fix Python script pattern, edge numbering collisions are the most common scripting mistake:

```python
# WRONG — counts edges that will be removed:
ne = len(model["edges"]) + 1  # BUG: includes edges you'll delete

# RIGHT — find the actual max:
import re
max_num = max(int(re.search(r'(\d+)', e["id"]).group(1)) for e in model["edges"])
ne = max_num + 1
```

If you use `len()` and also remove edges, the new IDs collide with remaining old IDs, producing `DUPLICATE_ID` P0 errors on the next validation run.

**Pattern:** Always `len(model["edges"])` first, print the max ID, then compute `ne` from the max. Do the same for artifact IDs if adding them dynamically.

