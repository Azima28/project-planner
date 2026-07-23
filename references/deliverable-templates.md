# Derived Artifact Templates

Use only the template whose manifest is `include`. All sections derive from the graph model; remove irrelevant sections only after the artifact node `skip` has a rationale.

## Metadata envelope

```markdown
> Artifact ID: `[artifact_id]`
> Project Model: `[model_version]`
> Source IDs: `[source_ids]`
> Archetype / Mode: `[archetype]` / `[operating_mode]`
> Lifecycle / Confidence: `[lifecycle]` / `[confidence]`
```

Do not place the SHA-256 file hash or validation run inside the file whose hash is being computed; both are recorded on the artifact manifest and control report. The validator matches `Artifact ID`, version, source IDs, mode, and actual hash.

> **REQUIRED**: Every deliverable file in `deliverables/` MUST begin with this metadata envelope. The validator will check for the presence of `Artifact ID`, `Project Model`, and `Source IDs`. Files without an envelope cannot be set to `validated`.

## Brief / Scope

```markdown
# [Project name]

## Outcome and boundary
- Outcome: [measurable change]
- Owner / audience: [who]
- Archetype and mode: [values]
- In / out / deferred: [IDs and rationale]

## Evidence, decisions, and unknowns
| ID | Claim or decision | Confidence | Evidence | Next action / release condition |
|---|---|---|---|---|

## Work and acceptance
| Work ID | Type/profile | Requirement/decision origin | Acceptance | Mode |
|---|---|---|---|---|
```

## Feature Map (Per Role)

```markdown
# Feature Map

## [Role Name 1] (e.g. Buyer, Admin)
- Description / Core Journey: [brief context]
- Channel/Surface: [e.g. Mobile App, Web Panel]

| ID | Feature / Requirement | Dimension | Priority (MoSCoW) | Status |
|---|---|---|---|---|
| REQ-xxx | [Feature name] | [Lifecycle/CRUD/etc] | [Must/Should/Could/Won't] | [Include/Deferred] |

## [Role Name 2]
...
```

## Traceability View

```markdown
| Instruction | Decision | Requirement | Work item | Delivery / test | Artifact |
|---|---|---|---|---|---|
| [IDs from typed edges] | | | | | |
```

## Policy / Operational Artifact

Use this structure for integration readiness, financial lifecycle, migration, data governance, event procedure, or safety plan.

```markdown
## Trigger and boundary
[capability/archetype IDs and what is explicitly excluded]

## States, owners, failures, and fallback
| State / event | Owner | Failure / abuse | Fallback / recovery | Evidence / test |
|---|---|---|---|---|

## Release conditions
[gate IDs, owner, evidence, expiry/review date]
```

## Three Control Reports

```markdown
## Planner Execution and Compliance
| Instruction / policy | Status | Evidence or gap | Action |
|---|---|---|---|

## Synchronization
| Check | Pass / gap | IDs / files | Corrective action |
|---|---|---|---|

## Tree Coverage
| Tree | Covered | Gap | Blocked | Orphan | N/A rationale |
|---|---:|---:|---:|---:|---|
```
