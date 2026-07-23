# Technology Selection Framework

Use only when the user requests strategy or technology. No domain, size, or capability automatically selects a framework, cloud, provider, microservices, or visual design.

## Decision record

Compare choices based on requirements and actual evidence:

| Criterion | Question | Evidence / constraint |
|---|---|---|
| Delivery fit | Platform, team skill, deadline, maintainability? | [IDs] |
| Risk fit | Security, privacy, data locality, failure/recovery? | [IDs] |
| Integration | Access, contract, sandbox, exit/fallback? | [IDs] |
| Cost and operation | TCO, owner, observability, rollback? | [IDs] |
| Evolution | Migration path, lock-in, portability, testability? | [IDs] |

Offer few options that are genuinely feasible, explain trade-offs, and store the decision + release condition. Pricing, versions, provider capabilities, and compliance must be researched at the time; do not rely on static knowledge.

## Safe heuristics

- Choose the simplest solution that meets evidence and current release conditions.
- Add services only when there is a proven boundary/ownership/failure mode requiring them.
- Start with a mock adapter if the partner is not yet available, not an imagined API.
- Visual design comes from user, audience, accessibility, brand, device, and context of use; not from domain default colors.
