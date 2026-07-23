# Extensible Capability and Policy Catalog

A capability is a policy trigger, not a domain label or tier. Add new capabilities when the project does not fit the catalog; custom nodes must set `policy_ids: ["custom"]` and specify their own `custom_policy` object (`trigger`, `required_artifact_types`, `required_delivery_categories`, `gate_description`, `owner`, and `release_condition`). 

> **CRITICAL**: The `policy_ids` array must contain ONLY valid built-in policy IDs from the table below, or `["custom"]`. Do NOT invent arbitrary policy ID strings like `policy_ids: ["online_exam_policy"]`. Arbitrary policy strings cause `UNKNOWN_POLICY` and `POLICY_ARTIFACT_UNMODELED` P0/P1 validation errors. Connect all capabilities to work items/artifacts with `requires` edges so the validator can check their delivery.

| Policy ID | Signal | Gate / minimum output | Feature expansion trigger |
|---|---|---|---|
| `identity_access` | login, permission, admin | role matrix, recovery/abuse path, audit need | Explore per role: profile, session mgmt, activity history, permission config UI |
| `money_movement` | payment, refund, wallet, invoice | lifecycle, idempotency, reconciliation, dispute/refund owner | Explore per role: transaction history, payment methods, invoice generator, refund status |
| `limited_inventory` | seat, stock, quota, booking | source of truth, hold/expiry, concurrent/failure test | Explore per role: real-time availability, booking management, waitlist, low stock alerts |
| `external_partner` | provider, vendor, operator | readiness matrix, contract boundary, fallback, owner | Explore per role: integration health dashboard, partner config, fallback manual overrides |
| `real_time` | live state/chat/tracking | ordering, reconnect, stale/recovery behavior | Explore per role: status dashboard, live feed, connection status, history/replay |
| `service_experience` | user-facing task, multi-role/channel | channel decision, service blueprint, state/recovery, accessibility | Explore per role: notifications, help/FAQ, onboarding, feedback, settings, themes |
| `offline_sync` | local use without network | boundary, conflict/revocation, recovery playbook | Explore per role: sync status indicator, offline conflict resolution UI, forced sync button |
| `sensitive_data` | identity, health, finance, documents | classification, purpose, access/retention/deletion | Explore per role: data export, privacy settings, consent management, audit trail viewer |
| `regulated` | government, medical, financial, safety | jurisdiction map, authoritative source, review owner | Explore per role: compliance reports, terms acceptance logs, document verification UI |
| `data_ai` | model, dataset, automated decision | provenance, evaluation, bias/abuse, human fallback | Explore per role: model explanation/confidence scores, feedback/correction loop UI |
| `migration` | legacy/data/platform change | inventory, compatibility, migration/rollback, cutover test | Explore per role: migration status tracker, data validation UI, legacy fallback toggle |
| `physical_safety` | device, venue, field work | hazard, safe procedure, contingency, responsible person | Explore per role: emergency stop, safety checklist UI, incident reporting flow |
| `custom` | anything else | custom policy contract; no silent omission | Map custom triggers appropriately |

Policy evaluation produces artifact candidates and graph edges. It must never select a provider, stack, or visual style automatically.
