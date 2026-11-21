#!/usr/bin/env python3
"""Quantify pure-normal drift by split, service and original feature."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import compare_algorithms as base


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "config" / "local_reference_manifest_v1.json"
DETAIL_PATH = ROOT / "reports" / "normal_drift_v1.csv"
SUMMARY_PATH = ROOT / "reports" / "normal_drift_v1.json"
FEATURE_NAMES = base.FEATURE_SETS["trimodal"]


def ks_distance(left: np.ndarray, right: np.ndarray) -> float | None:
    left = np.sort(left[np.isfinite(left)])
    right = np.sort(right[np.isfinite(right)])
    if not len(left) or not len(right):
        return None
    support = np.sort(np.unique(np.concatenate((left, right))))
    left_cdf = np.searchsorted(left, support, side="right") / len(left)
    right_cdf = np.searchsorted(right, support, side="right") / len(right)
    return float(np.max(np.abs(left_cdf - right_cdf)))


def finite_median(values: np.ndarray) -> float | None:
    finite = values[np.isfinite(values)]
    return float(np.median(finite)) if len(finite) else None


def train_scale(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    if not len(finite):
        return 1.0
    scale = float(np.percentile(finite, 75) - np.percentile(finite, 25))
    if not np.isfinite(scale) or scale <= 1e-9:
        scale = float(np.std(finite))
    return scale if np.isfinite(scale) and scale > 1e-9 else 1.0


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    dataset = base.load_dataset()
    values = base.numeric_matrix(dataset.rows, FEATURE_NAMES)
    normal = base.mask(
        dataset,
        lambda row: row["phase_membership"] == "pure"
        and row["condition"] == "normal",
    )
    services = np.array([row["service_name"] for row in dataset.assignments])
    splits = np.array([row["split"] for row in dataset.assignments])

    detail: list[dict[str, Any]] = []
    for service in sorted(set(services[normal].tolist())):
        train_rows = normal & (services == service) & (splits == "train")
        for feature_index, feature in enumerate(FEATURE_NAMES):
            train_values = values[train_rows, feature_index]
            train_median = finite_median(train_values)
            scale = train_scale(train_values)
            for target_split in ("validation", "test"):
                target_rows = normal & (services == service) & (splits == target_split)
                target_values = values[target_rows, feature_index]
                target_median = finite_median(target_values)
                median_displacement = (
                    abs(target_median - train_median) / scale
                    if train_median is not None and target_median is not None
                    else None
                )
                detail.append(
                    {
                        "target_split": target_split,
                        "service_name": service,
                        "feature": feature,
                        "train_rows": int(len(train_values)),
                        "target_rows": int(len(target_values)),
                        "train_finite": int(np.sum(np.isfinite(train_values))),
                        "target_finite": int(np.sum(np.isfinite(target_values))),
                        "train_missing_rate": float(np.mean(~np.isfinite(train_values))),
                        "target_missing_rate": float(np.mean(~np.isfinite(target_values))),
                        "absolute_missing_rate_difference": float(
                            abs(
                                np.mean(~np.isfinite(target_values))
                                - np.mean(~np.isfinite(train_values))
                            )
                        ),
                        "train_median_after_log1p": train_median,
                        "target_median_after_log1p": target_median,
                        "train_reference_scale": scale,
                        "standardized_median_displacement": median_displacement,
                        "ks_distance": ks_distance(train_values, target_values),
                    }
                )

    DETAIL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DETAIL_PATH.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(detail[0]))
        writer.writeheader()
        writer.writerows(detail)

    by_split: dict[str, dict[str, Any]] = {}
    for target_split in ("validation", "test"):
        rows = [row for row in detail if row["target_split"] == target_split]
        ks_values = np.array(
            [row["ks_distance"] for row in rows if row["ks_distance"] is not None]
        )
        shifts = np.array(
            [
                row["standardized_median_displacement"]
                for row in rows
                if row["standardized_median_displacement"] is not None
            ]
        )
        missing = np.array([row["absolute_missing_rate_difference"] for row in rows])
        by_split[target_split] = {
            "service_feature_pairs": len(rows),
            "ks_distance": {
                "median": float(np.median(ks_values)),
                "p90": float(np.percentile(ks_values, 90)),
                "maximum": float(np.max(ks_values)),
                "proportion_at_least_0_20": float(np.mean(ks_values >= 0.20)),
            },
            "standardized_median_displacement": {
                "median": float(np.median(shifts)),
                "p90": float(np.percentile(shifts, 90)),
                "maximum": float(np.max(shifts)),
                "proportion_at_least_1": float(np.mean(shifts >= 1.0)),
            },
            "absolute_missing_rate_difference": {
                "median": float(np.median(missing)),
                "p90": float(np.percentile(missing, 90)),
                "maximum": float(np.max(missing)),
                "proportion_at_least_0_10": float(np.mean(missing >= 0.10)),
            },
        }

    rankings: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for metric in (
        "ks_distance",
        "standardized_median_displacement",
        "absolute_missing_rate_difference",
    ):
        eligible = [row for row in detail if row[metric] is not None]
        rankings[metric] = [
            {
                "target_split": row["target_split"],
                "service_name": row["service_name"],
                "feature": row["feature"],
                "value": row[metric],
            }
            for row in sorted(eligible, key=lambda row: row[metric], reverse=True)[:20]
        ]

    summary = {
        "analysis_version": "normal_drift_v1",
        "manifest_version": manifest["manifest_version"],
        "value_transform": "log1p where declared in detector_comparison_v1; otherwise identity",
        "scope": "pure normal windows only",
        "summary_by_target_split": by_split,
        "top_service_feature_pairs": rankings,
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(detail)} service-feature drift comparisons.")
    for split, split_summary in by_split.items():
        print(
            f"{split}: median_KS={split_summary['ks_distance']['median']:.3f}, "
            f"KS>=0.20={split_summary['ks_distance']['proportion_at_least_0_20']:.3f}, "
            "median_shift>=1="
            f"{split_summary['standardized_median_displacement']['proportion_at_least_1']:.3f}"
        )


if __name__ == "__main__":
    main()
