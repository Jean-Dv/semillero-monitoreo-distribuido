#!/usr/bin/env python3
"""Validate the frozen cohort and assign splits/phases without label leakage."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "config" / "partition_manifest_v1.json"
FEATURES_PATH = ROOT / "data" / "features_v1.csv"
REFERENCES_PATH = ROOT / "data" / "evaluation_reference_v1.csv"
ASSIGNMENTS_PATH = ROOT / "reports" / "window_assignments_v1.csv"
REPORT_PATH = ROOT / "reports" / "dataset_validation_v1.json"


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace(" ", "T"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header in {path}")
        return reader.fieldnames, list(reader)


def split_by_run(manifest: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for split, run_ids in manifest["splits"].items():
        for run_id in run_ids:
            if run_id in result:
                raise ValueError(f"run_id assigned twice: {run_id}")
            result[run_id] = split
    return result


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    feature_columns, features = read_rows(FEATURES_PATH)
    _, references = read_rows(REFERENCES_PATH)
    run_splits = split_by_run(manifest)
    forbidden = set(manifest["leakage_policy"]["forbidden_feature_columns"])
    leaked = sorted(forbidden.intersection(feature_columns))
    if leaked:
        raise ValueError(f"Label leakage in feature export: {leaked}")

    expected_runs = set(run_splits)
    observed_runs = {row["run_id"] for row in features}
    if observed_runs != expected_runs:
        raise ValueError(
            f"Unexpected run IDs: expected={sorted(expected_runs)} observed={sorted(observed_runs)}"
        )
    expected_services = set(manifest["services"])
    observed_services = {row["service_name"] for row in features}
    if observed_services != expected_services:
        raise ValueError(
            "Unexpected services: "
            f"expected={sorted(expected_services)} observed={sorted(observed_services)}"
        )
    namespaces = {row["k8s_namespace"] for row in features}
    if namespaces != {manifest["namespace"]}:
        raise ValueError(f"Unexpected namespaces: {sorted(namespaces)}")
    contracts = {row["gold_contract_version"] for row in features}
    if contracts != {manifest["gold_contract_version"]}:
        raise ValueError(f"Unexpected Gold contracts: {sorted(contracts)}")

    feature_ids = [row["feature_id"] for row in features]
    logical_keys = [
        (
            row["run_id"],
            row["window_start"],
            row["service_name"],
            row["service_namespace"],
            row["k8s_namespace"],
        )
        for row in features
    ]
    if len(feature_ids) != len(set(feature_ids)):
        raise ValueError("Duplicate feature_id values")
    if len(logical_keys) != len(set(logical_keys)):
        raise ValueError("Duplicate logical keys")

    references_by_run: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for reference in references:
        run_id = reference["run_id"]
        if run_id not in expected_runs:
            raise ValueError(f"Unexpected reference run_id: {run_id}")
        references_by_run[run_id].append(
            {
                **reference,
                "start": parse_time(reference["window_start"]),
                "end": parse_time(reference["window_end"]),
            }
        )

    assignment_fields = [
        "feature_id",
        "run_id",
        "split",
        "window_start",
        "window_end",
        "service_name",
        "condition",
        "fault_type",
        "affected_component",
        "phase_membership",
        "analysis_scope",
        "system_fault_label",
        "affected_service_label",
        "late_event_count",
    ]
    counts: Counter[tuple[str, str, str]] = Counter()
    late_events: Counter[tuple[str, str]] = Counter()
    ASSIGNMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ASSIGNMENTS_PATH.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=assignment_fields)
        writer.writeheader()
        for feature in features:
            start = parse_time(feature["window_start"])
            end = parse_time(feature["window_end"])
            refs = references_by_run[feature["run_id"]]
            contained = [ref for ref in refs if start >= ref["start"] and end <= ref["end"]]
            overlapping = [ref for ref in refs if start < ref["end"] and end > ref["start"]]
            if len(contained) == 1:
                reference = contained[0]
                membership = "pure"
                condition = reference["condition"]
                fault_type = reference["fault_type"]
                affected_component = reference["affected_component"]
            elif not overlapping:
                membership = "outside"
                condition = ""
                fault_type = ""
                affected_component = ""
            else:
                membership = "boundary"
                condition = ""
                fault_type = ""
                affected_component = ""

            if membership != "pure":
                scope = "excluded_boundary_or_outside"
            elif condition in manifest["phase_policy"]["primary_evaluation_conditions"]:
                scope = "primary"
            elif condition in manifest["phase_policy"]["secondary_conditions"]:
                scope = "secondary"
            else:
                scope = "excluded"

            system_label = "1" if membership == "pure" and condition == "fault" else "0"
            if membership == "pure" and condition == "normal":
                affected_label = "0"
            elif (
                membership == "pure"
                and condition == "fault"
                and feature["service_name"] == affected_component
            ):
                affected_label = "1"
            else:
                affected_label = ""

            split = run_splits[feature["run_id"]]
            counts[(split, membership, condition or "unassigned")] += 1
            late_count = int(feature["late_event_count"] or "0")
            late_events[(split, condition or membership)] += late_count
            writer.writerow(
                {
                    "feature_id": feature["feature_id"],
                    "run_id": feature["run_id"],
                    "split": split,
                    "window_start": feature["window_start"],
                    "window_end": feature["window_end"],
                    "service_name": feature["service_name"],
                    "condition": condition,
                    "fault_type": fault_type,
                    "affected_component": affected_component,
                    "phase_membership": membership,
                    "analysis_scope": scope,
                    "system_fault_label": system_label,
                    "affected_service_label": affected_label,
                    "late_event_count": late_count,
                }
            )

    report = {
        "validation_version": "dataset_validation_v1",
        "manifest_sha256": sha256(MANIFEST_PATH),
        "features_sha256": sha256(FEATURES_PATH),
        "evaluation_reference_sha256": sha256(REFERENCES_PATH),
        "assignments_sha256": sha256(ASSIGNMENTS_PATH),
        "feature_rows": len(features),
        "unique_feature_ids": len(set(feature_ids)),
        "unique_logical_keys": len(set(logical_keys)),
        "feature_columns": feature_columns,
        "label_leakage_columns": leaked,
        "counts_by_split_membership_condition": [
            {
                "split": split,
                "phase_membership": membership,
                "condition": condition,
                "rows": rows,
            }
            for (split, membership, condition), rows in sorted(counts.items())
        ],
        "late_events_by_split_condition": [
            {"split": split, "condition": condition, "late_events": count}
            for (split, condition), count in sorted(late_events.items())
            if count
        ],
        "checks": {
            "expected_runs_only": True,
            "expected_services_only": True,
            "namespace_exact": True,
            "gold_contract_exact": True,
            "feature_ids_unique": True,
            "logical_keys_unique": True,
            "labels_separate_from_features": True,
        },
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
