#!/usr/bin/env python3
"""Compare detectors on preregistered local-level and causal-change features."""

from __future__ import annotations

import csv
import json
import platform
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.metrics import average_precision_score

import compare_algorithms as base


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "config" / "local_reference_manifest_v1.json"
V1_SUMMARY_PATH = ROOT / "reports" / "detector_comparison_v1.json"
COMPARISON_PATH = ROOT / "reports" / "local_reference_comparison_v1.csv"
SUMMARY_PATH = ROOT / "reports" / "local_reference_comparison_v1.json"
EXPLANATIONS_PATH = ROOT / "reports" / "local_reference_explanations_v1.json"
AUDIT_PATH = ROOT / "reports" / "local_reference_audit_v1.json"
PREREGISTRATION = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
REFERENCE_STARTS = int(PREREGISTRATION["local_reference"]["distinct_window_starts"])
CLIP = float(PREREGISTRATION["representation"]["clipping"][1])


@dataclass
class SelectedVariant:
    algorithm: str
    feature_set: str
    original_features: list[str]
    derived_features: list[str]
    transformed: np.ndarray
    model: Any
    calibrator: base.ServiceScoreCalibrator
    hyperparameters: dict[str, Any]
    validation_scores: np.ndarray


def local_reference_mask(dataset: base.Dataset) -> tuple[np.ndarray, dict[str, Any]]:
    candidates: dict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)
    for index, assignment in enumerate(dataset.assignments):
        if (
            assignment["phase_membership"] == "pure"
            and assignment["condition"] == "normal"
        ):
            candidates[(assignment["run_id"], assignment["service_name"])].append(
                (assignment["window_start"], index)
            )

    reference = np.zeros(len(dataset.rows), dtype=bool)
    group_counts: dict[str, int] = {}
    start_sets_by_run: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for (run_id, service), entries in sorted(candidates.items()):
        entries.sort()
        distinct_starts = sorted({window_start for window_start, _ in entries})
        if len(distinct_starts) < REFERENCE_STARTS:
            raise ValueError(
                f"Reference group {(run_id, service)} has only "
                f"{len(distinct_starts)} distinct starts"
            )
        selected_starts = set(distinct_starts[:REFERENCE_STARTS])
        indexes = [index for window_start, index in entries if window_start in selected_starts]
        if len(indexes) != REFERENCE_STARTS:
            raise ValueError(f"Expected one row per start for {(run_id, service)}")
        reference[indexes] = True
        group_counts[f"{run_id}:{service}"] = len(indexes)
        start_sets_by_run[run_id].add(tuple(sorted(selected_starts)))

    inconsistent = {
        run_id: len(start_sets)
        for run_id, start_sets in start_sets_by_run.items()
        if len(start_sets) != 1
    }
    if inconsistent:
        raise ValueError(f"Reference starts differ between services: {inconsistent}")
    split_counts: dict[str, int] = defaultdict(int)
    for include, assignment in zip(reference, dataset.assignments, strict=True):
        if include:
            split_counts[assignment["split"]] += 1
    return reference, {
        "reference_rows_by_split": dict(sorted(split_counts.items())),
        "reference_groups": len(group_counts),
        "rows_per_group": sorted(set(group_counts.values())),
        "common_start_set_per_run": True,
    }


def reference_parameters(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        center = np.nanmedian(values, axis=0)
        q25 = np.nanpercentile(values, 25, axis=0)
        q75 = np.nanpercentile(values, 75, axis=0)
        scale = q75 - q25
        standard_deviation = np.nanstd(values, axis=0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-9), scale, standard_deviation)
    center = np.where(np.isfinite(center), center, 0.0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-9), scale, 1.0)
    return center, scale


