#!/usr/bin/env python3
"""Regression checks for the project-planner validator's high-risk guarantees."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from validate_project_model import validate, validation_fingerprint


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "references" / "project-context.template.json"
SCHEMA = ROOT / "references" / "project-context.schema.json"


def write_event(path: Path, event_id: str, affected_ids: list[str]) -> None:
    event = {
        "id": event_id,
        "timestamp": "2026-07-21T00:00:00Z",
        "actor": "validator_test",
        "action": "initialize_project",
        "model_version_before": None,
        "model_version_after": "2.1.0",
        "project_revision_before": None,
        "project_revision_after": 1,
        "affected_ids": affected_ids,
    }
    path.write_text(json.dumps(event) + "\n", encoding="utf-8")


def codes(report: dict) -> set[str]:
    return {entry["code"] for entry in report["issues"]}


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        planning = Path(temporary) / "planning"
        planning.mkdir()
        model_path = planning / "project-context.json"
        model = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        write_event(planning / "decisions.jsonl", "EV-DEC-001", ["D-001"])
        write_event(planning / "research-ledger.jsonl", "EV-RES-001", ["R-001"])
        (planning / "change-requests.jsonl").write_text("", encoding="utf-8")

        report = validate(model, model_path, SCHEMA)
        unexpected_p0 = [entry for entry in report["issues"] if entry["severity"] == "P0"]
        assert not unexpected_p0, unexpected_p0

        # The validation receipt must remain stable when it is stored in a manifest.
        artifact = model["artifacts"][0]
        artifact["validation_run"] = f"VAL-{validation_fingerprint(model)}"
        assert artifact["validation_run"] == f"VAL-{validation_fingerprint(model)}"

        # A missing local asset must fail even if its Markdown parent exists.
        artifact.update({"lifecycle": "complete", "path": "deliverables/brief.md"})
        deliverable = planning / artifact["path"]
        deliverable.parent.mkdir()
        source_ids = ", ".join(f'"{item}"' for item in artifact["source_ids"])
        content = (
            "> Artifact ID: `ART-001`\n"
            "> Project Model: `2.1.0`\n"
            f"> Source IDs: [{source_ids}]\n"
            "> Archetype / Mode: `software_product` / `prototype_mock`\n"
            "> Lifecycle / Confidence: `complete` / `assumed`\n\n"
            "![Missing preview](images/not-present.png)\n"
        )
        deliverable.write_text(content, encoding="utf-8")
        artifact["content_hash"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
        artifact["validation_run"] = f"VAL-{validation_fingerprint(model)}"
        asset_report = validate(model, model_path, SCHEMA)
        assert "MISSING_LOCAL_ASSET_LINK" in codes(asset_report), asset_report["issues"]

        # Migration must create v2.1 event-log receipts beside its destination.
        legacy_path = Path(temporary) / "legacy-v1.json"
        legacy_path.write_text(json.dumps({"project": {"id": "legacy-project", "name": "Legacy", "model_version": "1.0.0"}}), encoding="utf-8")
        migrated_path = Path(temporary) / "migrated" / "project-context.json"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "migrate_project_model.py"), str(legacy_path), str(migrated_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert result.returncode == 0, result.stderr
        migrated = json.loads(migrated_path.read_text(encoding="utf-8"))
        assert migrated["project"]["model_version"] == "2.1.0"
        assert migrated["project"]["revision"] == 1
        for filename in ("decisions.jsonl", "research-ledger.jsonl", "change-requests.jsonl"):
            event = json.loads((migrated_path.parent / filename).read_text(encoding="utf-8").strip())
            assert event["project_revision_after"] == 1

    print("Validator regression checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
