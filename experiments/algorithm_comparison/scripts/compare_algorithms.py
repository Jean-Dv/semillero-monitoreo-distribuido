#!/usr/bin/env python3
"""Compare transparent and unsupervised detectors on the frozen cohort."""

from __future__ import annotations

import csv
import json
import math
import platform
import warnings
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
import sklearn
from sklearn.cluster import HDBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    adjusted_mutual_info_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    silhouette_score,
)
from sklearn.svm import OneClassSVM


ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = ROOT / "data" / "features_v1.csv"
ASSIGNMENTS_PATH = ROOT / "reports" / "window_assignments_v1.csv"
MANIFEST_PATH = ROOT / "config" / "partition_manifest_v1.json"
COMPARISON_PATH = ROOT / "reports" / "detector_comparison_v1.csv"
SUMMARY_PATH = ROOT / "reports" / "detector_comparison_v1.json"
HDBSCAN_PATH = ROOT / "reports" / "hdbscan_exploration_v1.json"
EXPLANATIONS_PATH = ROOT / "reports" / "explanations_v1.json"

FEATURE_SETS = {
    "metrics": [
        "pod_count",
        "deployment_count",
        "metric_point_count",
        "request_rate",
        "cpu_usage_cores",
        "memory_working_set_bytes",
        "missing_metrics",
    ],
    "logs": ["log_count", "log_error_ratio", "missing_logs"],
    "traces": [
        "span_count",
        "server_span_count",
        "span_error_ratio",
        "latency_p50_ms",
        "latency_p95_ms",
        "latency_p99_ms",
        "dependency_edge_count",
        "missing_traces",
    ],
}
FEATURE_SETS["trimodal"] = (
    FEATURE_SETS["metrics"] + FEATURE_SETS["logs"] + FEATURE_SETS["traces"]
)
SEED = 20261121
LOG1P_FEATURES = {
    "pod_count",
    "deployment_count",
    "metric_point_count",
    "request_rate",
    "span_count",
    "server_span_count",
    "log_count",
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
    "cpu_usage_cores",
    "memory_working_set_bytes",
    "dependency_edge_count",
}


@dataclass
class Dataset:
    rows: list[dict[str, str]]
    assignments: list[dict[str, str]]


