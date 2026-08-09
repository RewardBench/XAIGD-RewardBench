"""Small schema helpers shared by the public analysis scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def model_name(value: Any) -> str:
    name = str(value or "").replace(".json", "")
    return name[2:] if name[:2] in {"FI", "RI"} else name


def normalize_choice(value: Any) -> str | None:
    choice = str(value or "").strip().lower()
    return {
        "response_1_better": "response_1_better",
        "response_2_better": "response_2_better",
        "caption_1_better": "response_1_better",
        "caption_2_better": "response_2_better",
        "response_1": "response_1_better",
        "response_2": "response_2_better",
        "tie": "tie",
        "both_good": "tie",
        "both_bad": "both_bad",
    }.get(choice)


def score_for_choice(choice: Any, include_neutral: bool = False) -> float | None:
    normalized = normalize_choice(choice)
    if normalized == "response_1_better":
        return 1.0
    if normalized == "response_2_better":
        return 0.0
    if include_neutral and normalized in {"tie", "both_bad"}:
        return 0.5
    return None


def parse_verdict(answer: Any) -> str | None:
    if not isinstance(answer, str):
        return None
    match = re.match(r"^\s*[#>*_`~\-\s\"']*(real|fake)\b", answer, re.IGNORECASE)
    return match.group(1).lower() if match else None


def triplet_fingerprint(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return tuple(str(row.get(key, "")) for key in ("image_id", "caption_1", "caption_2", "csv1", "csv2"))
