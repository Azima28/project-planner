# Implementation Artifact Generation from Planning Model

When a user asks you to **build** after planning is complete, the planning model (`project-context.json`) becomes a specification you can read programmatically to produce implementation artifacts. This reference documents how to extract concrete deliverables from the model.

## When to use this reference

- User has approved the planning package (0 P0, all gates identified)
- User explicitly asks for implementation: DB schema, project scaffold, code modules
- You are transitioning from planning → building

Do NOT use this during planning itself — the skill boundary says "plan, don't build." Only reach for this when the user explicitly asks for implementation.

---

## 1. Database Schema from Model Entities

Read `work_items`, `delivery_nodes`, `capabilities`, and `integrations` to identify database entities. The model doesn't prescribe a specific database — derive schema from the entities and relationships.

### Mapping principles

| Model Signal | Maps To |
|---|---|
| `delivery_nodes` with `category: "data"` | Core tables |
| `work_items` grouped by domain | Entity groups |
| `integrations` (payment, storage, external) | Ledger/reference tables |
| `capabilities` (identity_access, money_movement, etc.) | Security + audit tables |

### Heuristics (adapt to your stack)

- Each **role** in the model → users table with role discriminator or separate tables
- **Money movement** capability → transaction ledger + audit trail
- **Limited inventory** → state tracking with concurrency handling
- **Real-time** capability → message/event tables
- **Sensitive data** → encryption strategy + immutable audit log
- **External partner** → integration reference tables with external IDs

**Output:** Migration files appropriate for your chosen database (SQL, Prisma, Drizzle, etc.)

### Pitfalls (database-agnostic)
- Design soft-delete strategy for user-facing entities
- Choose ID strategy (UUID, ULID, auto-increment) based on requirements
- Plan full-text search approach if needed (varies by database)
- Add `updated_at` timestamps on mutable tables
- Include audit trail for money-related entities

---

## 2. API Endpoints from Delivery Nodes + Work Items

Every `delivery_node` with `category: "api"` and every `work_item` with CRUD pattern generates endpoints.

### Mapping principles

Read work items and map to standard REST/GraphQL patterns:

| Work Item Pattern | API Pattern |
|---|---|
| Auth/identity | Register, login, token verify, profile |
| CRUD resource | GET list, GET detail, POST create, PUT update, DELETE |
| Transactional (orders, payments) | Create → process → status lifecycle |
| Real-time (chat, notifications) | REST for history + WebSocket/SSE for live |
| Admin operations | Separate route group with elevated permissions |

### Heuristics
- Group by **role** (public, authenticated, admin)
- Use **WebSocket/SSE** for real-time, not REST polling
- **Webhooks** for external partner callbacks
- Consistent response envelope pattern
- API versioning strategy from the start

**Output:** Handler stubs, route registration, middleware — in the structure appropriate for your chosen framework.

---

## 3. Screen/Interface Breakdown (Bridging Artifact)

If the project has user-facing work items, create a screen/interface breakdown — an exhaustive listing per role:

| Column | Content |
|---|---|
| Screen/view name | Route + purpose |
| Entry | Where user comes from |
| Exit | Where user goes after action |
| Components | UI elements needed |
| States | loading, empty, content, error, success |
| Input validation | Per-field: required, format, min/max |
| API calls | Method + path + request/response |

This artifact directly drives:
- Frontend screen/component implementation
- Backend handler + service implementation
- Integration test scenarios

**Output:** `planning/deliverables/screen-breakdown.md`

---

## 4. Project Structure from Architecture Decisions

Read `decision` nodes to determine project structure. Don't assume a structure — derive it.

### Common patterns (not prescriptive)

| Architecture Decision | Typical Structure |
|---|---|
| Modular monolith | `cmd/`, `internal/{domain layers}`, `pkg/{shared}` |
| Microservices | `services/{service-name}/` each with own layers |
| Frontend SPA | `src/{pages,components,services,hooks,context}` |
| Mobile app | `src/{screens,components,navigation,services}` |
| Full-stack monorepo | `apps/{api,web,mobile}`, `packages/{shared}` |
| Serverless | `functions/{function-name}/`, `shared/` |

Adapt to the chosen framework and team conventions. The model's decisions about backend language, frontend framework, and deployment approach should drive structure — not this reference.

---

## 5. Sprint/Phase Backlog from Work Items

Sort `work_items` by `criticality` (critical → high → medium → low) and `lifecycle` (active before deferred).

| Priority | Phase | Typical Content |
|---|---|---|
| Critical | Phase 1 | Auth/identity, core infrastructure, primary data model |
| High | Phase 2 | Core business features (varies by project) |
| Medium | Phase 3-4 | Secondary features, integrations |
| Low/Deferred | Backlog | Nice-to-have, future considerations |

Per phase: generate implementation layer by layer following your architecture pattern.

---

## 6. Delivery Checklist

- [ ] DB schema covers all entities derived from capabilities + work_items
- [ ] API/interface endpoints derived from delivery_nodes + work_items
- [ ] Screen/interface breakdown (if user-facing) lists every view with components, states, API
- [ ] Project structure matches architecture decisions
- [ ] Phase 1 backlog = critical items (auth + core infrastructure first)
- [ ] Each phase delivers across all layers (data → logic → interface)
- [ ] Implementation artifacts trace back to model nodes (include source IDs in comments/docs)
