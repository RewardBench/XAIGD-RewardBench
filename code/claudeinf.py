#!/usr/bin/env python3
"""Run an Anthropic vision model on the public image index."""

from __future__ import annotations

import argparse
import base64
import io
import os
from pathlib import Path

from inference_common import PROMPT, image_records, load_image, output_record, write_rows
from repo_paths import METADATA_DIR, MODEL_OUTPUTS_DIR, required_env


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=METADATA_DIR / "image_index.json")
    parser.add_argument("--output", type=Path, default=MODEL_OUTPUTS_DIR / "generated_anthropic.json")
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_API_KEY"))
    parser.add_argument("--image-dir")
    parser.add_argument("--dataset-id")
    parser.add_argument("--split", default="train")
    args = parser.parse_args()
    import anthropic

    client = anthropic.Anthropic(api_key=args.api_key or required_env("ANTHROPIC_API_KEY"))
    rows = []
    for record in image_records(args.input):
        image = load_image(record, args.image_dir, args.dataset_id, args.split)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        response = client.messages.create(
            model=args.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": encoded},
                        },
                    ],
                }
            ],
        )
        answer = "\n".join(getattr(block, "text", "") for block in response.content)
        rows.append(output_record(record, answer))
        print(f"completed {record['image_id']}")
    write_rows(args.output, rows)


if __name__ == "__main__":
    main()