class ServiceRobustScaler:
    """Median/IQR scaling fitted independently per service on training normal."""

    def __init__(self, feature_names: list[str]):
        self.feature_names = feature_names
        self.parameters: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        self.global_center: np.ndarray | None = None
        self.global_scale: np.ndarray | None = None

    @staticmethod
    def _parameters(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            center = np.nanmedian(values, axis=0)
            q25 = np.nanpercentile(values, 25, axis=0)
            q75 = np.nanpercentile(values, 75, axis=0)
            standard_deviation = np.nanstd(values, axis=0)
        scale = q75 - q25
        scale = np.where(
            np.isfinite(scale) & (scale > 1e-9), scale, standard_deviation
        )
        finite_counts = np.isfinite(values).sum(axis=0)
        return center, scale, finite_counts

    def fit(self, values: np.ndarray, services: np.ndarray) -> "ServiceRobustScaler":
        global_center, global_scale, _ = self._parameters(values)
        self.global_center = np.where(np.isfinite(global_center), global_center, 0.0)
        self.global_scale = np.where(
            np.isfinite(global_scale) & (global_scale > 1e-9), global_scale, 1.0
        )
        for service in sorted(set(services.tolist())):
            selected = values[services == service]
            center, scale, finite_counts = self._parameters(selected)
            center = np.where(finite_counts > 0, center, self.global_center)
            scale = np.where(
                (finite_counts > 0) & np.isfinite(scale) & (scale > 1e-9),
                scale,
                self.global_scale,
            )
            self.parameters[service] = (center, scale)
        return self

    def transform(self, values: np.ndarray, services: np.ndarray) -> np.ndarray:
        if self.global_center is None or self.global_scale is None:
            raise RuntimeError("Scaler has not been fitted")
        transformed = np.empty_like(values, dtype=float)
        for index, (row, service) in enumerate(zip(values, services, strict=True)):
            center, scale = self.parameters.get(
                service, (self.global_center, self.global_scale)
            )
            imputed = np.where(np.isfinite(row), row, center)
            transformed[index] = np.clip((imputed - center) / scale, -20.0, 20.0)
        return transformed


class RobustRuleDetector:
    def fit(self, _: np.ndarray) -> "RobustRuleDetector":
        return self

    def score(self, values: np.ndarray) -> np.ndarray:
        return np.max(np.abs(values), axis=1)


class ServiceScoreCalibrator:
    """Map raw anomaly scores to an empirical service-specific tail percentile."""

    def __init__(self) -> None:
        self.reference_scores: dict[str, np.ndarray] = {}
        self.global_scores: np.ndarray | None = None

    def fit(
        self, scores: np.ndarray, services: np.ndarray
    ) -> "ServiceScoreCalibrator":
        self.global_scores = np.sort(scores.astype(float))
        for service in sorted(set(services.tolist())):
            self.reference_scores[service] = np.sort(scores[services == service].astype(float))
        return self

    def transform(self, scores: np.ndarray, services: np.ndarray) -> np.ndarray:
        if self.global_scores is None:
            raise RuntimeError("Score calibrator has not been fitted")
        calibrated = np.empty(len(scores), dtype=float)
        for index, (score, service) in enumerate(zip(scores, services, strict=True)):
            reference = self.reference_scores.get(service, self.global_scores)
            rank = np.searchsorted(reference, score, side="right")
            calibrated[index] = (rank + 0.5) / (len(reference) + 1.0)
        return calibrated


class SklearnDetector:
    def __init__(self, estimator: Any):
        self.estimator = estimator

    def fit(self, values: np.ndarray) -> "SklearnDetector":
        self.estimator.fit(values)
        return self

    def score(self, values: np.ndarray) -> np.ndarray:
        return -self.estimator.score_samples(values)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def load_dataset() -> Dataset:
    rows = read_csv(FEATURES_PATH)
    assignment_by_id = {row["feature_id"]: row for row in read_csv(ASSIGNMENTS_PATH)}
    if len(rows) != len(assignment_by_id):
        raise ValueError("Feature and assignment row counts differ")
    assignments = []
    for row in rows:
        try:
            assignments.append(assignment_by_id[row["feature_id"]])
        except KeyError as error:
            raise ValueError(f"Missing assignment for {row['feature_id']}") from error
    return Dataset(rows=rows, assignments=assignments)


def numeric_matrix(rows: list[dict[str, str]], feature_names: list[str]) -> np.ndarray:
    values = np.empty((len(rows), len(feature_names)), dtype=float)
    for row_index, row in enumerate(rows):
        for column_index, feature in enumerate(feature_names):
            raw = row[feature]
            value = (
                float(raw) if raw not in {"", "\\N"} else np.nan
            )
            if feature in LOG1P_FEATURES and np.isfinite(value):
                if value < 0:
                    raise ValueError(f"Negative value for log1p feature {feature}: {value}")
                value = np.log1p(value)
            values[row_index, column_index] = value
    return values


def mask(dataset: Dataset, predicate: Callable[[dict[str, str]], bool]) -> np.ndarray:
    return np.array([predicate(row) for row in dataset.assignments], dtype=bool)


def system_rows(
    dataset: Dataset, selected: np.ndarray, scores: np.ndarray
) -> tuple[np.ndarray, np.ndarray, list[tuple[str, str]]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    score_index = 0
    for include, assignment in zip(selected, dataset.assignments, strict=True):
        if not include:
            continue
        key = (assignment["run_id"], assignment["window_start"])
        entry = grouped.setdefault(
            key,
            {
                "condition": assignment["condition"],
                "scores": [],
            },
        )
        if entry["condition"] != assignment["condition"]:
            raise ValueError(f"Condition disagreement at {key}")
        entry["scores"].append(float(scores[score_index]))
        score_index += 1
    keys = sorted(grouped)
    labels = np.array(
        [1 if grouped[key]["condition"] == "fault" else 0 for key in keys], dtype=int
    )
    aggregate_scores = np.array(
        [max(grouped[key]["scores"]) for key in keys], dtype=float
    )
    return labels, aggregate_scores, keys


def localization_metrics(
    dataset: Dataset, selected: np.ndarray, scores: np.ndarray
) -> dict[str, float]:
    grouped: dict[tuple[str, str], list[tuple[str, float, str]]] = defaultdict(list)
    score_index = 0
    for include, assignment in zip(selected, dataset.assignments, strict=True):
        if not include:
            continue
        score = float(scores[score_index])
        score_index += 1
        if assignment["condition"] != "fault":
            continue
        key = (assignment["run_id"], assignment["window_start"])
        grouped[key].append(
            (
                assignment["service_name"],
                score,
                assignment["affected_component"],
            )
        )
    ranks = []
    for entries in grouped.values():
        affected = entries[0][2]
        affected_scores = [score for service, score, _ in entries if service == affected]
        if len(affected_scores) != 1:
            raise ValueError(f"Expected one score for affected service {affected}")
        affected_score = affected_scores[0]
        greater = sum(score > affected_score for _, score, _ in entries)
        equal = sum(math.isclose(score, affected_score) for _, score, _ in entries)
        ranks.append(1.0 + greater + 0.5 * (equal - 1))
    rank_array = np.array(ranks, dtype=float)
    return {
        "mrr": float(np.mean(1.0 / rank_array)),
        "mean_rank": float(np.mean(rank_array)),
        "hit_at_1": float(np.mean(rank_array <= 1)),
        "hit_at_3": float(np.mean(rank_array <= 3)),
        "fault_windows": int(len(rank_array)),
    }


def best_f1_threshold(labels: np.ndarray, scores: np.ndarray) -> float:
    candidates = np.unique(scores)
    best = (-1.0, -1.0, float(candidates[0]))
    for threshold in candidates:
        predictions = (scores >= threshold).astype(int)
        f1 = f1_score(labels, predictions, zero_division=0)
        false_positives = int(np.sum((predictions == 1) & (labels == 0)))
        candidate = (float(f1), float(-false_positives), float(threshold))
        if candidate > best:
            best = candidate
    return best[2]


def binary_metrics(
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    keys: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    predictions = (scores >= threshold).astype(int)
    result: dict[str, Any] = {
        "average_precision": float(average_precision_score(labels, scores)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "false_positives": int(np.sum((predictions == 1) & (labels == 0))),
        "true_positives": int(np.sum((predictions == 1) & (labels == 1))),
        "threshold": float(threshold),
    }
    if keys is not None:
        normal_points = int(np.sum(labels == 0))
        observed_normal_hours = normal_points * 10.0 / 3600.0
        result["false_positives_per_normal_hour"] = (
            result["false_positives"] / observed_normal_hours
            if observed_normal_hours
            else None
        )
        fault_indexes = np.flatnonzero(labels == 1)
        detected_fault_indexes = np.flatnonzero((labels == 1) & (predictions == 1))
        if len(fault_indexes) and len(detected_fault_indexes):
            first_fault = datetime.fromisoformat(keys[fault_indexes[0]][1].replace(" ", "T"))
            first_detection = datetime.fromisoformat(
                keys[detected_fault_indexes[0]][1].replace(" ", "T")
            )
            result["delay_from_first_eligible_fault_seconds"] = (
                first_detection - first_fault
            ).total_seconds()
        else:
            result["delay_from_first_eligible_fault_seconds"] = None
    return result


def service_task(
    dataset: Dataset, selected: np.ndarray, scores: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    labels = []
    selected_scores = []
    score_index = 0
    for include, assignment in zip(selected, dataset.assignments, strict=True):
        if not include:
            continue
        score = float(scores[score_index])
        score_index += 1
        if assignment["condition"] == "normal":
            labels.append(0)
            selected_scores.append(score)
        elif assignment["service_name"] == assignment["affected_component"]:
            labels.append(1)
            selected_scores.append(score)
    return np.array(labels, dtype=int), np.array(selected_scores, dtype=float)


def candidate_models(algorithm: str) -> list[tuple[dict[str, Any], Any]]:
    if algorithm == "robust_rules":
        return [({}, RobustRuleDetector())]
    if algorithm == "isolation_forest":
        return [
            (
                {"n_estimators": 300, "max_samples": max_samples, "max_features": max_features},
                SklearnDetector(
                    IsolationForest(
                        n_estimators=300,
                        max_samples=max_samples,
                        max_features=max_features,
                        contamination="auto",
                        random_state=SEED,
                        n_jobs=-1,
                    )
                ),
            )
            for max_samples in (128, 256)
            for max_features in (0.75, 1.0)
        ]
    if algorithm == "one_class_svm":
        return [
            (
                {"nu": nu, "gamma": gamma},
                SklearnDetector(OneClassSVM(kernel="rbf", nu=nu, gamma=gamma)),
            )
            for nu in (0.01, 0.05, 0.1)
            for gamma in ("scale", 0.01, 0.1)
        ]
    raise ValueError(f"Unknown algorithm: {algorithm}")


def top_occlusion_features(
    model: Any,
    values: np.ndarray,
    feature_names: list[str],
) -> list[dict[str, float | str]]:
    original = model.score(values)
    contributions = []
    for column, feature in enumerate(feature_names):
        occluded = values.copy()
        occluded[:, column] = 0.0
        decrease = original - model.score(occluded)
        contributions.append(
            {
                "feature": feature,
                "mean_score_decrease": float(np.mean(decrease)),
                "mean_absolute_score_change": float(np.mean(np.abs(decrease))),
            }
        )
    return sorted(
        contributions,
        key=lambda item: item["mean_score_decrease"],
        reverse=True,
    )[:5]


def run_detectors(dataset: Dataset) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    train = mask(
        dataset,
        lambda row: row["split"] == "train"
        and row["phase_membership"] == "pure"
        and row["condition"] == "normal",
    )
    validation = mask(
        dataset,
        lambda row: row["split"] == "validation"
        and row["phase_membership"] == "pure"
        and row["condition"] in {"normal", "fault"},
    )
    test = mask(
        dataset,
        lambda row: row["split"] == "test"
        and row["phase_membership"] == "pure"
        and row["condition"] in {"normal", "fault"},
    )
    services = np.array([row["service_name"] for row in dataset.rows])
    results = []
    explanations: dict[str, Any] = {}
    for feature_set, feature_names in FEATURE_SETS.items():
        raw = numeric_matrix(dataset.rows, feature_names)
        scaler = ServiceRobustScaler(feature_names).fit(raw[train], services[train])
        transformed = scaler.transform(raw, services)
        for algorithm in ("robust_rules", "isolation_forest", "one_class_svm"):
            selected_model = None
            selected_params = None
            selected_validation_scores = None
            selected_calibrator = None
            selection_key = None
            for params, model in candidate_models(algorithm):
                model.fit(transformed[train])
                calibrator = ServiceScoreCalibrator().fit(
                    model.score(transformed[train]), services[train]
                )
                validation_scores = calibrator.transform(
                    model.score(transformed[validation]), services[validation]
                )
                system_labels, system_scores, _ = system_rows(
                    dataset, validation, validation_scores
                )
                localization = localization_metrics(
                    dataset, validation, validation_scores
                )
                key = (
                    float(average_precision_score(system_labels, system_scores)),
                    localization["mrr"],
                    json.dumps(params, sort_keys=True),
                )
                if selection_key is None or key > selection_key:
                    selection_key = key
                    selected_model = model
                    selected_params = params
                    selected_validation_scores = validation_scores
                    selected_calibrator = calibrator
            assert selected_model is not None
            assert selected_validation_scores is not None
            assert selected_calibrator is not None
            test_scores = selected_calibrator.transform(
                selected_model.score(transformed[test]), services[test]
            )

            val_system_y, val_system_score, val_system_keys = system_rows(
                dataset, validation, selected_validation_scores
            )
            test_system_y, test_system_score, test_system_keys = system_rows(
                dataset, test, test_scores
            )
            system_threshold = best_f1_threshold(val_system_y, val_system_score)
            val_service_y, val_service_score = service_task(
                dataset, validation, selected_validation_scores
            )
            test_service_y, test_service_score = service_task(dataset, test, test_scores)
            service_threshold = best_f1_threshold(val_service_y, val_service_score)
            result = {
                "algorithm": algorithm,
                "feature_set": feature_set,
                "features": feature_names,
                "hyperparameters": selected_params,
                "validation_system": binary_metrics(
                    val_system_y, val_system_score, system_threshold, val_system_keys
                ),
                "test_system": binary_metrics(
                    test_system_y, test_system_score, system_threshold, test_system_keys
                ),
                "validation_affected_service": binary_metrics(
                    val_service_y, val_service_score, service_threshold
                ),
                "test_affected_service": binary_metrics(
                    test_service_y, test_service_score, service_threshold
                ),
                "validation_localization": localization_metrics(
                    dataset, validation, selected_validation_scores
                ),
                "test_localization": localization_metrics(dataset, test, test_scores),
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
            explanation_key = f"{algorithm}:{feature_set}"
            explanations[explanation_key] = {
                "method": "feature occlusion to the service-specific training median",
                "population": "affected service in pure test fault windows",
                "rows": int(np.sum(affected_fault)),
                "top_features": top_occlusion_features(
                    selected_model, transformed[test][affected_fault], feature_names
                ),
            }
    return results, explanations


def run_hdbscan(dataset: Dataset) -> dict[str, Any]:
    train = mask(
        dataset,
        lambda row: row["split"] == "train"
        and row["phase_membership"] == "pure"
        and row["condition"] == "normal",
    )
    validation = mask(
        dataset,
        lambda row: row["split"] == "validation"
        and row["phase_membership"] == "pure"
        and row["condition"] in {"normal", "fault"},
    )
    test = mask(
        dataset,
        lambda row: row["split"] == "test"
        and row["phase_membership"] == "pure"
        and row["condition"] in {"normal", "fault"},
    )
    services = np.array([row["service_name"] for row in dataset.rows])
    output: dict[str, Any] = {
        "role": "exploratory transductive clustering; not directly compared as a novelty detector",
        "selection": "validation silhouette multiplied by non-noise coverage",
        "feature_sets": {},
    }
    for feature_set, feature_names in FEATURE_SETS.items():
        raw = numeric_matrix(dataset.rows, feature_names)
        scaler = ServiceRobustScaler(feature_names).fit(raw[train], services[train])
        transformed = scaler.transform(raw, services)
        best = None
        for min_cluster_size in (10, 20, 30):
            for min_samples in (5, 10):
                model = HDBSCAN(
                    min_cluster_size=min_cluster_size,
                    min_samples=min_samples,
                    allow_single_cluster=True,
                    copy=True,
                )
                labels = model.fit_predict(transformed[validation])
                non_noise = labels != -1
                clusters = set(labels[non_noise].tolist())
                coverage = float(np.mean(non_noise))
                if len(clusters) >= 2 and np.sum(non_noise) > len(clusters):
                    silhouette = float(
                        silhouette_score(transformed[validation][non_noise], labels[non_noise])
                    )
                else:
                    silhouette = -1.0
                objective = silhouette * coverage
                candidate = (
                    objective,
                    coverage,
                    -min_cluster_size,
                    -min_samples,
                    min_cluster_size,
                    min_samples,
                )
                if best is None or candidate > best:
                    best = candidate
        assert best is not None
        min_cluster_size, min_samples = best[-2], best[-1]
        model = HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            allow_single_cluster=True,
            copy=True,
        )
        labels = model.fit_predict(transformed[test])
        test_assignments = [
            assignment
            for include, assignment in zip(test, dataset.assignments, strict=True)
            if include
        ]
        conditions = np.array(
            [1 if row["condition"] == "fault" else 0 for row in test_assignments],
            dtype=int,
        )
        non_noise = labels != -1
        output["feature_sets"][feature_set] = {
            "hyperparameters": {
                "min_cluster_size": min_cluster_size,
                "min_samples": min_samples,
            },
            "test_clusters": len(set(labels[non_noise].tolist())),
            "test_noise_ratio": float(np.mean(~non_noise)),
            "test_normal_noise_ratio": float(np.mean(labels[conditions == 0] == -1)),
            "test_fault_noise_ratio": float(np.mean(labels[conditions == 1] == -1)),
            "condition_adjusted_mutual_information": float(
                adjusted_mutual_info_score(conditions, labels)
            ),
        }
    return output


def flatten_results(results: list[dict[str, Any]]) -> None:
    fields = [
        "algorithm",
        "feature_set",
        "hyperparameters",
        "validation_system_ap",
        "validation_system_f1",
        "test_system_ap",
        "test_system_precision",
        "test_system_recall",
        "test_system_f1",
        "test_system_false_positives",
        "test_system_false_positives_per_normal_hour",
        "test_system_delay_seconds",
        "test_affected_service_ap",
        "test_affected_service_f1",
        "test_localization_mrr",
        "test_localization_mean_rank",
        "test_localization_hit_at_1",
        "test_localization_hit_at_3",
    ]
    with COMPARISON_PATH.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "algorithm": result["algorithm"],
                    "feature_set": result["feature_set"],
                    "hyperparameters": json.dumps(
                        result["hyperparameters"], sort_keys=True
                    ),
                    "validation_system_ap": result["validation_system"][
                        "average_precision"
                    ],
                    "validation_system_f1": result["validation_system"]["f1"],
                    "test_system_ap": result["test_system"]["average_precision"],
                    "test_system_precision": result["test_system"]["precision"],
                    "test_system_recall": result["test_system"]["recall"],
                    "test_system_f1": result["test_system"]["f1"],
                    "test_system_false_positives": result["test_system"][
                        "false_positives"
                    ],
                    "test_system_false_positives_per_normal_hour": result[
                        "test_system"
                    ]["false_positives_per_normal_hour"],
                    "test_system_delay_seconds": result["test_system"][
                        "delay_from_first_eligible_fault_seconds"
                    ],
                    "test_affected_service_ap": result["test_affected_service"][
                        "average_precision"
                    ],
                    "test_affected_service_f1": result["test_affected_service"]["f1"],
                    "test_localization_mrr": result["test_localization"]["mrr"],
                    "test_localization_mean_rank": result["test_localization"][
                        "mean_rank"
                    ],
                    "test_localization_hit_at_1": result["test_localization"][
                        "hit_at_1"
                    ],
                    "test_localization_hit_at_3": result["test_localization"][
                        "hit_at_3"
                    ],
                }
            )


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    dataset = load_dataset()
    results, explanations = run_detectors(dataset)
    hdbscan = run_hdbscan(dataset)
    flatten_results(results)
    summary = {
        "comparison_version": "detector_comparison_v1",
        "manifest_version": manifest["manifest_version"],
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "random_seed": SEED,
        },
        "preprocessing": {
            "magnitude_transform": "log1p for non-negative counts, rates, latency, CPU and memory",
            "scaling": "per-service median and IQR fitted on train-normal; global train-normal fallback",
            "imputation": "per-service train-normal median; global train-normal fallback",
            "clipping": [-20.0, 20.0],
            "score_calibration": "empirical percentile per service fitted on train-normal raw scores"
        },
        "selection_policy": "Hyperparameters and thresholds use validation only; test is evaluated once after selection.",
        "results": results,
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    HDBSCAN_PATH.write_text(
        json.dumps(hdbscan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    EXPLANATIONS_PATH.write_text(
        json.dumps(explanations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(results)} detector comparisons.")
    for result in results:
        if result["feature_set"] == "trimodal":
            print(
                f"{result['algorithm']}: "
                f"test_system_ap={result['test_system']['average_precision']:.3f}, "
                f"test_localization_mrr={result['test_localization']['mrr']:.3f}"
            )
    print("No algorithm is selected automatically; interpret the tasks jointly.")


if __name__ == "__main__":
    main()
