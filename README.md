# XAIGID-RewardBench

[GitHub](https://github.com/RewardBench/XAIGID-RewardBench) · [Paper](https://arxiv.org/abs/2511.12363) · [Hugging Face](https://huggingface.co/datasets/MichaelYang469/XAIGID-RewardBench)

XAIGID-RewardBench evaluates multimodal models as judges of explanations for AI-generated image detection.

## Abstract

Conventional, classification-based AI-generated image detection methods cannot explain why an image is considered real or AI-generated in a way a human expert would, reducing their trustworthiness and persuasiveness in real-world applications. XAIGID-RewardBench is the first benchmark for evaluating multimodal large language models as judges of explanations for AI-generated image detection. It contains approximately 4,000 annotated triplets from diverse image generators and detector models. The best model achieves 68.8% four-way accuracy and 86.4% accuracy on clear-winner cases, compared with 59.8% and 87.4% human inter-annotator agreement, respectively. The benchmark also supports analysis of common model failure modes.

## Repository structure

- [`code/`](code/) contains analysis, inference, and validation scripts.
- [`configs/`](configs/) contains DPO experiment configurations.
- [`data/`](data/) contains benchmark artifacts, detector responses, and the camera-real subset.
- [`results/`](results/) contains the reported aggregate metrics.
- [`supplementary/`](supplementary/) contains the detector prompt.
- `requirements.txt` lists dependencies for the benchmark scripts.
- `requirements-dpo.txt` lists optional dependencies for DPO reproduction.

## Citation

```bibtex
@inproceedings{yang2026xaigid,
  title={Explainable AI-Generated Image Detection RewardBench},
  author={Yang, Michael and Deng, Shijian and Doan, William T. and Wang, Kai and Yang, Tianyu and Singh, Harsh and Tian, Yapeng},
  booktitle={Conference on Language Modeling},
  year={2026}
}
```
