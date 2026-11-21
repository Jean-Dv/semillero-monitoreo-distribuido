#!/usr/bin/env python3
"""Develop gradient boosting and an LSTM autoencoder without using test rows."""

from __future__ import annotations

import csv
import json
import platform
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
import torch
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

import compare_algorithms as base
import compare_local_reference as local


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "config" / "extended_candidates_manifest_v1.json"
SUMMARY_PATH = ROOT / "reports" / "extended_candidates_development_v1.json"
FLAT_PATH = ROOT / "reports" / "extended_candidates_development_v1.csv"
SEED = 20261121


@dataclass
class SequenceCohort:
    values: np.ndarray
    services: np.ndarray
    dataset: base.Dataset
    endpoint_feature_ids: list[str]


class GradientBoostingDetector:
    def __init__(self, estimator: HistGradientBoostingClassifier):
        self.estimator = estimator

    def score(self, values: np.ndarray) -> np.ndarray:
        return self.estimator.predict_proba(values)[:, 1]


class LSTMAutoencoder(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        latent_size: int,
        sequence_length: int,
    ) -> None:
        super().__init__()
        self.sequence_length = sequence_length
        self.encoder = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.to_latent = nn.Linear(hidden_size, latent_size)
        self.to_decoder_hidden = nn.Linear(latent_size, hidden_size)
        self.decoder = nn.LSTM(latent_size, hidden_size, batch_first=True)
        self.output = nn.Linear(hidden_size, input_size)

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        _, (hidden, _) = self.encoder(values)
        latent = self.to_latent(hidden[-1])
        decoder_input = latent.unsqueeze(1).repeat(1, self.sequence_length, 1)
        initial_hidden = torch.tanh(self.to_decoder_hidden(latent)).unsqueeze(0)
        initial_cell = torch.zeros_like(initial_hidden)
        decoded, _ = self.decoder(
            decoder_input, (initial_hidden, initial_cell)
        )
        return self.output(decoded)


def development_dataset() -> base.Dataset:
    full = base.load_dataset()
    include = [
        assignment["split"] in {"train", "validation"}
        for assignment in full.assignments
    ]
    return base.Dataset(
        rows=[row for row, keep in zip(full.rows, include, strict=True) if keep],
        assignments=[
            row for row, keep in zip(full.assignments, include, strict=True) if keep
        ],
    )


