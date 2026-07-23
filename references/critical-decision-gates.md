# Critical Decision Gates

Use these gates only when a capability or archetype triggers them. Do not request secret values; record only the evidence ID and a non-secret `secret_ref`.

## Single access contract

Use exactly one enum: `production_confirmed`, `sandbox_only`, `claimed_unverified`, `unavailable`, `unknown`, or `not_needed`. Do not create synonyms such as `confirmed`.

| Access | Maximum delivery mode | Requirement |
|---|---|---|
| `production_confirmed` | production | Official evidence + owner + release condition |
| `sandbox_only` | sandbox/limited pilot | Environment boundary and failure behavior |
| `claimed_unverified` / `unknown` | mock/defer/investigate | Do not claim real integration |
| `unavailable` | mock/defer/out_of_scope | Fallback and conditions to upgrade mode |
| `not_needed` | not needed | Rationale recorded |

## Capability-triggered gates

| Capability | Minimum receipt before higher mode |
|---|---|
| partner/API | access status, evidence, contract/permission, owner, fallback |
| money movement | money boundary, provider mode, state lifecycle, reconciliation/refund/dispute owner |
| sensitive/regulated data | classification, lawful purpose, access/retention/deletion, legal owner |
| identity/admin/multi-tenant | roles, scope/isolation, recovery, audit, abuse path |
| offline/sync | offline boundary, source of truth, conflict/revocation/recovery rule |
| inventory/concurrency | ownership, reservation/expiry/idempotency, race/failure test |
| production | approver, operational owner, monitoring, rollback, incident route, release evidence |

After a high-risk gate, display a receipt: recorded facts, chosen mode, what will NOT be built, fallback, and evidence needed to upgrade mode. A single "yes" must not approve multiple decisions at once.

## Waivers

P0 risks or legal/regulatory obligations cannot be waived by the planner. Other risks may only be waived with an authorized approver, evidence, reason, compensating control, expiry, and review date. Expired waivers automatically revert to blockers.

## Enforcement

A gate receipt is not a formality — it is a contract between the planner and the user. The user must know what was decided, what the consequences are, and how things can change later.

Every high-risk gate produces a receipt displayed before proceeding. Do not batch multiple gates in a single response without a receipt per gate — the user may miss reading them.

**Example receipt for a payment gate:**

> **Gate: Payment — money_movement**
>
> **Facts**: User wants a marketplace with 5% commission + 5% tax. Midtrans selected as payment gateway.
>
> **Mode chosen**: Sandbox (mock) — no real money in pilot.
>
> **What will NOT be built**: Production payment flow, refund automation, settlement reconciliation.
>
> **Fallback**: Mock adapter if Midtrans sandbox is down.
>
> **To upgrade to production**: Midtrans production key, end-to-end testing with real money, documented refund policy.
>
> Are the facts above correct? Any corrections?

**Must not:**
- Assume a gate is resolved because the user was silent (silence ≠ consent)
- Mark a gate as `confirmed` without evidence containing the user's statement about that gate
- Process a gate without explaining consequences and fallback
