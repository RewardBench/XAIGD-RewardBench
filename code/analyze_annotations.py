#!/usr/bin/env python3
"""Compute privacy-preserving coverage, agreement, and choice summaries."""

from __future__ import annotations

import argparse
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from data_utils import model_name, normalize_choice, read_json, write_json
from repo_paths import ANNOTATIONS_DIR, RESULTS_DIR, TRIPLETS_DIR


def annotation_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for triplet_id, record in data.items():
        for annotator_id, annotation in record.get("annotations", {}).items():
            choice = normalize_choice(annotation.get("choice"))
            if choice:
                rows.append(
                    {
                        "triplet_id": triplet_id,
                        "annotator_id": annotator_id,
                        "choice": choice,
                    }
                )
    return rows


def agreement(data: dict[str, Any], response_only: bool) -> dict[str, Any]:
    total_pairs = matching_pairs = analyzed = unanimous = 0
    allowed = {"response_1_better", "response_2_better"}
    for record in data.values():
        choices = [
            normalize_choice(annotation.get("choice"))
            for annotation in record.get("annotations", {}).values()
        ]
        choices = [choice for choice in choices if choice and (not response_only or choice in allowed)]
        if len(choices) < 2:
            continue
        analyzed += 1
        unanimous += int(len(set(choices)) == 1)
        total_pairs += len(choices) * (len(choices) - 1) // 2
        matching_pairs += sum(left == right for left, right in combinations(choices, 2))
    return {
        "triplets_with_multiple_annotations": analyzed,
        "unanimous_triplets": unanimous,
        "unanimous_rate": unanimous / analyzed if analyzed else 0.0,
        "matching_pairs": matching_pairs,
        "total_pairs": total_pairs,
        "pairwise_rate": matching_pairs / total_pairs if total_pairs else 0.0,
    }


def build_summary(annotation_path: Path, triplet_path: Path) -> dict[str, Any]:
    data = read_json(annotation_path)
    triplets = read_json(triplet_path)
    if not isinstance(data, dict) or not isinstance(triplets, list):
        raise ValueError("annotations must be an object and triplets must be a list")
    rows = annotation_rows(data)
    choices = Counter(row["choice"] for row in rows)
    pairs: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for record in data.values():
        pair = f"{model_name(record.get('csv1'))} vs {model_name(record.get('csv2'))}"
        for annotation in record.get("annotations", {}).values():
            choice = normalize_choice(annotation.get("choice"))
            if choice:
                pairs[pair][choice] += 1
    touched = sum(bool(record.get("annotations")) for record in data.values())
    times = []
    for record in data.values():
        for annotation in record.get("annotations", {}).values():
            # Timing fields are intentionally absent from the release.  This
            # branch keeps the analyzer useful for private, unsanitized input.
            if annotation.get("annotation_time_seconds") is not None:
                times.append(float(annotation["annotation_time_seconds"]))
    summary: dict[str, Any] = {
        "inputs": {"annotations": annotation_path.name, "triplets": triplet_path.name},
        "coverage": {
            "total_triplets": len(triplets),
            "touched_triplets": touched,
            "untouched_triplets": len(triplets) - touched,
            "total_annotations": len(rows),
            "unique_annotators": len({row["annotator_id"] for row in rows}),
            "annotator_ids": sorted({row["annotator_id"] for row in rows}),
            "coverage_rate": touched / len(triplets) if triplets else 0.0,
        },
        "choice_distribution": dict(choices),
        "agreement_all_choices": agreement(data, response_only=False),
        "agreement_response_only": agreement(data, response_only=True),
        "model_pair_choices": {key: dict(value) for key, value in sorted(pairs.items())},
    }
    if times:
        summary["private_input_timing_note"] = {
            "count": len(times),
            "mean_seconds": statistics.mean(times),
            "median_seconds": statistics.median(times),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=ANNOTATIONS_DIR / "benchmark_annotations.json")
    parser.add_argument("--triplets", type=Path, default=TRIPLETS_DIR / "benchmark_clean.json")
    parser.add_argument("--json-out", type=Path, default=RESULTS_DIR / "annotation_summary.json")
    args = parser.parse_args()
    summary = build_summary(args.annotations, args.triplets)
    write_json(args.json_out, summary)
    print(
        f"{summary['coverage']['touched_triplets']}/{summary['coverage']['total_triplets']} "
        f"triplets touched; {summary['coverage']['total_annotations']} annotations"
    )
    print(f"Wrote {args.json_out}")


if __name__ == "__main__":
    main()
