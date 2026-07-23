# Extensible Capability and Policy Catalog

A capability is a policy trigger, not a domain label or tier. Add new capabilities when the project does not fit the catalog; custom nodes must specify their own `trigger`, `required_artifact_types`, `required_delivery_categories`, `gate_description`, `owner`, and `release_condition`. Connect custom capabilities to work items with `requires` edges so the validator can check their delivery.

| Policy ID | Signal | Gate / minimum output |
|---|---|---|
| `identity_access` | login, permission, admin | role matrix, recovery/abuse path, audit need |
| `money_movement` | payment, refund, wallet, invoice | lifecycle, idempotency, reconciliation, dispute/refund owner |
| `limited_inventory` | seat, stock, quota, booking | source of truth, hold/expiry, concurrent/failure test |
| `external_partner` | provider, vendor, operator | readiness matrix, contract boundary, fallback, owner |
| `real_time` | live state/chat/tracking | ordering, reconnect, stale/recovery behavior |
| `service_experience` | user-facing task, multi-role/channel, UX/UI, service, or visual design | channel decision, service blueprint, state/recovery, accessibility, usability test |
| `offline_sync` | local use without network | boundary, conflict/revocation, recovery playbook |
| `sensitive_data` | identity, health, finance, documents | classification, purpose, access/retention/deletion, privacy owner |
| `regulated` | government, medical, financial, safety | jurisdiction map, authoritative source, review owner |
| `data_ai` | model, dataset, automated decision | provenance, evaluation, bias/abuse, human fallback, monitoring |
| `migration` | legacy/data/platform change | inventory, compatibility, migration/rollback, cutover test |
| `physical_safety` | device, venue, field work | hazard, safe procedure, contingency, responsible person |
| `custom` | anything else | custom policy contract; no silent omission |

Policy evaluation produces artifact candidates and graph edges. It must never select a provider, stack, or visual style automatically.
