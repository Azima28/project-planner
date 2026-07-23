# Session Continuity Protocol

Planning projects often span multiple sessions. This reference defines how an agent continues work from a previous session.

## Standardized workspace

```text
planning/
  project-context.json          ← canonical model
  decisions.jsonl                ← decision event log
  research-ledger.jsonl          ← research event log
  change-requests.jsonl          ← change event log
  conversation-log.jsonl         ← interview/conversation history
  reports/
    planner-execution-report.json
    synchronization-report.json
    tree-coverage-report.json
  deliverables/
```

## Conversation log format (conversation-log.jsonl)

Each line is a JSON object:

```json
{"role": "user|assistant|system", "timestamp": "ISO-8601", "content": "...", "tool_name": null}
```

- `role: user` — user statements, answers, or instructions
- `role: assistant` — agent responses
- `role: system` — metadata (model version, artifact ID, etc.)
- `timestamp` — actual time, not a placeholder. Do not make all timestamps identical.
- `tool_name` — name of the tool called (null if none)

The conversation log is **append-only**. Do not edit or delete old entries.

## Resume checklist for a new agent

When continuing an existing project, follow this order:

### 1. Read state (do not assume)
- Read `project-context.json` — this is the source of truth
- Read `conversation-log.jsonl` — this is the interview history
- Read all 3 reports (if they exist)
- Read all event logs (decisions, research, change-requests)

### 2. Identify status
- How many decisions exist? Which ones are still `assumed`?
- How many `include` artifacts already have files?
- How many evidence items are still `unverified`?
- Are there P0 issues in the last report?
- **Interview phase progress** (see `references/interview-decision-tree.md`):
  - Phase 1 (Understand & Reflect): completed or not?
  - Phase 2 (Stakeholder & Scope): MVP/phasing discussed?
  - Phase 3 (Role Deep Dive): which roles have been probed, which have not? Which of the 7 dimensions were covered per role?
  - Phase 4 (Synthesis): was scope locked by user?
- Are there `deferred_discovery` items from a previous session where the user cut the interview short?

### 3. Report to user
Before doing anything, communicate the status including interview progress:

> "From the previous session: 11 decisions (9 confirmed, 2 assumed), 5/8 deliverables have files, 3 P1 open. Interview progress: Phase 1-2 complete. Phase 3 deep dive done for Student and Teacher roles; Admin and Super Admin roles not yet explored. Phase 4 scope lock not yet confirmed. Where would you like to continue?"

### 4. Do not repeat answered interviews
If the conversation log shows the user already answered a question, DO NOT ask it again. Record as evidence from the conversation log. Resume from the exact phase/role/dimension where the previous session stopped.

### 5. Do not change old decisions without reason
If the previous session decided on React Native framework, do not suddenly suggest Flutter without a change request.

## Edge cases

- **Conversation log does not exist**: Read the model only. Assume interview history is lost. Ask the user: "I don't see a conversation log. Should I re-ask some questions, or proceed directly from the model?"
- **Model v1**: Run `scripts/migrate_project_model.py` first.
- **Report shows many P0s**: Do not fix everything immediately. Communicate to the user first, prioritize together.
- **User says "start from scratch"**: Archive the old folder (rename to `planning_v1/`), create a new `planning/`.
