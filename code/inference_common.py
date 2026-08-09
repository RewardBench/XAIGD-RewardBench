"""Shared image loading and output helpers for provider runners."""

from __future__ import annotations

import base64
import io
import json
import mimetypes
import os
from pathlib import Path
from typing import Any, Iterable

from PIL import Image

from repo_paths import METADATA_DIR, dataset_id, image_dir


PROMPT = (
    'Start with one word, "real" or "fake", then explain your judgment. '
    "Use only visible image evidence: lighting, shadows, texture, geometry, "
    "anatomy, text, perspective, reflections, and compression or generation artifacts. "
    "Do not use filenames, paths, metadata, labels, or outside knowledge."
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def image_records(input_path: Path) -> list[dict[str, Any]]:
    data = read_json(input_path)
    if not isinstance(data, list):
        raise ValueError(f"{input_path} must contain a JSON list")
    return data


def load_manifest() -> dict[str, str]:
    manifest = os.environ.get("XAIGID_IMAGE_MANIFEST", "").strip()
    if not manifest:
        return {}
    data = read_json(Path(manifest).expanduser())
    if isinstance(data, dict):
        return {str(key): str(value) for key, value in data.items()}
    if isinstance(data, list):
        return {str(row["image_id"]): str(row["path"]) for row in data if row.get("image_id") and row.get("path")}
    raise ValueError("XAIGID_IMAGE_MANIFEST must be a JSON object or list")


def local_image_path(record: dict[str, Any], explicit_dir: str | None = None) -> Path | None:
    manifest = load_manifest()
    image_id = str(record["image_id"])
    if image_id in manifest:
        return Path(manifest[image_id]).expanduser()
    root = image_dir(explicit_dir)
    if root is None:
        return None
    for suffix in ("", ".jpg", ".jpeg", ".png", ".webp"):
        candidate = root / f"{image_id}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def hf_image(record: dict[str, Any], dataset_name: str | None, split: str) -> Image.Image:
    from datasets import load_dataset

    name = dataset_id(dataset_name)
    token = os.environ.get("HF_TOKEN") or None
    dataset = load_dataset(name, split=split, token=token)
    image_column = next(
        (column for column, feature in dataset.features.items() if feature.__class__.__name__ == "Image"),
        None,
    )
    if image_column is None:
        image_column = "image" if "image" in dataset.column_names else None
    if image_column is None or "annotation_id" not in dataset.column_names:
        raise ValueError("HF dataset must provide an image column and annotation_id")
    target = str(record.get("hf_annotation_id", ""))
    for row in dataset:
        if str(row.get("annotation_id", "")) != target:
            continue
        value = row[image_column]
        if isinstance(value, Image.Image):
            return value.convert("RGB")
        if isinstance(value, dict) and value.get("bytes") is not None:
            return Image.open(io.BytesIO(value["bytes"])).convert("RGB")
        if isinstance(value, dict) and value.get("path"):
            return Image.open(value["path"]).convert("RGB")
        if isinstance(value, str):
            return Image.open(value).convert("RGB")
    raise FileNotFoundError(f"No HF image found for annotation_id={target}")


def load_image(record: dict[str, Any], image_root: str | None, dataset_name: str | None, split: str) -> Image.Image:
    path = local_image_path(record, image_root)
    if path is not None:
        return Image.open(path).convert("RGB")
    return hf_image(record, dataset_name, split)


def image_data_uri(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def write_rows(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(rows), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def output_record(record: dict[str, Any], answer: str) -> dict[str, Any]:
    output = {
        "image_id": record["image_id"],
        "image_type": record.get("image_type", "unknown"),
        "answer": answer,
    }
    if record.get("hf_annotation_id") is not None:
        output["hf_annotation_id"] = record["hf_annotation_id"]
    return output
