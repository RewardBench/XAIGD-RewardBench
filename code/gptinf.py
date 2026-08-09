#!/usr/bin/env python3
"""Run an OpenAI vision model on the public image index."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from inference_common import PROMPT, image_data_uri, image_records, load_image, output_record, write_rows
from repo_paths import METADATA_DIR, MODEL_OUTPUTS_DIR, required_env


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=METADATA_DIR / "image_index.json")
    parser.add_argument("--output", type=Path, default=MODEL_OUTPUTS_DIR / "generated_openai.json")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"))
    parser.add_argument("--image-dir")
    parser.add_argument("--dataset-id")
    parser.add_argument("--split", default="train")
    args = parser.parse_args()
    from openai import OpenAI

    client = OpenAI(api_key=args.api_key or required_env("OPENAI_API_KEY"))
    rows = []
    for record in image_records(args.input):
        image = load_image(record, args.image_dir, args.dataset_id, args.split)
        response = client.chat.completions.create(
            model=args.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "image_url", "image_url": {"url": image_data_uri(image)}},
                    ],
                }
            ],
        )
        rows.append(output_record(record, response.choices[0].message.content or ""))
        print(f"completed {record['image_id']}")
    write_rows(args.output, rows)


if __name__ == "__main__":
    main()
