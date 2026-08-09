# Code

- `analyze_annotations.py` computes annotation coverage, agreement, and choice summaries.
- `analyze_judge_accuracy.py` creates compact summaries of parsed judge choices.
- `analyze_policy_accuracy.py` computes detector accuracy from packaged responses.
- `calculate_elo.py` calculates sequential Elo rankings from human preferences.
- `claudeinf.py` runs an Anthropic vision model on the public image index.
- `data_utils.py` provides shared JSON, label, and verdict helpers.
- `filter_triplets.py` filters invalid or failed triplets from a triplet list.
- `geminiinf.py` runs a Gemini vision model on the public image index.
- `gptinf.py` runs an OpenAI vision model on the public image index.
- `inference_common.py` provides shared image-loading and inference-output helpers.
- `repo_paths.py` defines repository-relative paths and runtime environment helpers.
- `run_analysis.py` regenerates the packaged offline analysis reports.
- `validate_bundle.py` validates release schemas, joins, counts, and privacy constraints.
