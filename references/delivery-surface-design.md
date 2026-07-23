# Delivery Surface and Service Design

Use this reference when the project has direct users, more than one role, physical/digital channels, or the user requests UX, UI, visual, mockup, or design work. Do not read for pure backend/data unless a channel decision affects operations.

## Core principle

Design the service before the interface:

```text
outcome → roles and tasks → risk/failure → channel per role → information and procedures → surface-specific design → test
```

`screen` is not an assumption. Channels can be native app, web/PWA, desktop, POS, kiosk, card/QR, physical artifact, staff procedure, or hybrid. Tasks, rules, receipts, and recovery must remain consistent if the channel changes.

## Discovery that changes design

Collect in small batches:

1. Who are the roles, owners, and affected parties? Who shares a device or is not allowed to carry a phone?
2. What tasks must be fast, infrequent, risky, or can be performed by staff?
3. What are the real devices, connectivity, accessibility, language, location, and usage time?
4. What channels are available/prohibited, and is one channel sufficient for all roles?
5. What proof is needed: digital receipt, printed slip, audit log, signature, or physical output?
6. What are the failure/recovery conditions: network loss, device failure, identity mismatch, queuing, correction, or human escalation?

If answers are missing, record as `unknown` or decision `assumed`; choose the lowest-risk channel. Do not fill gaps with applications, dashboards, chatbots, or generic mockups.

## Model channels as graph

For important channel decisions, create a delivery node with category `surface` and connect it to work items/capabilities with typed edges. A `surface` node uses:

- `surface_kind`: `native_app`, `web`, `pwa`, `desktop`, `pos`, `kiosk`, `physical_card`, `human_procedure`, `api_only`, or `custom`.
- `roles`: roles that use the surface.
- `context`: device, connectivity, location, or constraints that affect design.

Use a separate decision when choosing or deferring a channel changes cost, risk, access, or scope. Do not store "mobile-first" as a slogan without role, device, and reasoning.

## Artifacts triggered by service experience

Activate the `service_experience` policy when user-facing work, multiple roles, or channel becomes a material decision. Add manifest `include` or `skip` for:

| Artifact | Minimum content |
|---|---|
| `channel_decision` | Channel per role, constraints, reasoning, fallback, and conditions for channel change. |
| `service_blueprint` | Roles, tasks, handoffs, source of truth, proof, failure, recovery, and owner. |
| `interaction_spec` | Information, state, actions, content, input/output, and error/recovery for each task. |
| `accessibility_spec` | Relevant accessibility requirements for the chosen channel and verification method. |
| `usability_test_plan` | Target users, tasks, metrics/observations, success criteria, and how to act on findings. |
| `visual_design_spec` | Only when visual is needed: visual principles, tested tokens, typography, components, asset source, and anti-patterns. |

For physical/procedural channels, `interaction_spec` can be an SOP, signage, form, receipt, or handling procedure. For backend only, mark as `skip` with rationale and condition that makes it required in the future.

## Surface-specific routing

| Surface | Add | Do not assume |
|---|---|---|
| Native app | permission/device state, navigation, push/offline behavior, touch target, platform accessibility | all users can/want to install an app |
| Web/PWA | responsive layout, keyboard/focus, browser/session behavior, supported devices | native hardware capability or permanent connection |
| Desktop/admin | tables/filters, bulk actions, audit, role/session, export | mobile navigation patterns or small touch targets |
| POS/kiosk | shift/device ownership, speed, peripherals, recovery, receipt | consumer dashboard or multi-layer forms |
| Card/QR/physical | issuance/replacement, loss, forgery, privacy, staff procedure | card as sole authenticator or device always functional |
| Human procedure | owner, script, proof, escalation, training, contingency | process auditable without clear records |
| Hybrid | source of truth, ordering, cross-channel state, conflict/revocation/recovery | each channel can make its own rules |

## Visual design without AI templates