def masks(
    dataset: base.Dataset, reference: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train_normal = base.mask(
        dataset,
        lambda row: row["split"] == "train"
        and row["phase_membership"] == "pure"
        and row["condition"] == "normal",
    ) & ~reference
    train_positive = base.mask(
        dataset,
        lambda row: row["split"] == "train"
        and row["phase_membership"] == "pure"
        and row["condition"] == "fault"
        and row["service_name"] == row["affected_component"],
    )
    train_other_fault = base.mask(
        dataset,
        lambda row: row["split"] == "train"
        and row["phase_membership"] == "pure"
        and row["condition"] == "fault"
        and row["service_name"] != row["affected_component"],
    )
    validation = base.mask(
        dataset,
        lambda row: row["split"] == "validation"
        and row["phase_membership"] == "pure"
        and row["condition"] in {"normal", "fault"},
    ) & ~reference
    return train_normal, train_positive, train_other_fault, validation


def validation_metrics(
    dataset: base.Dataset,
    selected: np.ndarray,
    scores: np.ndarray,
) -> dict[str, Any]:
    system_y, system_scores, system_keys = base.system_rows(
        dataset, selected, scores
    )
    system_threshold = base.best_f1_threshold(system_y, system_scores)
    service_y, service_scores = base.service_task(dataset, selected, scores)
    service_threshold = base.best_f1_threshold(service_y, service_scores)
    return {
        "system": base.binary_metrics(
            system_y, system_scores, system_threshold, system_keys
        ),
        "affected_service": base.binary_metrics(
            service_y, service_scores, service_threshold
        ),
        "localization": base.localization_metrics(dataset, selected, scores),
        "task_baselines": {
            "system_points": int(len(system_y)),
            "system_positive_points": int(np.sum(system_y)),
            "system_positive_prevalence": float(np.mean(system_y)),
            "affected_service_points": int(len(service_y)),
            "affected_service_positive_points": int(np.sum(service_y)),
            "affected_service_positive_prevalence": float(np.mean(service_y)),
            "random_localization_mrr": float(
                sum(1.0 / rank for rank in range(1, 12)) / 11.0
            ),
            "random_localization_hit_at_3": 3.0 / 11.0,
        },
    }


def gradient_boosting_results(
    dataset: base.Dataset,
    reference: np.ndarray,
) -> list[dict[str, Any]]:
    train_normal, train_positive, train_other_fault, validation = masks(
        dataset, reference
    )
    fit = train_normal | train_positive
    labels = train_positive[fit].astype(int)
    negative_count = int(np.sum(labels == 0))
    positive_count = int(np.sum(labels == 1))
    weights = np.where(labels == 1, negative_count / positive_count, 1.0)
    services = np.array([row["service_name"] for row in dataset.assignments])
    results: list[dict[str, Any]] = []
    for feature_set, feature_names in base.FEATURE_SETS.items():
        transformed, derived_names = local.local_representation(
            dataset, feature_names, reference
        )
        estimator = HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=200,
            max_leaf_nodes=15,
            max_depth=None,
            min_samples_leaf=20,
            l2_regularization=1.0,
            early_stopping=False,
            random_state=SEED,
        )
        estimator.fit(transformed[fit], labels, sample_weight=weights)
        model = GradientBoostingDetector(estimator)
        calibrator = base.ServiceScoreCalibrator().fit(
            model.score(transformed[train_normal]), services[train_normal]
        )
        validation_scores = calibrator.transform(
            model.score(transformed[validation]), services[validation]
        )
        result = {
            "algorithm": "hist_gradient_boosting",
            "feature_set": feature_set,
            "features": derived_names,
            "fit_population": {
                "normal_negative_rows": negative_count,
                "affected_service_positive_rows": positive_count,
                "other_fault_rows_excluded_from_fit": int(
                    np.sum(train_other_fault)
                ),
                "positive_sample_weight": float(negative_count / positive_count),
            },
            "hyperparameters": estimator.get_params(),
            "validation": validation_metrics(
                dataset, validation, validation_scores
            ),
        }
        validation_assignments = [
            assignment
            for include, assignment in zip(
                validation, dataset.assignments, strict=True
            )
            if include
        ]
        affected_fault = np.array(
            [
                assignment["condition"] == "fault"
                and assignment["service_name"] == assignment["affected_component"]
                for assignment in validation_assignments
            ],
            dtype=bool,
        )
        result["explanation"] = {
            "method": "occlusion to zero local level and zero previous-window change",
            "population": "affected service in pure validation fault windows",
            "top_features": base.top_occlusion_features(
                model,
                transformed[validation][affected_fault],
                derived_names,
            ),
        }
        results.append(result)
    return results


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace(" ", "T"))


def build_sequences(
    dataset: base.Dataset,
    transformed: np.ndarray,
    reference: np.ndarray,
    split: str,
    conditions: set[str],
    sequence_length: int,
    step_seconds: int,
) -> SequenceCohort:
    eligible = base.mask(
        dataset,
        lambda row: row["split"] == split
        and row["phase_membership"] == "pure"
        and row["condition"] in conditions,
    ) & ~reference
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, assignment in enumerate(dataset.assignments):
        if eligible[index]:
            groups[(assignment["run_id"], assignment["service_name"])].append(index)

    sequences: list[np.ndarray] = []
    assignments: list[dict[str, str]] = []
    endpoint_feature_ids: list[str] = []
    for indexes in groups.values():
        ordered = sorted(
            indexes, key=lambda index: dataset.assignments[index]["window_start"]
        )
        segments: list[list[int]] = []
        current: list[int] = []
        previous_time: datetime | None = None
        for index in ordered:
            current_time = parse_time(dataset.assignments[index]["window_start"])
            if (
                previous_time is not None
                and (current_time - previous_time).total_seconds() != step_seconds
            ):
                if current:
                    segments.append(current)
                current = []
            current.append(index)
            previous_time = current_time
        if current:
            segments.append(current)

        for segment in segments:
            for start in range(0, len(segment) - sequence_length + 1):
                selected = segment[start : start + sequence_length]
                sequence_conditions = {
                    dataset.assignments[index]["condition"] for index in selected
                }
                if len(sequence_conditions) != 1:
                    raise ValueError(
                        "A sequence crossed condition boundaries despite continuity checks"
                    )
                endpoint = selected[-1]
                sequences.append(transformed[selected])
                assignments.append(dataset.assignments[endpoint])
                endpoint_feature_ids.append(dataset.rows[endpoint]["feature_id"])

    if not sequences:
        raise ValueError(f"No sequences generated for {split} and {conditions}")
    values = np.stack(sequences).astype(np.float32)
    services = np.array([row["service_name"] for row in assignments])
    return SequenceCohort(
        values=values,
        services=services,
        dataset=base.Dataset(rows=[{} for _ in assignments], assignments=assignments),
        endpoint_feature_ids=endpoint_feature_ids,
    )


