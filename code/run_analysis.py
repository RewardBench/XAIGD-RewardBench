#!/usr/bin/env python3
"""Regenerate the offline reports shipped with the public snapshot."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from repo_paths import ANNOTATIONS_DIR, REPO_ROOT, RESULTS_DIR, TRIPLETS_DIR


def run(script: str, *arguments: str) -> None:
    command = [sys.executable, str(REPO_ROOT / "code" / script), *arguments]
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extension", action="store_true", help="Analyze the 998-row extension slice.")
    args = parser.parse_args()
    if args.extension:
        annotations = ANNOTATIONS_DIR / "extension_annotations.json"
        triplets = TRIPLETS_DIR / "extension_final_scrambled.json"
        annotation_out = RESULTS_DIR / "extension_annotation_summary.json"
        elo_out = RESULTS_DIR / "extension_elo_rankings.json"
    else:
        annotations = ANNOTATIONS_DIR / "benchmark_annotations.json"
        triplets = TRIPLETS_DIR / "benchmark_clean.json"
        annotation_out = RESULTS_DIR / "annotation_summary.json"
        elo_out = RESULTS_DIR / "elo_rankings.json"
    run("analyze_annotations.py", "--annotations", str(annotations), "--triplets", str(triplets), "--json-out", str(annotation_out))
    run("calculate_elo.py", "--annotations", str(annotations), "--json-out", str(elo_out))
    run("analyze_policy_accuracy.py")
    print("Judge accuracy is a compact packaged report; raw judge outputs are intentionally excluded.")


if __name__ == "__main__":
    main()
