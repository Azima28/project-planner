# Evidence Research and Fallback Protocol

Research strengthens decisions; it does not replace user permission, partner access, or authorized review.

## Evidence record

Every external claim has an evidence node with `kind`, `ref`, `scope`, `retrieved_at`, `confidence`, `sensitivity`, and `review_after` if volatile. Add a research node for claims, contradictions, and next action.

Record failed attempts as `tool_failure` evidence: question/scope, time, tool or source attempted, result (`unavailable`, `rate_limited`, `paywall`, `not_found`, `conflict`), and fallback. "Not found" is not evidence that something does not exist or is safe.

## Evidence hierarchy

1. Official provider/regulator/authority documents and user contracts.
2. Standards, primary papers, or official reports.
3. Credible independent sources that corroborate each other.
4. Reviews/pain points as hypotheses, not legal/technical facts.
5. Analogies/knowledge base only as `assumed`.

Seek evidence that contradicts initial conclusions. If a conflict is unresolved, use confidence `conflicting`; if research is insufficient, use `research_incomplete`; both block production claims that depend on them.

## Safe fallbacks

| Gap | Fallback |
|---|---|
| Partner/API unavailable | mock adapter, defer, investigate, or out-of-scope |
| Insufficient market data | hypothesis + user research/experiment with exit criterion |
| Legal/regulatory unclear | conservative scope + review owner; do not claim compliant |
| Web/tool failure | tool-failure evidence + user document/other primary source; still lower confidence |
| Rapidly changing data | range + review date before release decision |

## Evidence integrity

Evidence must be honest — it is the foundation of the entire planning package. But "honest" does not mean rigid. It means recording what actually happened, not what we hoped would happen.

### Principles

- `ref` must point to a real source. URL, conversation timestamp, official document, or local file. Do not fabricate references.
- `confidence: confirmed` means there is an explicit statement from the user or an official source. Not "user didn't object so we assume agreement."
- Ambiguous answers are still recorded, but as `assumed` with a follow-up question. Do not fill gaps with interpretation and then mark as `confirmed`.
- Research that is no longer applicable (user chose an alternative) should immediately change to `superseded`.

### Examples

**Good:**
```json
{
  "id": "E-003",
  "kind": "user_statement",
  "ref": "conversation:2026-07-21-batch1",
  "scope": "User stated 'just use react' when asked about framework.",
  "confidence": "confirmed"
}
```
This is good: ref points to an actual conversation, scope quotes the actual answer, confidence is confirmed because the user explicitly stated it.

**Bad:**
```json
{
  "id": "E-004",
  "kind": "user_statement",
  "ref": "conversation:2026-07-21-security",
  "scope": "Security baseline confirmed by user.",
  "confidence": "confirmed"
}
```
This is bad: the `security` conversation never happened (fabricated ref), the user never explicitly discussed security (this is agent inference), but it is marked `confirmed`. Should be `kind: agent_inference`, `confidence: assumed`.
