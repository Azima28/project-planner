# Project Model v2 Contract

`planning/project-context.json` is the sole canonical snapshot. `decisions.jsonl`, `research-ledger.jsonl`, and `change-requests.jsonl` are append-only event logs: each event has an ID, timestamp, actor/source, model version before/after, project revision before/after for model v2.1+, and affected IDs. Markdown, Mermaid, and reports are derived artifacts that must not become sources of new decisions.

## Applicable form

- Validate the snapshot with `project-context.schema.json` and the validator; both must use model v2.
- Each project selects an `archetype`: `software_product`, `backend_service`, `data_ai`, `research`, `operations`, `event`, `physical`, `hybrid`, or `custom` with its own definition.
- Use `work_items`, not the assumption that all work is UI features. Choose the appropriate `work_type` and `delivery_profile`.
- For important channel decisions, use `delivery_node` with category `surface` and `surface_kind`, `roles`, and `context`. Do not conclude that user-facing means application or screen; use `service_experience`, `procedure`, `physical_output`, or `screen` per the chosen channel.
- All meaningful relationships exist in typed `edges`. Reference arrays on nodes are only supplementary metadata, not a second graph.
- Do not store literal secrets, private URLs, or real personal data. Private evidence stores only a non-secret `ref` and `sensitivity`.

## Three status dimensions

Do not mix status meanings.

| Dimension | Values | Question answered |
|---|---|---|
| `lifecycle` | `draft`, `active`, `validated`, `deferred`, `deferred_discovery`, `out_of_scope`, `superseded`, `complete`, `draft_invalid` | Is the node being worked on? |
| `confidence` | `confirmed`, `assumed`, `unverified`, `blocked`, `conflicting`, `research_incomplete` | How trustworthy is the claim? |
| `operating_mode` (project) | `prototype_mock`, `sandbox`, `pilot`, `production` | What claims/operations are allowed? |

`confirmed` requires `evidence_ids`; `blocked` requires `next_action`; `deferred` requires `target_release`; `superseded` requires a `supersedes` edge. A parent is not `complete` if a critical child is active but its confidence is not safe.

## Evidence and graph

Evidence has a kind, scope, retrieval time, confidence, sensitivity, and an optional review date. Use the following edges:

| Relation | Direction |
|---|---|
| `informs` / `decides` / `constrains` | instruction or decision → affected node |
| `implemented_by` | requirement → work item |
| `delivers` / `verified_by` | work item or risk → delivery node/test |
| `requires` | capability → integration/artifact/gate |
| `mitigated_by` | risk → control/decision/work item |
| `documented_by` | plan node → artifact |
| `impacts` / `supersedes` | change/decision → changed node |
| `evidences` | evidence → any non-evidence node |

**`evidences` vs `evidence_ids`**: Use `evidence_ids` on a node when the evidence directly supports that node's claim. Use the `evidences` edge when you need the evidence relationship to appear in graph traversals and tree coverage reports. Both mechanisms are valid; `evidence_ids` is simpler for most cases. Use `evidences` edges when audit traceability in the graph is critical (e.g., production gates, waivers).

The graph produces Instruction, Decision, Requirement, Delivery, Integration, Risk, and Change-impact trees. An empty tree may only be `not_applicable` if the archetype/capability does not trigger that tree and there is a rationale on the artifact manifest.

## Work item and requirement contract

Requirements (`REQ-xxx`) must map MoSCoW priorities to `criticality`: Must = `critical`, Should = `high`, Could = `medium`, Won't = `low`.

Every active work item has acceptance criteria and an edge from a requirement or decision. Delivery needs are determined by profile:

- `user_facing`: flow and test; add the chosen surface, then screen/procedure/physical output per that surface.
- `mobile_app` / `web_app` / `pos`: flow, screen, test; add relevant platform/device/accessibility controls.
- `service_experience`: flow, procedure or surface, test; add handoff/recovery if involving humans or different channels.
- `backend`: test; add API/data/security if relevant; UI flow is not required.
- `data`: data contract, quality test, rollback/migration if relevant.
- `research`: question/hypothesis, evidence, method, decision exit.
- `operations`/`event`/`physical`: procedure or physical output, owner, safety/contingency test if relevant.

Elements that are not applicable must be recorded in `not_applicable` with a reason, not silently removed.

## Artifact and change contract

Every artifact candidate exists as a node with `disposition: include|skip`, rationale, trigger IDs, source IDs, and model version. An `include` artifact that is `validated` or `complete` also stores a relative path, SHA-256 content hash, and validation run; the validator reads the actual file and metadata envelope. The file envelope stores `Artifact ID`, model version, source IDs, and mode. The actual hash and validation run remain in the manifest to avoid becoming self-referential values.

Active change requests must have `impacts` edges to all affected nodes. After a change: update model → regenerate affected files → recalculate hashes → run all reports. Do not modify derived artifacts directly.
