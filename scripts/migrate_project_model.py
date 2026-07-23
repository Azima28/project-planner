#!/usr/bin/env python3
"""Create a safe v2 Project Planner model from a legacy v1 snapshot.

Imported confirmations are deliberately downgraded to unverified until a user,
primary source, or current artifact supplies v2 evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def values(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def state(old_status: str | None) -> tuple[str, str]:
    mapping = {
        "deferred": ("deferred", "assumed"),
        "out_of_scope": ("out_of_scope", "assumed"),
        "superseded": ("superseded", "unverified"),
        "blocked": ("active", "blocked"),
        "assumed": ("active", "assumed"),
        "unverified": ("active", "unverified"),
        "conflicting": ("active", "conflicting"),
        "research_incomplete": ("active", "research_incomplete"),
        "planned": ("draft", "assumed"),
        "draft": ("draft", "assumed"),
        "validated": ("draft", "unverified"),
        "complete": ("draft", "unverified"),
    }
    return mapping.get(old_status or "", ("active", "unverified"))


def category_from_id(node_id: str) -> str:
    prefix = node_id.split("-", 1)[0]
    return {
        "FLOW": "flow", "SCREEN": "screen", "API": "api", "DATA": "data",
        "SEC": "security", "TEST": "test", "METRIC": "metric", "RUNBOOK": "runbook",
    }.get(prefix, "custom")


def node_base(old: dict[str, Any]) -> dict[str, Any]:
    lifecycle, confidence = state(old.get("status"))
    result = {key: value for key, value in old.items() if key not in {"status", "mode", "trace", "type", "name"}}
    result["id"] = old["id"]
    result["lifecycle"] = lifecycle
    result["confidence"] = confidence
    if confidence == "blocked" and not result.get("next_action"):
        result["next_action"] = "Review this imported blocker and choose a safe fallback."
    if lifecycle == "deferred" and not result.get("target_release"):
        result["target_release"] = "to_be_confirmed"
    if lifecycle == "superseded" and not result.get("superseded_by"):
        result["superseded_by"] = "to_be_confirmed"
    return result


def migrate(old: dict[str, Any], source_ref: str) -> dict[str, Any]:
    old_project = old.get("project", {}) if isinstance(old.get("project"), dict) else {}
    mode = old_project.get("mode", "prototype_mock")
    if mode not in {"prototype_mock", "sandbox", "pilot", "production"}:
        mode = "prototype_mock"
    feature_list = [item for item in old.get("features", []) if isinstance(item, dict)]
    archetype = "software_product" if feature_list else "custom"
    output: dict[str, Any] = {
        "$schema": "./project-context.schema.json",
        "project": {
            "id": old_project.get("id", "migrated-project"),
            "name": old_project.get("name", "Migrated Project"),
            "model_version": "2.1.0",
            "revision": 1,
            "archetype": archetype,
            "operating_mode": "prototype_mock" if mode == "production" else mode,
            "lifecycle": "draft",
            "output_language": old_project.get("locale", "id-ID"),
            "migration_note": "Imported from v1. Production mode was lowered until all v2 evidence and release gates are reviewed.",
        },
        "evidence": [{
            "id": "E-MIGRATION-001", "kind": "internal_record", "ref": source_ref,
            "scope": "legacy v1 model imported without current v2 evidence verification",
            "retrieved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "confidence": "unverified", "sensitivity": "internal",
        }],
        "instructions": [], "decisions": [], "research": [], "capabilities": [], "requirements": [],
        "work_items": [], "delivery_nodes": [], "integrations": [], "risks": [],
        "change_requests": [], "artifacts": [], "edges": [], "unknowns": [],
    }
    if archetype == "custom":
        output["project"]["custom_archetype"] = "Review and classify imported legacy project."

    internal_ids: set[str] = {"E-MIGRATION-001"}
    for group in ("instructions", "decisions", "research", "capabilities", "requirements", "delivery_nodes", "integrations", "risks", "unknowns"):
        for old_node in old.get(group, []):
            if not isinstance(old_node, dict) or not isinstance(old_node.get("id"), str):
                continue
            node = node_base(old_node)
            if group == "instructions":
                node["text"] = old_node.get("text", "Imported instruction")
                node["acceptance_criteria"] = old_node.get("acceptance_criteria") or ["Review imported acceptance criteria."]
            elif group == "decisions":
                node["topic"] = old_node.get("topic", "imported_decision")
                node["value"] = old_node.get("value", "to_be_reviewed")
            elif group == "research":
                node["claim"] = old_node.get("claim", "Imported research claim")
                node["evidence_ids"] = ["E-MIGRATION-001"]
                node["next_action"] = old_node.get("next_action", "Re-research with current evidence.")
            elif group == "capabilities":
                node["key"] = old_node.get("name", old_node["id"]).lower().replace(" ", "_")
                node["policy_ids"] = [node["key"] if node["key"] else "custom"]
                if node["policy_ids"] == ["custom"]:
                    node["custom_policy"] = {"note": "Define gates, artifacts, tests, owner, and release condition."}
            elif group == "requirements":
                node["title"] = old_node.get("title", old_node["id"])
                node["requirement_type"] = old_node.get("requirement_type", "functional")
            elif group == "delivery_nodes":
                node["title"] = old_node.get("title", old_node.get("type", old_node["id"]))
                node["category"] = old_node.get("category", category_from_id(old_node["id"]))
            elif group == "integrations":
                node["name"] = old_node.get("name", old_node["id"])
                node["capability_id"] = old_node.get("capability_id", "CAP-MIGRATION-001")
                node["delivery_mode"] = old_node.get("delivery_mode", "deferred")
                node["access_status"] = "claimed_unverified"
                node["fallback"] = old_node.get("fallback", "investigate_or_mock")
                node["owner"] = old_node.get("owner", "to_be_confirmed")
                node["release_condition"] = old_node.get("release_condition", "Verify official access and contract.")
            elif group == "risks":
                node["title"] = old_node.get("title", old_node["id"])
                node["severity"] = old_node.get("severity", "P1")
                node["owner"] = old_node.get("owner", "to_be_confirmed")
                node["next_action"] = old_node.get("next_action", "Review mitigation and verification.")
            elif group == "unknowns":
                node["question"] = old_node.get("question", old_node["id"])
                node["next_action"] = old_node.get("next_action", "Resolve or explicitly defer.")
            output[group].append(node)
            internal_ids.add(node["id"])

    existing_delivery = {node["id"] for node in output["delivery_nodes"]}
    for old_feature in feature_list:
        if not isinstance(old_feature.get("id"), str):
            continue
        node = node_base(old_feature)
        trace = old_feature.get("trace", {}) if isinstance(old_feature.get("trace"), dict) else {}
        profile = "user_facing" if values(trace.get("screen_ids")) or values(trace.get("flow_ids")) else "backend"
        node.update({
            "title": old_feature.get("name", old_feature["id"]),
            "work_type": "feature",
            "delivery_profile": profile,
            "acceptance_criteria": old_feature.get("acceptance_criteria") or ["Review imported acceptance criteria."],
        })
        output["work_items"].append(node)
        internal_ids.add(node["id"])
        for key, ids in trace.items():
            if not key.endswith("_ids"):
                continue
            for delivery_id in values(ids):
                if delivery_id not in existing_delivery:
                    output["delivery_nodes"].append({
                        "id": delivery_id, "title": f"Imported {delivery_id}", "category": category_from_id(delivery_id),
                        "lifecycle": "draft", "confidence": "unverified",
                    })
                    existing_delivery.add(delivery_id)
                    internal_ids.add(delivery_id)

    for old_artifact in old.get("artifacts", []):
        if not isinstance(old_artifact, dict) or not isinstance(old_artifact.get("id"), str):
            continue
        node = node_base(old_artifact)
        source_ids = [item for item in values(old_artifact.get("source_ids")) if item in internal_ids]
        node.update({
            "artifact_type": old_artifact.get("type", "imported_artifact"),
            "disposition": "include", "rationale": "Imported artifact must be reconciled against v2 graph.",
            "source_ids": source_ids or ["E-MIGRATION-001"], "trigger_ids": ["E-MIGRATION-001"],
            "model_version": "2.1.0", "lifecycle": "draft", "confidence": "unverified",
        })
        output["artifacts"].append(node)
        internal_ids.add(node["id"])

    edge_number = 1

    def edge(source: str, target: str, relation: str) -> None:
        nonlocal edge_number
        if source not in internal_ids or target not in internal_ids:
            return
        output["edges"].append({
            "id": f"EDGE-MIG-{edge_number:03d}", "from_id": source, "to_id": target,
            "relation": relation, "lifecycle": "draft", "confidence": "unverified",
        })
        edge_number += 1

    for requirement in old.get("requirements", []):
        if not isinstance(requirement, dict):
            continue
        for instruction_id in values(requirement.get("instruction_ids")):
            edge(instruction_id, requirement.get("id", ""), "informs")
        for decision_id in values(requirement.get("decision_ids")):
            edge(decision_id, requirement.get("id", ""), "constrains")
    for feature in feature_list:
        feature_id = feature.get("id", "")
        for requirement_id in values(feature.get("requirement_ids")):
            edge(requirement_id, feature_id, "implemented_by")
        for decision_id in values(feature.get("decision_ids")):
            edge(decision_id, feature_id, "constrains")
        trace = feature.get("trace", {}) if isinstance(feature.get("trace"), dict) else {}
        for key, ids in trace.items():
            relation = "verified_by" if key == "test_ids" else "delivers"
            for delivery_id in values(ids):
                edge(feature_id, delivery_id, relation)
    for decision in old.get("decisions", []):
        if isinstance(decision, dict):
            for target in values(decision.get("impact_ids")):
                edge(decision.get("id", ""), target, "impacts")
    for integration in old.get("integrations", []):
        if isinstance(integration, dict):
            edge(integration.get("capability_id", ""), integration.get("id", ""), "requires")
    for risk in old.get("risks", []):
        if isinstance(risk, dict):
            for target in values(risk.get("mitigation_ids")):
                edge(risk.get("id", ""), target, "mitigated_by")
            for target in values(risk.get("test_ids")):
                edge(risk.get("id", ""), target, "verified_by")
    for artifact in output["artifacts"]:
        for source in values(artifact.get("source_ids")):
            edge(source, artifact["id"], "documented_by")

    for tree, group in {"integration": "integrations", "risk": "risks"}.items():
        if not output[group]:
            output["project"].setdefault("not_applicable_trees", {})[tree] = "No imported active node; confirm applicability during reconciliation."
    output["change_requests"].append({
        "id": "CR-MIGRATION-001", "reason": "Reconcile imported v1 planning model into v2 graph.",
        "approval_required": True, "propagation_status": "pending", "lifecycle": "active", "confidence": "unverified",
    })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely migrate a Project Planner v1 JSON model to v2.")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        old = json.loads(args.source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Cannot read source model: {error}", file=sys.stderr)
        return 2
    if str(old.get("project", {}).get("model_version", "")).startswith("2."):
        print("Source already declares model v2; refusing to overwrite it.", file=sys.stderr)
        return 2
    migrated = migrate(old, f"file:{args.source.name}")
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    all_ids = [
        node["id"]
        for group in ("evidence", "instructions", "decisions", "research", "capabilities", "requirements", "work_items", "delivery_nodes", "integrations", "risks", "change_requests", "artifacts", "unknowns")
        for node in migrated.get(group, [])
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    ]
    old_project = old.get("project", {}) if isinstance(old.get("project"), dict) else {}
    common = {
        "timestamp": timestamp,
        "actor": "project_planner_migration",
        "action": "migrate_v1_to_v2_1",
        "model_version_before": str(old_project.get("model_version", "v1")),
        "model_version_after": "2.1.0",
        "project_revision_before": 0,
        "project_revision_after": 1,
    }
    append_jsonl(args.destination.parent / "decisions.jsonl", {**common, "id": "EV-MIGRATION-DEC-001", "affected_ids": all_ids})
    append_jsonl(args.destination.parent / "research-ledger.jsonl", {**common, "id": "EV-MIGRATION-RES-001", "affected_ids": [node_id for node_id in all_ids if node_id.startswith(("E-", "R-", "U-"))]})
    append_jsonl(args.destination.parent / "change-requests.jsonl", {**common, "id": "EV-MIGRATION-CR-001", "affected_ids": ["CR-MIGRATION-001"]})
    print(f"Migrated safely to {args.destination}. Review all imported claims before use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
