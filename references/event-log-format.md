# Event Log Format Reference (Model v2.1)

Each event in a `.jsonl` file is a **single-line JSON object**. Every event requires these core fields; additional fields depend on the log type.

## Core Fields (all event types)

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ | `EVT-{X}-{NNN}` — X = D (decision), R (research), CR (change), C (conversation) |
| `timestamp` | string | ✅ | ISO 8601 datetime |
| `actor` | string | ✅ | `"user"` or `"agent"` |
| `model_version_before` | string | ✅ | Version before this event (`""` for initial session) |
| `model_version_after` | string | ✅ | Version after this event |
| `project_revision_before` | int | ✅ | Revision before this event (0 for initial) |
| `project_revision_after` | int | ✅ | Revision after this event |
| `type` | string | ✅ | One of: `decision`, `research`, `change_request`, `conversation` |

---

## 1. Decisions (`decisions.jsonl`)

### Required additional fields

| Field | Type | Description |
|---|---|---|
| `decision_id` | string | Matching node ID in model (e.g. `D-001`) |
| `topic` | string | Short label |
| `value` | string | The decision made |
| `rationale` | string | Why this decision |
| `affected_ids` | array | Node IDs affected by this decision |

### Examples

```json
{"id":"EVT-D-001","timestamp":"2026-07-23T00:00:00Z","actor":"user","model_version_before":"","model_version_after":"2.1.0","project_revision_before":0,"project_revision_after":1,"type":"decision","decision_id":"D-001","topic":"delivery_channel","value":"all_web","rationale":"User request: semua web, siswa responsive, guru/admin desktop","affected_ids":["SURFACE-SISWA","SURFACE-GURU","SURFACE-ADMIN"]}

{"id":"EVT-D-002","timestamp":"2026-07-23T00:00:00Z","actor":"agent","model_version_before":"2.1.0","model_version_after":"2.1.0","project_revision_before":1,"project_revision_after":1,"type":"decision","decision_id":"D-004","topic":"frontend_stack","value":"Next.js (React) dengan route grouping","rationale":"Recommended: satu codebase, responsive mobile-first, shadcn/ui untuk admin dashboard","affected_ids":["SURFACE-SISWA","SURFACE-GURU","SURFACE-ADMIN"]}
```

### Rules
- Every `D-xxx` node in the model **must** have a corresponding event.
- `project_revision` only increments when the model file actually changes (revision bump).
- Within the same session, multiple events can share the same revision numbers if the model file hasn't been re-written yet.

---

## 2. Research (`research-ledger.jsonl`)

### Required additional fields

| Field | Type | Description |
|---|---|---|
| `research_id` | string | Matching node ID (e.g. `R-001`) |
| `claim` | string | The research claim |
| `confidence` | string | `confirmed`, `assumed`, `unverified`, etc. |
| `method` | string | How it was investigated |
| `finding` | string | What was learned |
| `evidence_ids` | array | Supporting evidence IDs |
| `next_action` | string | What to do next |

### Examples

```json
{"id":"EVT-R-001","timestamp":"2026-07-23T00:00:00Z","actor":"agent","model_version_before":"2.1.0","model_version_after":"2.1.0","project_revision_before":1,"project_revision_after":1,"type":"research","research_id":"R-001","claim":"Visibility API cukup untuk deteksi keluar tab di semua browser modern.","confidence":"confirmed","method":"user_statement + common_knowledge","finding":"Page Visibility API didukung semua browser modern. window.onblur sebagai fallback.","evidence_ids":["E-001"],"next_action":"Implementasi visibilitychange event listener"}
```

---

## 3. Change Requests (`change-requests.jsonl`)

### Required additional fields

| Field | Type | Description |
|---|---|---|
| `change_request_id` | string | Matching node ID (e.g. `CR-001`) |
| `reason` | string | Why the change is needed |
| `affected_ids` | array | Node IDs impacted |
| `propagation_status` | string | `pending`, `in_progress`, `regenerated`, `validated`, `rejected` |

### Examples

```json
{"id":"EVT-CR-001","timestamp":"2026-07-24T00:00:00Z","actor":"agent","model_version_before":"2.1.0","model_version_after":"2.1.0","project_revision_before":2,"project_revision_after":3,"type":"change_request","change_request_id":"CR-001","reason":"User mengubah delivery channel dari native app jadi all-web.","affected_ids":["D-001","SURFACE-SISWA","W-SISWA-001","REQ-SISWA-001"],"propagation_status":"regenerated"}
```

### Rules
- Rule 9 of project-planner mandates change requests for **material changes**: framework/language/provider swap, capability/role changes, or >3 nodes altered.
- Always `regenerated` or `validated` after files are patched. Never leave as `pending` when regeneration is done.

---

## 4. Conversation Log (`conversation-log.jsonl`)

### Required additional fields

| Field | Type | Description |
|---|---|---|
| `actor` | string | `"user"` or `"agent"` |
| `type` | string | Event category (see examples) |
| `summary` | string | What happened |
| `key_points` | array | Bullet-point takeaways |

### Examples

```json
{"id":"LOG-001","timestamp":"2026-07-23T00:00:00Z","actor":"user","type":"scope_definition","summary":"User request aplikasi exam profesional untuk sekolah.","key_points":["Domain: sekolah (SD/SMP/SMA/SMK)","Single school, real project","Full scope: bank soal, timer, proctoring, anti-cheat"]}

{"id":"LOG-002","timestamp":"2026-07-23T00:00:00Z","actor":"user","type":"role_definition","summary":"Semua role teridentifikasi.","key_points":["Murid: web responsive","Guru: bank soal, draft, koreksi, analytics","Admin: deploy, monitor, master data","Super Admin: all + audit, config"]}

{"id":"LOG-008","timestamp":"2026-07-23T00:00:00Z","actor":"user","type":"directive","summary":"Selesaikan planning yang belum. Dilarang mulai coding.","key_points":["Selesaikan deliverables","Jangan koding"]}
```

### Suggested `type` values
- `scope_definition` — initial project scope
- `role_definition` — roles identified
- `tech_stack` — technology decisions
- `feature_discovery` — deep-dive per role
- `scope_lock` — scope confirmed by user
- `directive` — explicit user instruction
- `planning_package` — planning artifact created

### Rules
- Final check in project-planner: "Conversation log has been written for this session's key interactions before ending."
- You do **not** need one event per message. One event per meaningful **milestone** (scope definition, role definition, scope lock, directive) is sufficient.
- Model node `E-001` (evidence) should reference the conversation-log via `ref: "conversation:YYYY-MM-DD-topic"`.
