# Domain Probe Library

This is a list of trigger questions, not provider facts, pricing, design, or technology recommendations. Research up-to-date sources every time an answer affects a decision.

| Domain signal | Probe | Potentially active capability |
|---|---|---|
| Commerce/booking | Can items/seats run out or be booked simultaneously? | `limited_inventory`, `money_movement` |
| Health/education/public service | What data is sensitive or regulated? Who is the authority? | `sensitive_data`, `regulated` |
| Finance/payment | Who holds the money and handles disputes/refunds? | `money_movement`, `regulated` |
| Logistics/location | How accurate is the location and what is the fallback if stale? | `real_time`, `offline_sync`, `sensitive_data` |
| Community/content | Who moderates abuse and handles appeals? | `identity_access`, `custom` |
| AI/data | Where does the data/model come from, how is it evaluated, who corrects? | `data_ai`, `sensitive_data` |
| Internal ops/event | Who runs the procedure when it fails or in the field? | `operations`, `physical_safety` |
| Legacy migration | What must not be lost, how to rollback, and when is cutover? | `migration` |

Add rows/custom capabilities when a new domain does not fit. Do not infer partner access, legal obligations, pricing, or API compatibility from this list.
