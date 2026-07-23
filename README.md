# Project Planner Skill

An adaptive, high-assurance planning skill for AI coding agents. It dynamically discovers project requirements, produces traceable planning artifacts, and validates consistency through a canonical JSON graph model.

## What it does

- **Adaptive Interview**: Dynamically discovers archetype, delivery channel, roles, features, and risks through context-reactive conversations — not static questionnaires.
- **Graph-Based Model**: Maintains a canonical `project-context.json` with typed nodes and edges for evidence, decisions, requirements, work items, delivery, risks, and artifacts.
- **Self-Validation**: Runs automated validation (`validate_project_model.py`) that checks graph integrity, artifact synchronization, policy coverage, and tree completeness.
- **Traceable Outputs**: Every decision, research finding, and change is logged in append-only JSONL event logs for full auditability.

## Structure

```
SKILL.md                          ← Main skill instructions
references/                       ← Reference documents read at each workflow step
  interview-decision-tree.md      ← Adaptive interview framework
  domain-knowledge.md             ← Domain-specific probing amplifiers
  capability-catalog.md           ← Policy triggers and feature expansion signals
  project-model.md                ← Graph model v2 contract
  project-context.schema.json     ← JSON Schema for model validation
  project-context.template.json   ← Starter template for new projects
  delivery-surface-design.md      ← Channel/surface design guidance
  design-handoff-contract.md      ← Planning vs coding agent boundary
  research-protocol.md            ← Evidence research and fallback rules
  critical-decision-gates.md      ← High-risk decision gate protocol
  artifact-manifest.md            ← Artifact selection and lifecycle
  deliverable-templates.md        ← Derived artifact templates
  technology-selection.md         ← Technology choice framework
  validation-protocol.md          ← Validation and reconciliation rules
  validation-iteration-patterns.md← Common validation error patterns
  forward-test-matrix.md          ← Forward test scenarios
  control-artifact-templates.md   ← Control report contract
  scale-detection-guide.md        ← Proportional planning depth
  fullstack-checklist.md          ← Planning completeness checklist
  session-continuity.md           ← Multi-session resume protocol
  prompt-engineering-guide.md     ← Coding agent handoff prompt
  implementation-artifact-generation.md ← Generate code artifacts from model
  example-cases.md                ← Rule application examples
scripts/
  validate_project_model.py       ← Automated model validator
  migrate_project_model.py        ← v1 → v2 model migration
  test_validate_project_model.py  ← Validator unit tests
  requirements.txt                ← Python dependencies
```

## Usage

This skill is designed for use with AI coding agents (e.g., Gemini in Antigravity IDE). Place it in your skills directory and the agent will automatically discover and use it when asked to plan a project.

## License

MIT
