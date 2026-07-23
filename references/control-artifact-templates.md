# Control Report Contract

Three reports are written by the validator from the same model. Do not manually fill `pass` status.

| Report | Minimum content |
|---|---|
| Planner execution | instruction/policy compliance, policy coverage, event-log receipt, evidence, decision, research, unknown, gate, eligibility |
| Synchronization | missing artifact, file/hash/version mismatch, local asset/link integrity, orphan, decision violation, change propagation |
| Tree coverage | total, covered, gap, blocked, orphan, N/A rationale for seven trees |

All reports contain `model_version`, `validation_run`, timestamp, severity, evidence/file pointers, and corrective action. `issues: []` must not be presented as user acceptance, semantic completeness, or production readiness without reading all report sections. No report contains chain-of-thought.
