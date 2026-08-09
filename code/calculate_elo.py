#!/usr/bin/env python3
"""Calculate deterministic Elo rankings from anonymous human preferences."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

from data_utils import model_name, read_json, score_for_choice, write_json
from repo_paths import ANNOTATIONS_DIR, RESULTS_DIR


def calculate(data: dict[str, Any], initial: float, k_factor: float, include_neutral: bool) -> dict[str, Any]:
    ratings: defaultdict[str, float] = defaultdict(lambda: initial)
    stats: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
    processed = skipped = 0
    for triplet_id in sorted(data):
        record = data[triplet_id]
        first, second = model_name(record.get("csv1")), model_name(record.get("csv2"))
        if not first or not second:
            skipped += 1
            continue
        for annotation in record.get("annotations", {}).values():
            score = score_for_choice(annotation.get("choice"), include_neutral)
            if score is None:
                skipped += 1
                continue
            expected = 1.0 / (1.0 + 10 ** ((ratings[second] - ratings[first]) / 400.0))
            delta = k_factor * (score - expected)
            ratings[first] += delta
            ratings[second] -= delta
            stats[first]["games_played"] += 1
            stats[second]["games_played"] += 1
            if score == 1.0:
                stats[first]["wins"] += 1
                stats[second]["losses"] += 1
            elif score == 0.0:
                stats[first]["losses"] += 1
                stats[second]["wins"] += 1
            else:
                stats[first]["neutral"] += 1
                stats[second]["neutral"] += 1
            processed += 1
    rankings = []
    for model in sorted(ratings, key=lambda name: (-ratings[name], name)):
        row = dict(stats[model])
        games = row.get("games_played", 0)
        decisive = row.get("wins", 0) + row.get("losses", 0)
        row.update(
            {
                "model": model,
                "elo_rating": ratings[model],
                "win_rate_non_neutral": row.get("wins", 0) / decisive if decisive else 0.0,
                "games_played": games,
            }
        )
        rankings.append(row)
    for index, row in enumerate(rankings, 1):
        row["rank"] = index
    return {
        "parameters": {
            "initial_rating": initial,
            "k_factor": k_factor,
            "include_neutral": include_neutral,
        },
        "processed_comparisons": processed,
        "skipped_annotations": skipped,
        "rankings": rankings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=ANNOTATIONS_DIR / "benchmark_annotations.json")
    parser.add_argument("--json-out", type=Path, default=RESULTS_DIR / "elo_rankings.json")
    parser.add_argument("--include-neutral", action="store_true")
    args = parser.parse_args()
    data = read_json(args.annotations)
    summary = calculate(data, 1200.0, 32.0, args.include_neutral)
    write_json(args.json_out, summary)
    print("\n".join(f"{row['rank']:>2}. {row['model']}: {row['elo_rating']:.2f}" for row in summary["rankings"]))


if __name__ == "__main__":
    main()