def scale_sequences(
    train_values: np.ndarray, validation_values: np.ndarray
) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    feature_count = train_values.shape[2]
    scaler = StandardScaler().fit(train_values.reshape(-1, feature_count))
    train_scaled = scaler.transform(
        train_values.reshape(-1, feature_count)
    ).reshape(train_values.shape)
    validation_scaled = scaler.transform(
        validation_values.reshape(-1, feature_count)
    ).reshape(validation_values.shape)
    return (
        train_scaled.astype(np.float32),
        validation_scaled.astype(np.float32),
        scaler,
    )


def train_autoencoder(
    train_values: np.ndarray,
    input_size: int,
    sequence_length: int,
) -> tuple[LSTMAutoencoder, list[float]]:
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    model = LSTMAutoencoder(
        input_size=input_size,
        hidden_size=24,
        latent_size=12,
        sequence_length=sequence_length,
    )
    optimizer = torch.optim.Adam(
        model.parameters(), lr=0.001, weight_decay=0.0001
    )
    loss_function = nn.MSELoss()
    loader = DataLoader(
        TensorDataset(torch.from_numpy(train_values)),
        batch_size=32,
        shuffle=False,
    )
    losses: list[float] = []
    model.train()
    for _ in range(80):
        total_loss = 0.0
        total_rows = 0
        for (batch,) in loader:
            optimizer.zero_grad(set_to_none=True)
            reconstruction = model(batch)
            loss = loss_function(reconstruction, batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += float(loss.detach()) * len(batch)
            total_rows += len(batch)
        losses.append(total_loss / total_rows)
    return model, losses


def reconstruct(
    model: LSTMAutoencoder, values: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    with torch.no_grad():
        source = torch.from_numpy(values)
        reconstructed = model(source).numpy()
    squared_error = np.square(values - reconstructed)
    scores = np.mean(squared_error, axis=(1, 2))
    return scores.astype(float), squared_error


def autoencoder_results(
    dataset: base.Dataset,
    reference: np.ndarray,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for feature_set, feature_names in base.FEATURE_SETS.items():
        transformed, derived_names = local.local_representation(
            dataset, feature_names, reference
        )
        train = build_sequences(
            dataset,
            transformed,
            reference,
            split="train",
            conditions={"normal"},
            sequence_length=12,
            step_seconds=10,
        )
        validation = build_sequences(
            dataset,
            transformed,
            reference,
            split="validation",
            conditions={"normal", "fault"},
            sequence_length=12,
            step_seconds=10,
        )
        train_scaled, validation_scaled, scaler = scale_sequences(
            train.values, validation.values
        )
        model, losses = train_autoencoder(
            train_scaled,
            input_size=train_scaled.shape[2],
            sequence_length=train_scaled.shape[1],
        )
        train_scores, _ = reconstruct(model, train_scaled)
        validation_raw_scores, squared_error = reconstruct(
            model, validation_scaled
        )
        calibrator = base.ServiceScoreCalibrator().fit(
            train_scores, train.services
        )
        validation_scores = calibrator.transform(
            validation_raw_scores, validation.services
        )
        selected = np.ones(len(validation_scores), dtype=bool)
        metrics = validation_metrics(
            validation.dataset, selected, validation_scores
        )
        affected_fault = np.array(
            [
                assignment["condition"] == "fault"
                and assignment["service_name"] == assignment["affected_component"]
                for assignment in validation.dataset.assignments
            ],
            dtype=bool,
        )
        feature_error = np.mean(squared_error[affected_fault], axis=(0, 1))
        time_error = np.mean(squared_error[affected_fault], axis=(0, 2))
        top_feature_indexes = np.argsort(feature_error)[::-1][:5]
        top_time_indexes = np.argsort(time_error)[::-1][:5]
        results.append(
            {
                "algorithm": "lstm_temporal_autoencoder",
                "feature_set": feature_set,
                "features": derived_names,
                "sequence": {
                    "length_steps": 12,
                    "step_seconds": 10,
                    "train_sequences": int(len(train.values)),
                    "validation_sequences": int(len(validation.values)),
                    "validation_normal_sequences": int(
                        sum(
                            row["condition"] == "normal"
                            for row in validation.dataset.assignments
                        )
                    ),
                    "validation_fault_sequences": int(
                        sum(
                            row["condition"] == "fault"
                            for row in validation.dataset.assignments
                        )
                    ),
                },
                "architecture": {
                    "input_size": int(train_scaled.shape[2]),
                    "hidden_size": 24,
                    "latent_size": 12,
                    "parameter_count": int(
                        sum(parameter.numel() for parameter in model.parameters())
                    ),
                },
                "optimization": {
                    "epochs": 80,
                    "initial_train_loss": losses[0],
                    "final_train_loss": losses[-1],
                    "minimum_train_loss": min(losses),
                    "scaler_mean_shape": list(scaler.mean_.shape),
                },
                "validation": metrics,
                "explanation": {
                    "method": "mean standardized reconstruction error on affected-service validation fault sequences",
                    "top_features": [
                        {
                            "feature": derived_names[index],
                            "mean_squared_error": float(feature_error[index]),
                        }
                        for index in top_feature_indexes
                    ],
                    "top_relative_steps": [
                        {
                            "relative_step": int(index - 11),
                            "mean_squared_error": float(time_error[index]),
                        }
                        for index in top_time_indexes
                    ],
                },
            }
        )
    return results


def selection_key(result: dict[str, Any]) -> tuple[float, float, str]:
    return (
        result["validation"]["system"]["average_precision"],
        result["validation"]["localization"]["mrr"],
        result["feature_set"],
    )


def flatten(results: list[dict[str, Any]]) -> None:
    fields = [
        "algorithm",
        "feature_set",
        "validation_system_ap",
        "validation_system_prevalence",
        "validation_system_f1",
        "validation_system_false_positives",
        "validation_affected_service_ap",
        "validation_affected_service_prevalence",
        "validation_localization_mrr",
        "validation_localization_hit_at_3",
        "eligible_validation_system_windows",
    ]
    with FLAT_PATH.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for result in results:
            validation = result["validation"]
            writer.writerow(
                {
                    "algorithm": result["algorithm"],
                    "feature_set": result["feature_set"],
                    "validation_system_ap": validation["system"][
                        "average_precision"
                    ],
                    "validation_system_prevalence": validation["task_baselines"][
                        "system_positive_prevalence"
                    ],
                    "validation_system_f1": validation["system"]["f1"],
                    "validation_system_false_positives": validation["system"][
                        "false_positives"
                    ],
                    "validation_affected_service_ap": validation[
                        "affected_service"
                    ]["average_precision"],
                    "validation_affected_service_prevalence": validation[
                        "task_baselines"
                    ]["affected_service_positive_prevalence"],
                    "validation_localization_mrr": validation["localization"][
                        "mrr"
                    ],
                    "validation_localization_hit_at_3": validation[
                        "localization"
                    ]["hit_at_3"],
                    "eligible_validation_system_windows": validation[
                        "task_baselines"
                    ]["system_points"],
                }
            )


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    dataset = development_dataset()
    if any(row["split"] == "test" for row in dataset.assignments):
        raise RuntimeError("Test rows entered the extended-candidate development set")
    reference, reference_audit = local.local_reference_mask(dataset)
    gradient_results = gradient_boosting_results(dataset, reference)
    autoencoder = autoencoder_results(dataset, reference)
    results = gradient_results + autoencoder
    family_ranking = {}
    for algorithm in ("hist_gradient_boosting", "lstm_temporal_autoencoder"):
        selected = max(
            (result for result in results if result["algorithm"] == algorithm),
            key=selection_key,
        )
        family_ranking[algorithm] = {
            "feature_set": selected["feature_set"],
            "validation_system_threshold": selected["validation"]["system"][
                "threshold"
            ],
            "validation_affected_service_threshold": selected["validation"][
                "affected_service"
            ]["threshold"],
            "selection_key": list(selection_key(selected)),
            "status": "provisional validation ranking; not an algorithm selection or confirmatory estimate",
        }
    output = {
        "comparison_version": "extended_candidates_development_v1",
        "manifest_version": manifest["manifest_version"],
        "scope": "test rows were excluded before representation construction and modeling; no test feature, label or prior test result was used",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "torch": torch.__version__,
            "device": "cpu",
            "random_seed": SEED,
        },
        "reference_audit": reference_audit,
        "provisional_family_ranking": family_ranking,
        "results": results,
    }
    SUMMARY_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    flatten(results)
    print("Developed 4 gradient-boosting and 4 LSTM-autoencoder variants.")
    for algorithm, selected in family_ranking.items():
        print(
            f"{algorithm}: top_validation_variant={selected['feature_set']}, "
            f"validation_system_ap={selected['selection_key'][0]:.3f}, "
            f"validation_localization_mrr={selected['selection_key'][1]:.3f}"
        )
    print("Test rows were excluded before modeling; no confirmatory claim is permitted.")


if __name__ == "__main__":
    main()