Visuals are created only after tasks, channels, and states are stable. Planning produces direction and constraints only; visual implementation details are the coding agent's job (see "Visual design spec boundary in planning" below). Follow these principles:

- Derive character from audience, context, existing brand, real content, and work rhythm — not just adjectives like "premium/modern."
- Do not use emoji as system icons or label substitutes. Use a consistent icon family and text labels for important actions.
- Avoid glassmorphism, neon gradients, layered cards, generic 3D illustrations, and metric dashboards without actions, unless there is a documented and tested reason.
- Use real photos/assets or clearly marked placeholders. Every local asset referenced in Markdown must exist and be modeled as an artifact; do not claim mockups that have not been created.
- Do not promise "guaranteed to be liked by many users." Test prototypes with different roles; record task success, errors, confusion, and recurring preferences.
- Do not use color as the sole status indicator. Write state, icon, and recovery action explicitly.

## Testable design criteria

Define criteria per channel, for example:

- All critical tasks have a happy path, failure/recovery path, owner, and acceptance evidence.
- Touch surfaces use operable targets and tested contrast; keyboard surfaces have focus order and shortcuts where relevant; physical procedures have signage/SOP that can be practiced.
- Every meaningful status has text, an accessible icon/signal, and next action.
- Local assets/links are valid; visual spec does not claim files that do not exist.
- User testing separates roles with different goals; fixes enter change requests and affect the correct artifacts.

- Do not copy accessibility numbers from one platform to all surfaces. Reference the chosen platform's guidelines and record the standard/source as evidence if the claim is `confirmed`.

## Visual design spec boundary in planning

Planning produces **direction and constraints**, not visual implementation. But this is not a rigid wall — adjust to context.

### How to think about this boundary

Ask: "Does this decision require framework/platform context that does not yet exist?" If yes, it is the coding agent's job. If not (e.g., user already has a brand guide), the planner may be more specific.

**Planner always determines** (because these come from user, audience, and business):
- Brand character, positioning, differentiation from competitors
- Color mood and direction (not hex codes — unless user/brand guide already has them)
- Typography direction (geometric/humanist — not font family + size)
- Accessibility constraints (non-negotiable, always record)
- Anti-requirements (what to avoid — often more useful than what to build)
- Reference apps as mood anchors
- Navigation architecture (this is an architectural decision, not visual)
- State requirements (loading, empty, error, success — this is a UX decision)

**Coding agent always determines** (because these require implementation context):
- Complete color palette with scale
- Typography scale, line heights, letter spacing
- Spacing system, border radius, elevation
- Component styling
- Animation/motion
- Dark mode palette
- Responsive breakpoints

**Grey area — depends on situation:**
- Hex color → allowed if from brand guide, not allowed if planner invents it
- Font family → allowed if user requests specifically, not allowed if planner assumes
- Layout grid → allowed if "2-column product grid" (e-commerce convention), not allowed if detailed dp values

### Good planner decision example

> "Primary color hue warm — coral/terracotta/amber are fine — but must be **different** from Shopee orange and Tokped green. Neutral: clean whites, not yellowish off-white."

This is good because: it gives clear direction (warm, not cool), specific constraints (not Shopee/Tokped), and flexibility (coding agent picks exact hue).

### Bad planner decision example

> "Primary: #E53935 (Red-600), Secondary: #FFB300 (Amber-600)"

This is bad because: hex codes without brand guide basis, just copied from Material palette, and coding agent has no creative room.

### Anti-patterns that are always prohibited regardless of context

- ASCII wireframes/mockups as design substitutes — these are not visual representations, they are misleading
- Claiming mockups/screenshots that have not been created
- Emoji as system icons
- Empty adjectives ("premium", "modern", "sleek") without concrete definition from audience
- Directly copying competitor palettes without differentiation

For complete reference with case examples per project type, see `references/design-handoff-contract.md`.
