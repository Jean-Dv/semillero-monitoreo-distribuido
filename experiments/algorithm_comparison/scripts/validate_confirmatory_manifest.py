#!/usr/bin/env python3
"""Validate the frozen blind-comparison manifest and its provenance hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


COMPARISON_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = COMPARISON_ROOT / "config" / "confirmatory_manifest_v1.json"
CHECKSUM_PATH = COMPARISON_ROOT / "config" / "confirmatory_manifest_v1.sha256"
BLIND_PROTOCOL_PATH = REPOSITORY_ROOT.parent / "AIOpsLab" / "deploy" / "etl" / "blind_protocol_v1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_provenance(manifest: dict[str, Any]) -> None:
    for artifact in manifest["development_provenance"]["artifacts"]:
        path = REPOSITORY_ROOT / artifact["path"]
        require(path.is_file(), f"Missing frozen provenance artifact: {path}")
        require(
            sha256(path) == artifact["sha256"],
            f"Provenance hash changed: {artifact['path']}",
        )

    require(
        BLIND_PROTOCOL_PATH.is_file(),
        f"Blind protocol is missing: {BLIND_PROTOCOL_PATH}",
    )
    require(
        sha256(BLIND_PROTOCOL_PATH) == manifest["blind_protocol"]["protocol_sha256"],
        "blind_protocol_v1 no longer matches the confirmatory freeze",
    )


def validate_candidates(manifest: dict[str, Any]) -> None:
    candidates = manifest["candidate_matrix"]
    require(len(candidates) == 10, "Exactly ten frozen variants are required")
    identifiers = [candidate["model_id"] for candidate in candidates]
    require(len(set(identifiers)) == len(identifiers), "Duplicate model_id")
    expected = {
        (family, feature_set)
        for family in (
            "robust_rules",
            "isolation_forest",
            "one_class_svm",
            "hist_gradient_boosting",
            "lstm_temporal_autoencoder",
        )
        for feature_set in ("metrics", "trimodal")
    }
    observed = {
        (candidate["family"], candidate["feature_set"])
        for candidate in candidates
    }
    require(observed == expected, "Candidate family/feature-set matrix changed")
    for candidate in candidates:
        for field in ("system_threshold", "affected_service_threshold"):
            value = float(candidate[field])
            require(0.0 <= value <= 1.0, f"Invalid {field} for {candidate['model_id']}")


def validate_contract(manifest: dict[str, Any]) -> None:
    contract = manifest["data_contract"]
    predictors = set(contract["required_predictor_columns"])
    forbidden = set(contract["forbidden_during_representation_training_and_inference"])
    require(not predictors & forbidden, "A forbidden label entered predictor columns")
    require(len(contract["services"]) == 11, "Primary cohort must retain eleven services")
    feature_sets = manifest["feature_sets"]
    require(set(feature_sets) == {"metrics", "trimodal"}, "Unexpected feature set")
    require(set(feature_sets["metrics"]) < set(feature_sets["trimodal"]),
            "Trimodal inputs must strictly contain the metric inputs")
    require(
        manifest["training_and_calibration"]["retraining_on_blind_data"] is False,
        "Blind retraining must remain disabled",
    )
    require(
        manifest["training_and_calibration"]["threshold_recalibration_on_blind_data"]
        is False,
        "Blind threshold recalibration must remain disabled",
    )
    evaluation = manifest["evaluation_plan"]
    require(
        evaluation["primary_task"]
        == "System condition detection on the common sequence-eligible population.",
        "Primary task changed",
    )
    require(
        float(evaluation["mandatory_control_gate"]["maximum_alert_episodes_per_normal_hour"])
        == 6.0,
        "Control false-alert gate changed",
    )


def main() -> None:
    expected_hash = CHECKSUM_PATH.read_text(encoding="utf-8").split()[0]
    observed_hash = sha256(MANIFEST_PATH)
    require(observed_hash == expected_hash, "Confirmatory manifest checksum changed")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(
        manifest["manifest_version"] == "confirmatory_manifest_v1",
        "Unexpected manifest version",
    )
    require(
        manifest["status"] == "frozen_before_blind_batch_preparation",
        "Manifest is not frozen",
    )
    validate_provenance(manifest)
    validate_candidates(manifest)
    validate_contract(manifest)
    print(f"confirmatory_manifest_v1 valid: sha256={observed_hash}")
    print("10 variants frozen; blind fitting, tuning, and threshold changes disabled.")


if __name__ == "__main__":
    main()
