"""Repository-relative paths and external runtime configuration."""

from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
TRIPLETS_DIR = DATA_DIR / "triplets"
ANNOTATIONS_DIR = DATA_DIR / "annotations"
MODEL_OUTPUTS_DIR = DATA_DIR / "model_outputs"
METADATA_DIR = DATA_DIR / "metadata"
RESULTS_DIR = REPO_ROOT / "results"


def env_path(name: str, default: Path | None = None) -> Path | None:
    value = os.environ.get(name)
    if value:
        return Path(value).expanduser()
    return default


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Set {name} before running this network-dependent command")
    return value


def dataset_id(explicit: str | None = None) -> str:
    return (explicit or os.environ.get("XAIGID_DATASET_ID", "")).strip() or required_env(
        "XAIGID_DATASET_ID"
    )


def image_dir(explicit: str | None = None) -> Path | None:
    return env_path("XAIGID_IMAGE_DIR", Path(explicit).expanduser() if explicit else None)