def local_representation(
    dataset: base.Dataset,
    feature_names: list[str],
    reference: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    raw = base.numeric_matrix(dataset.rows, feature_names)
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, assignment in enumerate(dataset.assignments):
        groups[(assignment["run_id"], assignment["service_name"])].append(index)

    level = np.empty_like(raw, dtype=float)
    change = np.empty_like(raw, dtype=float)
    for key, indexes in groups.items():
        ordered = sorted(indexes, key=lambda index: dataset.assignments[index]["window_start"])
        reference_indexes = [index for index in ordered if reference[index]]
        if len(reference_indexes) != REFERENCE_STARTS:
            raise ValueError(f"Invalid reference count for {key}: {len(reference_indexes)}")
        center, scale = reference_parameters(raw[reference_indexes])
        imputed = np.where(np.isfinite(raw[ordered]), raw[ordered], center)
        local_level = (imputed - center) / scale
        local_change = np.zeros_like(local_level)
        local_change[1:] = (imputed[1:] - imputed[:-1]) / scale
        level[ordered] = np.clip(local_level, -CLIP, CLIP)
        change[ordered] = np.clip(local_change, -CLIP, CLIP)

    derived_names = [f"level:{name}" for name in feature_names] + [
        f"change:{name}" for name in feature_names
    ]
    return np.concatenate((level, change), axis=1), derived_names


def evaluation_masks(
    dataset: base.Dataset, reference: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    train = base.mask(
        dataset,
        lambda row: row["split"] == "train"
        and row["phase_membership"] == "pure"
        and row["condition"] == "normal",
    ) & ~reference
    validation = base.mask(
        dataset,
        lambda row: row["split"] == "validation"
        and row["phase_membership"] == "pure"
        and row["condition"] in {"normal", "fault"},
    ) & ~reference
    test = base.mask(
        dataset,
        lambda row: row["split"] == "test"
        and row["phase_membership"] == "pure"
        and row["condition"] in {"normal", "fault"},
    ) & ~reference
    return train, validation, test


def select_with_validation(
    dataset: base.Dataset,
    reference: np.ndarray,
) -> tuple[list[SelectedVariant], tuple[np.ndarray, np.ndarray, np.ndarray]]:
    train, validation, test = evaluation_masks(dataset, reference)
    services = np.array([row["service_name"] for row in dataset.rows])
    selections: list[SelectedVariant] = []
    for feature_set, feature_names in base.FEATURE_SETS.items():
        transformed, derived_names = local_representation(dataset, feature_names, reference)
        for algorithm in ("robust_rules", "isolation_forest", "one_class_svm"):
            selected: SelectedVariant | None = None
            selection_key: tuple[float, float, str] | None = None
            for parameters, model in base.candidate_models(algorithm):
                model.fit(transformed[train])
                calibrator = base.ServiceScoreCalibrator().fit(
                    model.score(transformed[train]), services[train]
                )
                validation_scores = calibrator.transform(
                    model.score(transformed[validation]), services[validation]
                )
                system_labels, system_scores, _ = base.system_rows(
                    dataset, validation, validation_scores
                )
                localization = base.localization_metrics(
                    dataset, validation, validation_scores
                )
                key = (
                    float(average_precision_score(system_labels, system_scores)),
                    localization["mrr"],
                    json.dumps(parameters, sort_keys=True),
                )
                if selection_key is None or key > selection_key:
                    selection_key = key
                    selected = SelectedVariant(
                        algorithm=algorithm,
                        feature_set=feature_set,
                        original_features=feature_names,
                        derived_features=derived_names,
                        transformed=transformed,
                        model=model,
                        calibrator=calibrator,
                        hyperparameters=parameters,
                        validation_scores=validation_scores,
                    )
            assert selected is not None
            selections.append(selected)
    return selections, (train, validation, test)


def evaluate_frozen_selections(
    dataset: base.Dataset,
    selections: list[SelectedVariant],
    masks: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _, validation, test = masks
    services = np.array([row["service_name"] for row in dataset.rows])
    results: list[dict[str, Any]] = []
    explanations: dict[str, Any] = {}
    for selected in selections:
        test_scores = selected.calibrator.transform(
            selected.model.score(selected.transformed[test]), services[test]
        )
        val_system_y, val_system_score, val_system_keys = base.system_rows(
            dataset, validation, selected.validation_scores
        )
        test_system_y, test_system_score, test_system_keys = base.system_rows(
            dataset, test, test_scores
        )
        system_threshold = base.best_f1_threshold(val_system_y, val_system_score)
        val_service_y, val_service_score = base.service_task(
            dataset, validation, selected.validation_scores
        )
        test_service_y, test_service_score = base.service_task(dataset, test, test_scores)
        service_threshold = base.best_f1_threshold(val_service_y, val_service_score)
        result = {
            "algorithm": selected.algorithm,
            "feature_set": selected.feature_set,
            "features": selected.derived_features,
            "hyperparameters": selected.hyperparameters,
            "validation_system": base.binary_metrics(
                val_system_y, val_system_score, system_threshold, val_system_keys
            ),
            "test_system": base.binary_metrics(
                test_system_y, test_system_score, system_threshold, test_system_keys
            ),
            "validation_affected_service": base.binary_metrics(
                val_service_y, val_service_score, service_threshold
            ),
            "test_affected_service": base.binary_metrics(
                test_service_y, test_service_score, service_threshold
            ),
            "validation_localization": base.localization_metrics(
                dataset, validation, selected.validation_scores
            ),
            "test_localization": base.localization_metrics(dataset, test, test_scores),
        }
        results.append(result)

        test_assignments = [
            assignment
            for include, assignment in zip(test, dataset.assignments, strict=True)
            if include
        ]
        affected_fault = np.array(
            [
                assignment["condition"] == "fault"
                and assignment["service_name"] == assignment["affected_component"]
                for assignment in test_assignments
            ],
            dtype=bool,
        )
        explanations[f"{selected.algorithm}:{selected.feature_set}"] = {
            "method": "feature occlusion to zero local deviation and zero causal change",
            "population": "affected service in pure test fault windows",
            "rows": int(np.sum(affected_fault)),
            "top_features": base.top_occlusion_features(
                selected.model,
                selected.transformed[test][affected_fault],
                selected.derived_features,
            ),
        }
    return results, explanations


def write_flat_results(results: list[dict[str, Any]]) -> None:
    fields = [
        "algorithm", "feature_set", "hyperparameters", "validation_system_ap",
        "test_system_ap", "test_system_precision", "test_system_recall",
        "test_system_f1", "test_system_false_positives",
        "test_system_false_positives_per_normal_hour", "test_system_delay_seconds",
        "test_affected_service_ap", "test_affected_service_f1",
        "test_localization_mrr", "test_localization_mean_rank",
        "test_localization_hit_at_1", "test_localization_hit_at_3",
    ]
    with COMPARISON_PATH.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "algorithm": result["algorithm"],
                    "feature_set": result["feature_set"],
                    "hyperparameters": json.dumps(result["hyperparameters"], sort_keys=True),
                    "validation_system_ap": result["validation_system"]["average_precision"],
                    "test_system_ap": result["test_system"]["average_precision"],
                    "test_system_precision": result["test_system"]["precision"],
                    "test_system_recall": result["test_system"]["recall"],
                    "test_system_f1": result["test_system"]["f1"],
                    "test_system_false_positives": result["test_system"]["false_positives"],
                    "test_system_false_positives_per_normal_hour": result["test_system"]["false_positives_per_normal_hour"],
                    "test_system_delay_seconds": result["test_system"]["delay_from_first_eligible_fault_seconds"],
                    "test_affected_service_ap": result["test_affected_service"]["average_precision"],
                    "test_affected_service_f1": result["test_affected_service"]["f1"],
                    "test_localization_mrr": result["test_localization"]["mrr"],
                    "test_localization_mean_rank": result["test_localization"]["mean_rank"],
                    "test_localization_hit_at_1": result["test_localization"]["hit_at_1"],
                    "test_localization_hit_at_3": result["test_localization"]["hit_at_3"],
                }
            )


def compare_to_v1(
    results: list[dict[str, Any]],
    local_system_prevalence: float,
    local_service_prevalence: float,
) -> list[dict[str, Any]]:
    v1 = json.loads(V1_SUMMARY_PATH.read_text(encoding="utf-8"))
    previous = {(row["algorithm"], row["feature_set"]): row for row in v1["results"]}
    v1_system_prevalence = 0.5
    v1_service_prevalence = 1.0 / 12.0
    comparison = []
    for row in results:
        old = previous[(row["algorithm"], row["feature_set"])]
        comparison.append(
            {
                "algorithm": row["algorithm"],
                "feature_set": row["feature_set"],
                "test_system_ap_v1": old["test_system"]["average_precision"],
                "test_system_ap_local_reference": row["test_system"]["average_precision"],
                "test_system_ap_change": row["test_system"]["average_precision"] - old["test_system"]["average_precision"],
                "test_system_ap_lift_over_prevalence_v1": old["test_system"]["average_precision"] - v1_system_prevalence,
                "test_system_ap_lift_over_prevalence_local_reference": row["test_system"]["average_precision"] - local_system_prevalence,
                "test_affected_service_ap_v1": old["test_affected_service"]["average_precision"],
                "test_affected_service_ap_local_reference": row["test_affected_service"]["average_precision"],
                "test_affected_service_ap_change": row["test_affected_service"]["average_precision"] - old["test_affected_service"]["average_precision"],
                "test_affected_service_ap_lift_over_prevalence_v1": old["test_affected_service"]["average_precision"] - v1_service_prevalence,
                "test_affected_service_ap_lift_over_prevalence_local_reference": row["test_affected_service"]["average_precision"] - local_service_prevalence,
                "test_localization_mrr_v1": old["test_localization"]["mrr"],
                "test_localization_mrr_local_reference": row["test_localization"]["mrr"],
                "test_localization_mrr_change": row["test_localization"]["mrr"] - old["test_localization"]["mrr"],
            }
        )
    return comparison


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    dataset = base.load_dataset()
    reference, audit = local_reference_mask(dataset)
    selections, masks = select_with_validation(dataset, reference)
    print(
        f"Frozen {len(selections)} selections with validation; "
        "evaluating the test split once."
    )
    results, explanations = evaluate_frozen_selections(dataset, selections, masks)
    write_flat_results(results)
    train, validation, test = masks
    service_count = len({row["service_name"] for row in dataset.rows})
    audit.update(
        {
            "fit_rows": int(np.sum(train)),
            "validation_rows": int(np.sum(validation)),
            "test_rows": int(np.sum(test)),
            "fit_normal_starts_per_service": int(np.sum(train) // service_count),
            "validation_normal_starts_per_service": int(
                sum(
                    include and assignment["condition"] == "normal"
                    for include, assignment in zip(validation, dataset.assignments, strict=True)
                ) // service_count
            ),
            "test_normal_starts_per_service": int(
                sum(
                    include and assignment["condition"] == "normal"
                    for include, assignment in zip(test, dataset.assignments, strict=True)
                ) // service_count
            ),
        }
    )
    zero_scores = np.zeros(int(np.sum(test)), dtype=float)
    test_system_labels, _, _ = base.system_rows(dataset, test, zero_scores)
    test_service_labels, _ = base.service_task(dataset, test, zero_scores)
    task_baselines = {
        "test_system_positive_prevalence": float(np.mean(test_system_labels)),
        "test_affected_service_positive_prevalence": float(
            np.mean(test_service_labels)
        ),
        "random_localization_mrr_for_eleven_services": float(
            sum(1.0 / rank for rank in range(1, service_count + 1)) / service_count
        ),
        "random_localization_hit_at_3_for_eleven_services": float(
            3.0 / service_count
        ),
    }
    summary = {
        "comparison_version": "local_reference_comparison_v1",
        "manifest_version": manifest["manifest_version"],
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "random_seed": base.SEED,
        },
        "representation": manifest["representation"],
        "selection_policy": manifest["comparison"],
        "audit": audit,
        "task_baselines": task_baselines,
        "results": results,
        "comparison_with_detector_comparison_v1": compare_to_v1(
            results,
            task_baselines["test_system_positive_prevalence"],
            task_baselines["test_affected_service_positive_prevalence"],
        ),
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    EXPLANATIONS_PATH.write_text(
        json.dumps(explanations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    AUDIT_PATH.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(results)} local-reference detector comparisons.")
    for result in results:
        if result["feature_set"] == "trimodal":
            print(
                f"{result['algorithm']}: test_system_ap={result['test_system']['average_precision']:.3f}, "
                f"test_affected_service_ap={result['test_affected_service']['average_precision']:.3f}, "
                f"test_localization_mrr={result['test_localization']['mrr']:.3f}"
            )
    print("No algorithm is selected; independent conditions and runs remain required.")


if __name__ == "__main__":
    main()
