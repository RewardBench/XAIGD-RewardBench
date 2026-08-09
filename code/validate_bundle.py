#!/usr/bin/env python3
"""Offline release validator for schemas, counts, joins, and privacy hazards."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from data_utils import read_json, triplet_fingerprint
from repo_paths import ANNOTATIONS_DIR, DATA_DIR, METADATA_DIR, MODEL_OUTPUTS_DIR, REPO_ROOT, RESULTS_DIR, TRIPLETS_DIR


ABSOLUTE_PATH_RE = re.compile(
    r"(?:/Users/|/home/|[A-Za-z]:[\\/](?:Users|home|private|tmp|var|Volumes|Documents|storage))"
)
SECRET_RES = (
    re.compile(r"(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(?:api[_ -]?key|access[_ -]?token)[ \t]*[:=][ \t]*[A-Za-z0-9_./+=-]{20,}"),
)
PERSONAL_MARKERS = re.compile(
    r"(?i)(?:michaelyang|michael_yang|michaelYang469|storage/images/)"
)
FORBIDDEN_NAMES = {"images", "hf_upload", ".gradio", "__pycache__", ".venv", "venv", "logs"}
CAMERA_IMAGES_DIR = Path("data/camera_real_subset/images")
CAMERA_IMAGE_NAME_RE = re.compile(r"camera_real_\d{3}\.jpg$")
<<<<<<< HEAD
=======
PUBLIC_HF_DATASET_URL = "https://huggingface.co/datasets/MichaelYang469/XAIGID-RewardBench"
>>>>>>> 538693c (documentation)


def fail(message: str) -> None:
    raise ValueError(message)


def assert_json_files_parse() -> None:
    for path in REPO_ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path.suffix.lower() not in {".json", ".jsonl"}:
            continue
        if path.suffix.lower() == ".json":
            read_json(path)
        else:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as exc:
                        fail(f"invalid JSONL {path}:{line_number}: {exc}")


def assert_no_forbidden_files() -> None:
    for path in REPO_ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(REPO_ROOT)
        is_camera_image = relative == CAMERA_IMAGES_DIR or relative.is_relative_to(CAMERA_IMAGES_DIR)
<<<<<<< HEAD
        if is_camera_image and path.is_file() and not CAMERA_IMAGE_NAME_RE.fullmatch(path.name):
=======
        if is_camera_image and path.is_file() and path.name != "README.md" and not CAMERA_IMAGE_NAME_RE.fullmatch(path.name):
>>>>>>> 538693c (documentation)
            fail(f"unexpected camera image filename: {relative}")
        if any(part in FORBIDDEN_NAMES for part in path.parts) and not is_camera_image:
            fail(f"forbidden release path: {path.relative_to(REPO_ROOT)}")


def assert_privacy() -> None:
    scan_roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / ".env.example",
        REPO_ROOT / ".gitignore",
        REPO_ROOT / "code",
        REPO_ROOT / "data",
        REPO_ROOT / "results",
        REPO_ROOT / "supplementary",
    ]
    for root in scan_roots:
        paths = [root] if root.is_file() else list(root.rglob("*"))
        for path in paths:
            if not path.is_file() or path.name == Path(__file__).name:
                continue
            relative = path.relative_to(REPO_ROOT)
<<<<<<< HEAD
            if relative.is_relative_to(CAMERA_IMAGES_DIR):
=======
            if relative.is_relative_to(CAMERA_IMAGES_DIR) and path.suffix.lower() == ".jpg":
>>>>>>> 538693c (documentation)
                payload = path.read_bytes()
                if any(marker in payload for marker in (b"\xff\xe1", b"\xff\xe2", b"\xff\xed", b"\xff\xfe")):
                    fail(f"camera JPEG contains metadata marker: {relative}")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
<<<<<<< HEAD
=======
            if path == REPO_ROOT / "README.md":
                text = text.replace(PUBLIC_HF_DATASET_URL, "")
>>>>>>> 538693c (documentation)
            if ABSOLUTE_PATH_RE.search(text) or PERSONAL_MARKERS.search(text):
                fail(f"privacy marker found in {path.relative_to(REPO_ROOT)}")
            for secret_re in SECRET_RES:
                if secret_re.search(text):
                    fail(f"credential-like marker found in {path.relative_to(REPO_ROOT)}")
            if re.search(r"(?i)[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text):
                fail(f"email-like value found in {path.relative_to(REPO_ROOT)}")


def assert_no_local_path_keys(value: Any, location: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"img_path", "image_path", "local_image_path"}:
                if (
                    key == "image_path"
                    and location.startswith("data/camera_real_subset")
                    and isinstance(child, str)
                    and re.fullmatch(r"camera_real_\d{3}\.jpg", child)
                ):
                    continue
                fail(f"local image-path field found at {location}.{key}")
            assert_no_local_path_keys(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_local_path_keys(child, f"{location}[{index}]")


def validate() -> None:
    assert_no_forbidden_files()
    assert_json_files_parse()
    assert_privacy()

    benchmark = read_json(TRIPLETS_DIR / "benchmark_clean.json")
    extension = read_json(TRIPLETS_DIR / "extension_final.json")
    extension_scrambled = read_json(TRIPLETS_DIR / "extension_final_scrambled.json")
    if len(benchmark) != 3988 or len(extension) != 998 or len(extension_scrambled) != 998:
        fail("triplet counts are not 3988, 998, 998")
    if {triplet_fingerprint(row) for row in extension} != {
        triplet_fingerprint(row) for row in extension_scrambled
    }:
        fail("ordered and scrambled extension triplets do not contain the same universe")
    for rows in (benchmark, extension, extension_scrambled):
        for row in rows:
            if not row.get("image_id") or not row.get("hf_annotation_id"):
                fail("triplet is missing image_id or hf_annotation_id")
            if row.get("image_type") not in {"real", "synthetic", "unknown"}:
                fail("triplet has an invalid image_type")
        assert_no_local_path_keys(rows)

    benchmark_annotations = read_json(ANNOTATIONS_DIR / "benchmark_annotations.json")
    extension_annotations = read_json(ANNOTATIONS_DIR / "extension_annotations.json")
    if len(benchmark_annotations) != 3959 or len(extension_annotations) != 969:
        fail("annotation row counts are not 3959 and 969")
    benchmark_by_id = {row["benchmark_id"]: row for row in benchmark}
    extension_by_id = {row["triplet_id"]: row for row in extension_scrambled}
    for key, record in benchmark_annotations.items():
        if key not in benchmark_by_id or record.get("triplet_id") != benchmark_by_id[key]["triplet_id"]:
            fail(f"benchmark annotation join failed: {key}")
        if any(not name.startswith("annotator_") for name in record.get("annotations", {})):
            fail("non-anonymous annotator ID found")
    for key, record in extension_annotations.items():
        if key not in extension_by_id:
            fail(f"extension annotation references unknown triplet: {key}")
        if record.get("triplet_id") != key:
            fail(f"extension annotation key mismatch: {key}")
    assert_no_local_path_keys(benchmark_annotations)
    assert_no_local_path_keys(extension_annotations)

    image_index = read_json(METADATA_DIR / "image_index.json")
    if len(image_index) != 1000 or len({row.get("image_id") for row in image_index}) != 1000:
        fail("image index must contain 1,000 unique images")
    if any(not row.get("hf_annotation_id") for row in image_index):
        fail("image index contains an image without an HF annotation ID")

    policy_files = sorted(MODEL_OUTPUTS_DIR.glob("*.json"))
    if len(policy_files) != 16:
        fail(f"expected 16 policy-response files, found {len(policy_files)}")
    for path in policy_files:
        rows = read_json(path)
        if len(rows) != 500:
            fail(f"{path.name} does not contain 500 responses")
        if any(not row.get("image_id") or "answer" not in row for row in rows):
            fail(f"{path.name} has an invalid response row")

    policy_summary = read_json(RESULTS_DIR / "policy_accuracy.json")
    if len(policy_summary.get("models", [])) != 8:
        fail("policy accuracy report does not contain eight models")
    elo_summary = read_json(RESULTS_DIR / "elo_rankings.json")
    if len(elo_summary.get("rankings", [])) != 8:
        fail("Elo report does not contain eight models")
    annotation_summary = read_json(RESULTS_DIR / "annotation_summary.json")
    coverage = annotation_summary.get("coverage", {})
    if coverage.get("total_triplets") != 3988 or coverage.get("touched_triplets") != 3959:
        fail("annotation summary coverage is stale")
    judge_summary = read_json(RESULTS_DIR / "judge_accuracy.json")
    if len(judge_summary.get("judges", [])) != 9:
        fail("judge accuracy report does not contain nine judges")

    for path in REPO_ROOT.rglob("*.json"):
        if ".git" not in path.parts:
            assert_no_local_path_keys(read_json(path), str(path.relative_to(REPO_ROOT)))
    print("offline public bundle validation passed")
    print("triplets: 3988 benchmark + 998 extension")
    print("annotations: 3959 benchmark rows + 969 extension rows")
    print("policy outputs: 16 files x 500 rows; images: 1000")


if __name__ == "__main__":
    validate()
