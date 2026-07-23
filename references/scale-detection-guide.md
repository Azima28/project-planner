# Proportional Planning Guide

Planning depth is determined by risk, irreversibility, and evidence — not team size, domain name, or a single tier score.

| Signal | Add depth |
|---|---|
| Decision easily reversible, single owner, no data/money/partner | concise brief, acceptance criteria, risk/unknown, basic trace |
| Many work items or dependencies | graph, artifact manifest, change impact, delivery ownership |
| Sensitive data, money, safety, regulation, partner, or production | critical gates, evidence freshness, adversarial tests, release controls |
| Multiple teams/regions/legacy systems | namespace/ownership, interface contracts, migration, rollout/rollback, decision cadence |
| High volatility | review date, assumptions register, experiment/telemetry, short planning horizon |

Do not use "lite/standard/program" as jargon with the user. Use it only as the number of active controls and explain with impact language: "because there is payment, we need to ensure reconciliation and a refund owner."

If constraints conflict — for example, a critical service, very short timeline, and no operations owner — reduce mode/scope or create a blocker. Do not disguise it by swapping stacks.
