#!/usr/bin/env python3
"""Validate Project Planner canonical model v2 and its derived artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_GROUPS = (
    "evidence", "instructions", "decisions", "research", "capabilities", "requirements",
    "work_items", "delivery_nodes", "integrations", "risks", "change_requests",
    "artifacts", "edges", "unknowns",
)
NODE_GROUPS = tuple(group for group in ROOT_GROUPS if group != "edges")
ACTIVE = "active"
OPEN_CONFIDENCE = {"assumed", "unverified", "blocked", "conflicting", "research_incomplete"}
TRUSTED_EVIDENCE_KINDS = {"user_statement", "user_document", "official_source", "primary_research"}
PRODUCTION_EVIDENCE_KINDS = {"user_document", "official_source", "primary_research", "internal_record"}
SECRET_KEYS = {
    "api_key", "apikey", "access_token", "token", "password", "private_key",
    "client_secret", "secret", "bearer_token", "authorization", "auth_header",
    "webhook_secret", "signing_key",
}
PII_KEYS = {"email", "phone", "phone_number", "national_id", "nik", "passport_number", "address"}
SECRET_QUERY = re.compile(r"[?&](?:api[_-]?key|access[_-]?token|token|secret|password)=", re.I)
POLICY_ARTIFACTS = {
    "identity_access": {"role_matrix", "access_policy", "recovery_abuse_plan"},
    "money_movement": {"financial_lifecycle", "reconciliation_plan"},
    "limited_inventory": {"state_model", "concurrency_test"},
    "external_partner": {"integration_readiness", "fallback_runbook"},
    "real_time": {"realtime_consistency_policy", "recovery_playbook"},
    "service_experience": {"channel_decision", "service_blueprint", "interaction_spec", "accessibility_spec", "usability_test_plan"},
    "offline_sync": {"sync_conflict_policy", "recovery_playbook"},
    "sensitive_data": {"data_governance", "access_policy"},
    "regulated": {"regulatory_boundary", "review_record"},
    "data_ai": {"data_model_governance", "evaluation_plan"},
    "migration": {"migration_plan", "rollback_plan"},
    "physical_safety": {"safety_procedure", "contingency_plan"},
}
BASELINE_COMPLETE_ARTIFACTS = {
    "project_brief", "decision_register", "risk_unknown_register",
    "planner_execution_report", "synchronization_report", "tree_coverage_report",
}
LOCAL_MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
EVENT_LOGS = {
    "decisions.jsonl": "decision",
    "research-ledger.jsonl": "research",
    "change-requests.jsonl": "change_request",
}


def issue(report: dict[str, Any], severity: str, code: str, message: str, node_id: str | None = None) -> None:
    report["issues"].append({"severity": severity, "code": code, "message": message, "node_id": node_id})


def values(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def active(node: dict[str, Any]) -> bool:
    return node.get("lifecycle") == ACTIVE


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validation_fingerprint(model: dict[str, Any]) -> str:
    """Hash a stable validation snapshot without self-referential run receipts."""
    snapshot = json.loads(json.dumps(model, ensure_ascii=False))
    for artifact in snapshot.get("artifacts", []):
        if isinstance(artifact, dict):
            artifact.pop("validation_run", None)
    return sha256_bytes(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8"))[:12]


def is_v21_or_newer(model: dict[str, Any]) -> bool:
    version = str(model.get("project", {}).get("model_version", ""))
    match = re.match(r"^2\.(\d+)\.", version)
    return bool(match and int(match.group(1)) >= 1)


def scan_sensitive(value: Any, path: str = "") -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{path}.{key}" if path else key
            normalized = key.lower().replace("-", "_")
            if normalized in SECRET_KEYS and child not in (None, ""):
                findings.append(("INLINE_SECRET", current))
            if normalized in PII_KEYS and child not in (None, "", "[redacted]"):
                findings.append(("POSSIBLE_PII_LITERAL", current))
            if normalized in {"url", "endpoint", "base_url"} and isinstance(child, str) and SECRET_QUERY.search(child):
                findings.append(("INLINE_SECRET", current))
            findings.extend(scan_sensitive(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(scan_sensitive(child, f"{path}[{index}]"))
    return findings


def schema_validate(model: dict[str, Any], schema_path: Path, report: dict[str, Any]) -> None:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        issue(report, "P0", "SCHEMA_ENGINE_UNAVAILABLE", "jsonschema is required; validation assurance is unavailable.")
        return
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        issue(report, "P0", "SCHEMA_UNAVAILABLE", f"Cannot load schema: {error}")
        return
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(model), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "root"
        issue(report, "P0", "SCHEMA_INVALID", f"{location}: {error.message}")


def audit_event_logs(
    model: dict[str, Any], model_path: Path, known_ids: set[str], report: dict[str, Any]
) -> dict[str, Any]:
    """Check event-log existence and the minimum receipt needed for reconciliation."""
    planning_dir = model_path.parent
    project = model.get("project", {})
    require_revision = is_v21_or_newer(model)
    expected_revision = project.get("revision")
    if require_revision and not isinstance(expected_revision, int):
        issue(report, "P0", "MISSING_PROJECT_REVISION", "Model v2.1+ needs project.revision as an integer.")

    seen_ids: set[str] = set()
    affected_ids: set[str] = set()
    summaries: dict[str, Any] = {}
    for filename, group in EVENT_LOGS.items():
        path = planning_dir / filename
        entry_count = 0
        invalid_count = 0
        if not path.is_file():
            issue(report, "P0", "EVENT_LOG_MISSING", f"Required event log is missing: {filename}")
            summaries[filename] = {"status": "missing", "entries": 0}
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as error:
            issue(report, "P0", "EVENT_LOG_UNREADABLE", f"Cannot read {filename}: {error}")
            summaries[filename] = {"status": "unreadable", "entries": 0}
            continue
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            entry_count += 1
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                invalid_count += 1
                issue(report, "P0", "EVENT_LOG_INVALID_JSON", f"{filename}:{line_number}: {error.msg}")
                continue
            if not isinstance(event, dict):
                invalid_count += 1
                issue(report, "P0", "EVENT_LOG_INVALID_ENTRY", f"{filename}:{line_number} is not an object.")
                continue
            event_id = event.get("id")
            if not isinstance(event_id, str) or not event_id:
                invalid_count += 1
                issue(report, "P0", "EVENT_LOG_MISSING_ID", f"{filename}:{line_number} has no event ID.")
            elif event_id in seen_ids:
                invalid_count += 1
                issue(report, "P0", "EVENT_LOG_DUPLICATE_ID", f"Event ID '{event_id}' is duplicated.")
            else:
                seen_ids.add(event_id)
            for field in ("timestamp", "actor", "action", "model_version_before", "model_version_after", "affected_ids"):
                if field not in event:
                    invalid_count += 1
                    issue(report, "P0", "EVENT_LOG_MISSING_FIELD", f"{filename}:{line_number} lacks {field}.")
            timestamp = event.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    invalid_count += 1
                    issue(report, "P0", "EVENT_LOG_INVALID_TIMESTAMP", f"{filename}:{line_number} has invalid timestamp.")
            if require_revision:
                for field in ("project_revision_before", "project_revision_after"):
                    if field not in event:
                        invalid_count += 1
                        issue(report, "P0", "EVENT_LOG_MISSING_REVISION", f"{filename}:{line_number} lacks {field} for model v2.1+.")
            event_affected = values(event.get("affected_ids"))
            if event.get("affected_ids") is not None and not isinstance(event.get("affected_ids"), list):
                invalid_count += 1
                issue(report, "P0", "EVENT_LOG_INVALID_AFFECTED_IDS", f"{filename}:{line_number} affected_ids must be an array.")
            for affected_id in event_affected:
                affected_ids.add(affected_id)
                if affected_id not in known_ids:
                    issue(report, "P1", "EVENT_LOG_UNKNOWN_AFFECTED_ID", f"{filename}:{line_number} references missing current node '{affected_id}'.", affected_id)
        summaries[filename] = {"status": "pass" if not invalid_count else "gap", "entries": entry_count, "invalid_entries": invalid_count, "group": group}

    for change in model.get("change_requests", []):
        if isinstance(change, dict) and active(change) and change.get("id") not in affected_ids:
            issue(report, "P0", "CHANGE_WITHOUT_EVENT_RECEIPT", f"Active change request '{change.get('id')}' is absent from change logs.", change.get("id"))

    # Rule #11 enforcement: every active decision must have an event in decisions.jsonl,
    # and every active research must have an event in research-ledger.jsonl.
    decision_log_summary = summaries.get("decisions.jsonl", {})
    if decision_log_summary.get("status") != "missing":
        for decision in model.get("decisions", []):
            if isinstance(decision, dict) and active(decision) and decision.get("id") not in affected_ids:
                issue(report, "P1", "DECISION_WITHOUT_EVENT", f"Active decision '{decision.get('id')}' has no corresponding event in decisions.jsonl.", decision.get("id"))

    research_log_summary = summaries.get("research-ledger.jsonl", {})
    if research_log_summary.get("status") != "missing":
        for research in model.get("research", []):
            if isinstance(research, dict) and active(research) and research.get("id") not in affected_ids:
                issue(report, "P1", "RESEARCH_WITHOUT_EVENT", f"Active research '{research.get('id')}' has no corresponding event in research-ledger.jsonl.", research.get("id"))

    return {"logs": summaries, "known_event_ids": len(seen_ids), "affected_node_ids": sorted(affected_ids)}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(model: dict[str, Any], model_path: Path, schema_path: Path) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    report: dict[str, Any] = {
        "report_type": "project_planner_v2_validation",
        "validation_run": f"VAL-{validation_fingerprint(model)}",
        "validated_at": now,
        "model_version": model.get("project", {}).get("model_version"),
        "issues": [],
    }
    schema_validate(model, schema_path, report)

    project = model.get("project")
    if not isinstance(project, dict):
        issue(report, "P0", "MISSING_PROJECT", "Root object 'project' is required.")
        return report

    for key in ROOT_GROUPS:
        if not isinstance(model.get(key), list):
            issue(report, "P0", "MISSING_GROUP", f"Root list '{key}' is required.")

    nodes: dict[str, dict[str, Any]] = {}
    groups_by_id: dict[str, str] = {}
    for group in NODE_GROUPS:
        for node in model.get(group, []):
            if not isinstance(node, dict):
                issue(report, "P0", "INVALID_NODE", f"{group} contains a non-object node.")
                continue
            node_id = node.get("id")
            if not isinstance(node_id, str) or not node_id:
                issue(report, "P0", "MISSING_ID", f"A node in {group} has no stable ID.")
                continue
            if node_id in nodes:
                issue(report, "P0", "DUPLICATE_ID", f"ID '{node_id}' is duplicated.", node_id)
                continue
            nodes[node_id] = node
            groups_by_id[node_id] = group
            confidence = node.get("confidence")
            lifecycle = node.get("lifecycle")
            if confidence == "confirmed" and group != "evidence" and not values(node.get("evidence_ids")):
                issue(report, "P0", "CONFIRMED_WITHOUT_EVIDENCE", f"Confirmed {group} '{node_id}' has no evidence IDs.", node_id)
            if confidence == "blocked" and not node.get("next_action"):
                issue(report, "P0", "BLOCKED_WITHOUT_ACTION", f"Blocked node '{node_id}' needs next_action.", node_id)
            if lifecycle == "deferred" and not node.get("target_release"):
                issue(report, "P1", "DEFERRED_WITHOUT_TARGET", f"Deferred node '{node_id}' needs target_release.", node_id)
            if lifecycle == "superseded" and not node.get("superseded_by"):
                issue(report, "P1", "SUPERSEDED_WITHOUT_TARGET", f"Superseded node '{node_id}' needs superseded_by.", node_id)

    for kind, path in scan_sensitive(model):
        severity = "P0" if kind == "INLINE_SECRET" else "P1"
        issue(report, severity, kind, f"Potential sensitive literal at '{path}'. Store only a non-secret reference.")

    evidence_by_id = {
        node.get("id"): node for node in model.get("evidence", [])
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }
    evidence_ids = set(evidence_by_id)
    for evidence_id, evidence in evidence_by_id.items():
        review_after = evidence.get("review_after")
        if not review_after:
            continue
        try:
            review_time = datetime.fromisoformat(str(review_after).replace("Z", "+00:00"))
            if review_time <= datetime.now(timezone.utc):
                issue(report, "P1", "STALE_EVIDENCE", f"Evidence '{evidence_id}' has passed its review date.", evidence_id)
        except ValueError:
            issue(report, "P1", "INVALID_EVIDENCE_REVIEW_DATE", f"Evidence '{evidence_id}' has an invalid review_after value.", evidence_id)
    for node_id, node in nodes.items():
        node_evidence_ids = values(node.get("evidence_ids"))
        for evidence_id in node_evidence_ids:
            if evidence_id not in evidence_ids:
                issue(report, "P0", "BROKEN_EVIDENCE_REFERENCE", f"Node '{node_id}' references missing evidence '{evidence_id}'.", node_id)
        if node.get("confidence") == "confirmed" and groups_by_id[node_id] != "evidence":
            trusted = [
                evidence_by_id[evidence_id] for evidence_id in node_evidence_ids
                if evidence_id in evidence_by_id and evidence_by_id[evidence_id].get("kind") in TRUSTED_EVIDENCE_KINDS
                and evidence_by_id[evidence_id].get("confidence") == "confirmed"
            ]
            if not trusted:
                issue(report, "P0", "CONFIRMED_WITH_UNTRUSTED_EVIDENCE", f"Confirmed node '{node_id}' has no trusted confirmed evidence.", node_id)

    edges = [edge for edge in model.get("edges", []) if isinstance(edge, dict)]
    relation_contracts: dict[str, tuple[set[str], set[str]]] = {
        "informs": ({"instructions", "decisions", "research", "evidence"}, {"requirements", "decisions", "capabilities", "work_items", "risks"}),
        "decides": ({"decisions"}, {"requirements", "work_items", "delivery_nodes", "integrations", "risks", "artifacts"}),
        "constrains": ({"instructions", "decisions", "research", "risks"}, {"requirements", "work_items", "delivery_nodes", "integrations", "artifacts"}),
        "implemented_by": ({"requirements"}, {"work_items"}),
        "delivers": ({"work_items"}, {"delivery_nodes"}),
        "requires": ({"capabilities"}, {"work_items", "delivery_nodes", "integrations", "artifacts"}),
        "mitigated_by": ({"risks"}, {"decisions", "work_items", "delivery_nodes", "artifacts"}),
        "verified_by": ({"requirements", "work_items", "risks", "integrations"}, {"delivery_nodes"}),
        "documented_by": ({"instructions", "decisions", "requirements", "work_items", "risks", "capabilities", "change_requests"}, {"artifacts"}),
        "impacts": ({"decisions", "change_requests"}, set(NODE_GROUPS)),
        "supersedes": (set(NODE_GROUPS), set(NODE_GROUPS)),
        "evidences": ({"evidence"}, set(NODE_GROUPS) - {"evidence"}),
    }
    edge_ids: set[str] = set()
    edge_signatures: set[tuple[str, str, str]] = set()
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id:
            issue(report, "P0", "EDGE_WITHOUT_ID", "Every edge needs an ID.")
            continue
        if edge_id in edge_ids or edge_id in nodes:
            issue(report, "P0", "DUPLICATE_ID", f"Edge ID '{edge_id}' is duplicated.", edge_id)
            continue
        edge_ids.add(edge_id)
        source, target = edge.get("from_id"), edge.get("to_id")
        if source not in nodes or target not in nodes:
            issue(report, "P0", "BROKEN_EDGE", f"Edge '{edge_id}' references '{source}' -> '{target}', which is not a node.", edge_id)
            continue
        contract = relation_contracts.get(edge.get("relation"))
        if contract:
            allowed_sources, allowed_targets = contract
            if groups_by_id[source] not in allowed_sources or groups_by_id[target] not in allowed_targets:
                issue(
                    report,
                    "P0",
                    "INVALID_EDGE_RELATION",
                    f"Edge '{edge_id}' uses '{edge.get('relation')}' from {groups_by_id[source]} to {groups_by_id[target]}, which violates the typed relation contract.",
                    edge_id,
                )
        sig = (source, target, edge.get("relation", ""))
        if sig in edge_signatures:
            issue(report, "P1", "DUPLICATE_EDGE_CONTENT", f"Edge '{edge_id}' is a semantic duplicate ({source} -{sig[2]}-> {target}).", edge_id)
        edge_signatures.add(sig)
        outgoing[source].append(edge)
        incoming[target].append(edge)

    def has_out(node_id: str, relations: set[str] | None = None) -> bool:
        return any(edge.get("relation") in relations for edge in outgoing[node_id]) if relations else bool(outgoing[node_id])

    def has_in(node_id: str, relations: set[str] | None = None) -> bool:
        return any(edge.get("relation") in relations for edge in incoming[node_id]) if relations else bool(incoming[node_id])

    def active_nodes(group: str) -> list[dict[str, Any]]:
        return [node for node in model.get(group, []) if isinstance(node, dict) and active(node)]

    for node_id, node in nodes.items():
        if node.get("lifecycle") == "superseded" and not has_out(node_id, {"supersedes"}):
            issue(report, "P1", "SUPERSEDED_WITHOUT_EDGE", f"Superseded node '{node_id}' lacks a supersedes edge.", node_id)

    event_log = audit_event_logs(model, model_path, set(nodes), report)

    # Integration access and waiver semantics.
    for integration in active_nodes("integrations"):
        node_id = integration.get("id", "<unknown>")
        access = integration.get("access_status")
        delivery = integration.get("delivery_mode")
        if access == "production_confirmed" and not values(integration.get("evidence_ids")):
            issue(report, "P0", "UNPROVEN_PRODUCTION_ACCESS", f"Integration '{node_id}' claims production access without evidence.", node_id)
        if access == "production_confirmed" and not any(
            evidence_id in evidence_by_id and evidence_by_id[evidence_id].get("kind") in PRODUCTION_EVIDENCE_KINDS
            and evidence_by_id[evidence_id].get("confidence") == "confirmed"
            for evidence_id in values(integration.get("evidence_ids"))
        ):
            issue(report, "P0", "UNTRUSTED_PRODUCTION_ACCESS", f"Integration '{node_id}' lacks trusted production-access evidence.", node_id)
        if access in {"claimed_unverified", "unknown", "unavailable", "sandbox_only"} and delivery == "production":
            issue(report, "P0", "UNVERIFIED_PRODUCTION_INTEGRATION", f"Integration '{node_id}' has non-production access but production delivery.", node_id)
        if access in {"claimed_unverified", "unknown", "unavailable", "sandbox_only"} and not integration.get("fallback"):
            issue(report, "P0", "INTEGRATION_WITHOUT_FALLBACK", f"Integration '{node_id}' needs a fallback.", node_id)

    for risk in active_nodes("risks"):
        waiver = risk.get("waiver")
        if not isinstance(waiver, dict):
            continue
        node_id = risk.get("id", "<unknown>")
        if risk.get("severity") == "P0" or risk.get("criticality") == "critical":
            issue(report, "P0", "ILLEGAL_WAIVER", f"Risk '{node_id}' is P0/critical and cannot be waived by the planner.", node_id)
        for field in ("approved_by", "approved_at", "expires_at", "reason", "compensating_control"):
            if not waiver.get(field):
                issue(report, "P0", "INCOMPLETE_WAIVER", f"Risk '{node_id}' waiver lacks {field}.", node_id)
        if not values(waiver.get("evidence_ids")):
            issue(report, "P0", "INCOMPLETE_WAIVER", f"Risk '{node_id}' waiver lacks evidence.", node_id)
        try:
            expiry = datetime.fromisoformat(str(waiver.get("expires_at", "")).replace("Z", "+00:00"))
            if expiry <= datetime.now(timezone.utc):
                issue(report, "P0", "EXPIRED_WAIVER", f"Risk '{node_id}' waiver has expired.", node_id)
        except ValueError:
            issue(report, "P0", "INVALID_WAIVER_EXPIRY", f"Risk '{node_id}' waiver expiry is invalid.", node_id)

    # A declared capability always creates a planning obligation. Draft mode may
    # defer a file, but it must not silently erase the policy candidate.
    required_by_policy: dict[str, set[str]] = defaultdict(set)
    custom_delivery_requirements: dict[str, set[str]] = {}
    for capability in active_nodes("capabilities"):
        node_id = capability.get("id", "<unknown>")
        if not has_out(node_id, {"requires"}):
            issue(report, "P0", "CAPABILITY_WITHOUT_REQUIRE_EDGE", f"Capability '{node_id}' has no downstream requires edge.", node_id)
        keys = values(capability.get("policy_ids"))
        if not keys:
            issue(report, "P0", "CAPABILITY_WITHOUT_POLICY", f"Capability '{node_id}' has no policy IDs.", node_id)
            continue
        for policy_id in keys:
            if policy_id == "custom":
                custom_policy = capability.get("custom_policy")
                if not isinstance(custom_policy, dict):
                    issue(report, "P0", "CUSTOM_POLICY_UNDEFINED", f"Capability '{node_id}' uses custom policy without a contract.", node_id)
                    continue
                policy_artifacts = set(values(custom_policy.get("required_artifact_types")))
                custom_delivery_requirements[node_id] = set(values(custom_policy.get("required_delivery_categories")))
            else:
                if policy_id not in POLICY_ARTIFACTS:
                    issue(report, "P1", "UNKNOWN_POLICY", f"Capability '{node_id}' uses unknown policy '{policy_id}'.", node_id)
                policy_artifacts = POLICY_ARTIFACTS.get(policy_id, set())
            required_by_policy[policy_id].update(policy_artifacts)

    artifacts = [artifact for artifact in model.get("artifacts", []) if isinstance(artifact, dict)]
    artifacts_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for artifact in artifacts:
        artifact_type = artifact.get("artifact_type")
        if isinstance(artifact_type, str):
            artifacts_by_type[artifact_type].append(artifact)
        if artifact.get("disposition") == "skip" and not artifact.get("revisit_condition"):
            issue(report, "P1", "SKIPPED_ARTIFACT_WITHOUT_REVISIT", f"Skipped artifact '{artifact.get('id')}' needs a condition that makes it required later.", artifact.get("id"))

    policy_coverage: dict[str, Any] = {"required": {}, "baseline": {}}
    for policy_id, policy_artifacts in sorted(required_by_policy.items()):
        entries: dict[str, str] = {}
        for artifact_type in sorted(policy_artifacts):
            candidates = artifacts_by_type.get(artifact_type, [])
            if not candidates:
                issue(report, "P0", "POLICY_ARTIFACT_UNMODELED", f"Policy '{policy_id}' requires candidate artifact type '{artifact_type}', but no include/skip node exists.")
                entries[artifact_type] = "unmodeled"
            elif any(candidate.get("disposition") == "include" for candidate in candidates):
                entries[artifact_type] = "include"
            else:
                entries[artifact_type] = "skip"
        policy_coverage["required"][policy_id] = entries

    for artifact_type in sorted(BASELINE_COMPLETE_ARTIFACTS):
        candidates = artifacts_by_type.get(artifact_type, [])
        if not candidates:
            issue(report, "P0", "BASELINE_ARTIFACT_UNMODELED", f"Every package needs artifact node '{artifact_type}', even while it is draft.")
            policy_coverage["baseline"][artifact_type] = "unmodeled"
        elif any(candidate.get("disposition") == "include" for candidate in candidates):
            policy_coverage["baseline"][artifact_type] = "include"
        else:
            issue(report, "P0", "BASELINE_ARTIFACT_SKIPPED", f"Baseline artifact '{artifact_type}' cannot be skipped.")
            policy_coverage["baseline"][artifact_type] = "skip"

    experience_profiles = {"user_facing", "mobile_app", "web_app", "pos", "service_experience"}
    if any(work.get("delivery_profile") in experience_profiles for work in active_nodes("work_items")) and not any(
        "service_experience" in values(capability.get("policy_ids")) for capability in active_nodes("capabilities")
    ):
        issue(report, "P1", "USER_FACING_WITHOUT_SERVICE_POLICY", "User-facing work exists without the service_experience capability; channel, recovery, accessibility, and usability artifacts may be silently omitted.")

    # Graph/tree checks.
    tree_gaps: dict[str, list[str]] = defaultdict(list)
    for node in active_nodes("instructions"):
        node_id = node["id"]
        if not has_out(node_id, {"informs", "decides", "constrains"}):
            tree_gaps["instruction"].append(node_id)
            issue(report, "P1", "INSTRUCTION_WITHOUT_TRACE", f"Instruction '{node_id}' has no downstream graph edge.", node_id)
    for node in active_nodes("decisions"):
        node_id = node["id"]
        if not has_out(node_id, {"decides", "constrains", "impacts"}):
            tree_gaps["decision"].append(node_id)
            issue(report, "P1", "DECISION_WITHOUT_IMPACT", f"Decision '{node_id}' has no impact edge.", node_id)
    for node in active_nodes("requirements"):
        node_id = node["id"]
        if not has_in(node_id, {"informs", "decides", "constrains"}) or not has_out(node_id, {"implemented_by"}):
            tree_gaps["requirement"].append(node_id)
            issue(report, "P1", "REQUIREMENT_TRACE_GAP", f"Requirement '{node_id}' lacks origin or implementation edge.", node_id)

    profile_categories = {
        "user_facing": {"flow", "test"},
        "mobile_app": {"flow", "screen", "test"},
        "web_app": {"flow", "screen", "test"},
        "pos": {"flow", "screen", "test"},
        "service_experience": {"flow", "test"},
        "backend": {"test"},
        "data": {"data", "test"},
        "research": {"experiment", "procedure"},
        "operations": {"procedure"},
        "physical": {"physical_output", "procedure"},
        "mixed": {"test"},
    }
    delivery_categories = {node.get("id"): node.get("category") for node in active_nodes("delivery_nodes")}
    for work in active_nodes("work_items"):
        node_id = work["id"]
        delivered = {
            delivery_categories.get(edge.get("to_id"))
            for edge in outgoing[node_id]
            if edge.get("relation") in {"delivers", "verified_by"}
        }
        expected = profile_categories.get(work.get("delivery_profile"), {"test"})
        missing = sorted(expected - delivered)
        if missing:
            tree_gaps["delivery"].append(node_id)
            issue(report, "P0", "DELIVERY_PROFILE_GAP", f"Work item '{node_id}' ({work.get('delivery_profile')}) lacks {', '.join(missing)}.", node_id)
        if not has_in(node_id, {"implemented_by", "constrains", "decides"}):
            tree_gaps["requirement"].append(node_id)
            issue(report, "P1", "WORK_WITHOUT_ORIGIN", f"Work item '{node_id}' has no requirement or decision origin.", node_id)
        if work.get("delivery_profile") == "service_experience" and not ({"surface", "procedure", "physical_output"} & delivered):
            tree_gaps["delivery"].append(node_id)
            issue(report, "P0", "SERVICE_SURFACE_GAP", f"Service work item '{node_id}' needs a surface, procedure, or physical output delivery.", node_id)
        for capability_id, required_categories in custom_delivery_requirements.items():
            if any(edge.get("from_id") == capability_id and edge.get("to_id") == node_id and edge.get("relation") == "requires" for edge in incoming[node_id]):
                missing_custom = sorted(required_categories - delivered)
                if missing_custom:
                    tree_gaps["delivery"].append(node_id)
                    issue(report, "P0", "CUSTOM_POLICY_DELIVERY_GAP", f"Work item '{node_id}' lacks custom-policy delivery categories: {', '.join(missing_custom)}.", node_id)

    for integration in active_nodes("integrations"):
        node_id = integration["id"]
        if not has_in(node_id, {"requires"}):
            tree_gaps["integration"].append(node_id)
            issue(report, "P1", "INTEGRATION_WITHOUT_CAPABILITY_EDGE", f"Integration '{node_id}' lacks capability edge.", node_id)
    for risk in active_nodes("risks"):
        node_id = risk["id"]
        if risk.get("severity") in {"P0", "P1"} and (not has_out(node_id, {"mitigated_by"}) or not has_out(node_id, {"verified_by"})):
            tree_gaps["risk"].append(node_id)
            issue(report, "P0", "RISK_TREE_GAP", f"Risk '{node_id}' needs mitigation and verification edges.", node_id)
    for change in active_nodes("change_requests"):
        node_id = change["id"]
        if not has_out(node_id, {"impacts"}):
            tree_gaps["change_impact"].append(node_id)
            issue(report, "P0", "CHANGE_IMPACT_GAP", f"Change request '{node_id}' has no impact edges.", node_id)

    # Artifact and real-file checks.
    artifact_paths: set[Path] = set()
    asset_link_integrity: dict[str, Any] = {"checked": 0, "missing": [], "outside_workspace": []}
    base_dir = model_path.parent.resolve()
    for artifact in artifacts:
        node_id = artifact.get("id", "<unknown>")
        disposition = artifact.get("disposition")
        for ref in values(artifact.get("source_ids")) + values(artifact.get("trigger_ids")):
            if ref not in nodes:
                issue(report, "P0", "BROKEN_ARTIFACT_REFERENCE", f"Artifact '{node_id}' references missing node '{ref}'.", node_id)
        if artifact.get("model_version") != project.get("model_version"):
            issue(report, "P0", "STALE_ARTIFACT", f"Artifact '{node_id}' has a stale model version.", node_id)
        if disposition == "skip" and artifact.get("path"):
            issue(report, "P1", "SKIPPED_ARTIFACT_HAS_FILE", f"Skipped artifact '{node_id}' should not claim a generated file.", node_id)
        path_value = artifact.get("path")
        if disposition == "include" and isinstance(path_value, str) and path_value:
            art_p = (base_dir / path_value).resolve()
            if base_dir in art_p.parents and art_p != base_dir:
                artifact_paths.add(art_p)

        needs_file = disposition == "include" and artifact.get("lifecycle") in {"validated", "complete"}
        if needs_file:
            if not isinstance(path_value, str) or not path_value:
                issue(report, "P0", "VALIDATED_ARTIFACT_WITHOUT_PATH", f"Artifact '{node_id}' needs a relative path.", node_id)
                continue
            artifact_path = (base_dir / path_value).resolve()
            if base_dir not in artifact_path.parents or artifact_path == base_dir:
                issue(report, "P0", "ARTIFACT_PATH_OUTSIDE_WORKSPACE", f"Artifact '{node_id}' path leaves planning workspace.", node_id)
                continue
            if not artifact_path.is_file():
                issue(report, "P0", "MISSING_ARTIFACT_FILE", f"Artifact '{node_id}' file does not exist: {path_value}", node_id)
                continue
            content = artifact_path.read_bytes()
            if artifact.get("content_hash") != sha256_bytes(content):
                issue(report, "P0", "ARTIFACT_HASH_MISMATCH", f"Artifact '{node_id}' hash does not match file content.", node_id)
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                issue(report, "P1", "ARTIFACT_NOT_UTF8", f"Artifact '{node_id}' cannot be checked for metadata envelope.", node_id)
                continue
            version_marker = f"Project Model: `{project.get('model_version')}`"
            if version_marker not in text:
                issue(report, "P0", "ARTIFACT_METADATA_MISMATCH", f"Artifact '{node_id}' lacks matching project-model metadata.", node_id)
            if is_v21_or_newer(model):
                artifact_marker = f"Artifact ID: `{node_id}`"
                if artifact_marker not in text:
                    issue(report, "P0", "ARTIFACT_ID_METADATA_MISMATCH", f"Artifact '{node_id}' lacks matching Artifact ID metadata.", node_id)
                if artifact.get("validation_run") != report["validation_run"]:
                    issue(report, "P0", "ARTIFACT_VALIDATION_RUN_MISMATCH", f"Artifact '{node_id}' validation run does not match the stable current validation snapshot.", node_id)
                if "> SHA-256:" in text or "> Validation Run:" in text:
                    issue(report, "P1", "SELF_REFERENTIAL_ARTIFACT_METADATA", f"Artifact '{node_id}' stores a hash or validation run in its own content; keep those receipts in the manifest/report.", node_id)
            for source_id in values(artifact.get("source_ids")):
                if source_id not in text:
                    issue(report, "P1", "ARTIFACT_SOURCE_METADATA_GAP", f"Artifact '{node_id}' does not expose source ID '{source_id}'.", node_id)
            for link_match in LOCAL_MARKDOWN_LINK.finditer(text):
                link_value = link_match.group(1).strip()
                if not link_value or link_value.startswith(("#", "http://", "https://", "mailto:", "data:")):
                    continue
                path_part = link_value.split("#", 1)[0].replace("%20", " ")
                if not path_part:
                    continue
                asset_link_integrity["checked"] += 1
                linked_path = (artifact_path.parent / path_part).resolve()
                if base_dir not in linked_path.parents and linked_path != base_dir:
                    asset_link_integrity["outside_workspace"].append(f"{node_id}:{link_value}")
                    issue(report, "P0", "LOCAL_ASSET_LINK_OUTSIDE_WORKSPACE", f"Artifact '{node_id}' link leaves planning workspace: {link_value}", node_id)
                elif not linked_path.exists():
                    asset_link_integrity["missing"].append(f"{node_id}:{link_value}")
                    issue(report, "P0", "MISSING_LOCAL_ASSET_LINK", f"Artifact '{node_id}' references missing local asset/link: {link_value}", node_id)

    if project.get("lifecycle") == "complete" or project.get("operating_mode") == "production":
        for artifact in artifacts:
            if artifact.get("disposition") == "include" and artifact.get("lifecycle") not in {"validated", "complete"}:
                issue(report, "P0", "INCOMPLETE_INCLUDED_ARTIFACT", f"Complete/production project has unfinished artifact '{artifact.get('id')}'.", artifact.get("id"))

    unmodelled_files: list[str] = []
    for artifact_dir_name in ("deliverables", "reports"):
        artifact_dir = base_dir / artifact_dir_name
        if artifact_dir.is_dir():
            for file_path in artifact_dir.rglob("*"):
                if file_path.is_file() and file_path.resolve() not in artifact_paths:
                    unmodelled_files.append(str(file_path.relative_to(base_dir)).replace("\\", "/"))
    for unmodelled_path in unmodelled_files:
        issue(report, "P1", "OUTPUT_WITHOUT_ARTIFACT_NODE", f"Generated file '{unmodelled_path}' has no artifact node.")

    # Orphans and honest tree reporting.
    orphan_ids: list[str] = []
    for group in ("requirements", "work_items", "delivery_nodes", "integrations", "risks", "artifacts"):
        for node in active_nodes(group):
            node_id = node["id"]
            if not incoming[node_id] and not outgoing[node_id]:
                orphan_ids.append(node_id)
                issue(report, "P1", "ORPHAN_NODE", f"Active {group} node '{node_id}' has no graph edge.", node_id)

    na_rationales = project.get("not_applicable_trees") if isinstance(project.get("not_applicable_trees"), dict) else {}
    tree_groups = {
        "instruction": "instructions", "decision": "decisions", "requirement": "requirements",
        "delivery": "work_items", "integration": "integrations", "risk": "risks",
        "change_impact": "change_requests",
    }
    tree_coverage: dict[str, Any] = {}
    for tree_name, group in tree_groups.items():
        total = len(active_nodes(group))
        gaps = sorted(set(tree_gaps[tree_name]))
        if gaps:
            status = "gap"
        elif total:
            status = "pass"
        elif tree_name == "change_impact":
            status = "ready_no_change"
        elif isinstance(na_rationales.get(tree_name), str) and na_rationales[tree_name].strip():
            status = "not_applicable"
        else:
            status = "gap"
            issue(report, "P1", "TREE_NA_WITHOUT_RATIONALE", f"Tree '{tree_name}' is empty without an explicit N/A rationale.")
        tree_coverage[tree_name] = {"total": total, "covered": max(total - len(gaps), 0), "gaps": gaps, "status": status, "na_rationale": na_rationales.get(tree_name)}

    # Production gate is intentionally a hard gate.
    if project.get("operating_mode") == "production":
        gate = project.get("release_gate")
        if not isinstance(gate, dict):
            issue(report, "P0", "PRODUCTION_RELEASE_GATE_MISSING", "Production project needs a verified release gate.")
        else:
            gate_evidence_ids = values(gate.get("evidence_ids"))
            for evidence_id in gate_evidence_ids:
                if evidence_id not in evidence_ids:
                    issue(report, "P0", "PRODUCTION_GATE_EVIDENCE_BROKEN", f"Release gate references missing evidence '{evidence_id}'.")
            if not any(
                evidence_id in evidence_by_id and evidence_by_id[evidence_id].get("kind") in PRODUCTION_EVIDENCE_KINDS
                and evidence_by_id[evidence_id].get("confidence") == "confirmed"
                for evidence_id in gate_evidence_ids
            ):
                issue(report, "P0", "PRODUCTION_GATE_EVIDENCE_UNTRUSTED", "Release gate needs trusted confirmed evidence.")
        for integration in active_nodes("integrations"):
            if integration.get("delivery_mode") != "not_needed" and (
                integration.get("delivery_mode") != "production" or integration.get("access_status") != "production_confirmed"
            ):
                issue(report, "P0", "PRODUCTION_INTEGRATION_NOT_READY", f"Integration '{integration.get('id')}' is not production-confirmed.", integration.get("id"))

    status_counts = Counter(
        f"{groups_by_id[node_id] if groups_by_id[node_id] == 'evidence' else node.get('lifecycle', 'missing')}/{node.get('confidence', 'missing')}"
        for node_id, node in nodes.items()
    )
    p0_issues = [entry for entry in report["issues"] if entry["severity"] == "P0"]
    p1_issues = [entry for entry in report["issues"] if entry["severity"] == "P1"]
    critical_open = [
        node_id for node_id, node in nodes.items()
        if active(node) and node.get("confidence") in OPEN_CONFIDENCE and (
            node.get("criticality") in {"high", "critical"} or node.get("severity") == "P0"
        )
    ]
    production_allowed = (
        project.get("operating_mode") == "production" and not p0_issues and not p1_issues and not critical_open
        and all(tree["status"] in {"pass", "ready_no_change", "not_applicable"} for tree in tree_coverage.values())
    )
    report["planner_execution"] = {
        "status_counts": dict(sorted(status_counts.items())),
        "critical_open_nodes": sorted(critical_open),
        "operating_mode": project.get("operating_mode"),
        "archetype": project.get("archetype"),
        "eligibility": {
            "prototype_mock": "allowed" if not p0_issues else "not_ready",
            "pilot": "allowed" if not p0_issues and not critical_open else "not_ready",
            "production": "allowed" if production_allowed else "not_ready",
        },
    }
    report["synchronization"] = {
        "planned_but_missing": sorted(
            artifact.get("id") for artifact in artifacts
            if artifact.get("disposition") == "include" and artifact.get("lifecycle") in {"validated", "complete"}
            and not artifact.get("path")
        ),
        "output_without_plan": sorted(unmodelled_files),
        "orphan_nodes": sorted(orphan_ids),
        "stale_or_hash_mismatch": sorted({entry.get("node_id") for entry in report["issues"] if entry["code"] in {"STALE_ARTIFACT", "ARTIFACT_HASH_MISMATCH", "ARTIFACT_METADATA_MISMATCH"} and entry.get("node_id")}),
        "decision_violations": sorted({entry.get("node_id") for entry in report["issues"] if "PRODUCTION" in entry["code"] and entry.get("node_id")}),
    }
    report["tree_coverage"] = tree_coverage
    report["policy_coverage"] = policy_coverage
    report["event_log"] = event_log
    report["asset_link_integrity"] = asset_link_integrity
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Project Planner canonical model v2.")
    parser.add_argument("model", type=Path, help="Path to planning/project-context.json")
    parser.add_argument("--schema", type=Path, help="Override schema path")
    parser.add_argument("--report", type=Path, help="Optional combined JSON report path")
    parser.add_argument("--report-dir", type=Path, help="Write the three required control reports here")
    parser.add_argument("--strict", action="store_true", help="Return non-zero for P1 issues as well as P0 issues")
    args = parser.parse_args()

    try:
        model = json.loads(args.model.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Cannot load model: {error}", file=sys.stderr)
        return 2
    schema_path = args.schema or (Path(__file__).resolve().parent.parent / "references" / "project-context.schema.json")
    report = validate(model, args.model.resolve(), schema_path.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    try:
        if args.report:
            write_json(args.report, report)
        if args.report_dir:
            common = {key: report[key] for key in ("report_type", "validation_run", "validated_at", "model_version", "issues")}
            write_json(args.report_dir / "planner-execution-report.json", {**common, "planner_execution": report["planner_execution"], "policy_coverage": report["policy_coverage"], "event_log": report["event_log"]})
            write_json(args.report_dir / "synchronization-report.json", {**common, "synchronization": report["synchronization"], "asset_link_integrity": report["asset_link_integrity"]})
            write_json(args.report_dir / "tree-coverage-report.json", {**common, "tree_coverage": report["tree_coverage"]})
    except OSError as error:
        print(f"Cannot write validation report: {error}", file=sys.stderr)
        return 2
    severities = {entry["severity"] for entry in report["issues"]}
    return 1 if "P0" in severities or (args.strict and severities) else 0


if __name__ == "__main__":
    raise SystemExit(main())
