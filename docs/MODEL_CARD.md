---
language:
- te
license: other
license_name: indic-open-model-license-v1.0
license_link: LICENSE.md
base_model: bodhan-ai/indic-ocr
library_name: peft
tags:
- ocr
- handwriting-recognition
- telugu
- lora
- image-to-text
---

# Akshara Telugu Handwriting OCR — selected adapter

**Built with IndicOCR from Bodhan AI / AI4Bharat.** This independent research adaptation is not endorsed by the upstream organizations. This repository contains the exact validation-selected **LoRA adapter**, not a merged base model or a running inference endpoint.

[Hugging Face Space](https://huggingface.co/spaces/thanujhf/akshara-ocr-studio) ? [Website](https://akshara-ocr-seven.vercel.app/) ? [Measured analysis](https://akshara-ocr-seven.vercel.app/analysis.html)

## Training and selection

One effective epoch over a frozen 25,000-example Telugu word-image training set; 5,000 validation examples selected pilot initialization and the candidate before the sealed 3,000-example final comparison. Rank-8 q/v LoRA, learning rate 1e-5, microbatch 1, accumulation 4, seed 42, native BF16, 6,250 updates; no augmentation. Completed locally on Windows / RTX 3050 Laptop 4 GB, not Colab. No extra epoch is pending.

## Measured final results

| Variant | Grapheme CER ↓ | WER ↓ | Whole-word exact match ↑ |
|---|---:|---:|---:|
| Original IndicOCR | 12.7839% | 42.2667% | 66.4333% |
| Preserved pilot | 12.1907% | 40.1667% | 67.4667% |
| **This selected adapter** | **7.4534%** | **24.4000%** | **76.2000%** |

Identical 3,000 final word crops, deterministic decoding. Raw/NFC aggregate pairs coincide. Candidate 2,286/3,000 exact; 714 not exact. Exact-match improvement over original 9.7667 percentage points, paired 95% interval [8.3444, 11.1631]; 2,000 bootstrap repetitions, seed 42, 128 source-document/duplicate groups, not verified independent writers. Validation exact81.38% is separate from final76.20%.

Candidate median generation0.6274s, p95 0.9228s, peak allocated GPU memory approximately1.80GiB. These exclude HTTP/upload/input processing and are not universal hardware speed claims. The original study passed85 software checks and64/64 actual local API parity comparisons on32 predeclared validation crops; these are not hosted inference checks.

## Loading the correct model

Use the existing source and Windows installation instructions at **https://github.com/Thanujgthub/akshara-ocr**. Download this repository in full with `hf download thanujhf/akshara-telugu-handwriting-ocr --local-dir D:/OCR/releases/akshara-selected` (substitute this page's repository ID).

Obtain `bodhan-ai/indic-ocr` at **cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25**, including its shipped tokenizer, processor, root Python modules and original weights. The adapter's original `base_model_name_or_path` contains a preserved Windows provenance path. **Do not use AutoModel on this adapter repository or interpret that path as an alternative downloadable base.** The existing loader explicitly supplies the pinned base and `adapter/` subfolder to PEFT.

From the source checkout, after installing the pinned environment:

```powershell
python scripts/serve_selected.py --base D:/OCR/models/indic-ocr-pinned --release D:/OCR/releases/akshara-selected --verify-only
python scripts/serve_selected.py --base D:/OCR/models/indic-ocr-pinned --release D:/OCR/releases/akshara-selected
```

Open http://127.0.0.1:8765 and use word-crop mode. Native CUDA BF16 is required; no silent precision conversion or tokenizer substitution. The model uses the existing literal Telugu prompt, official preprocessing, greedy decoding and preserved raw strings. Human corrections stay separate.

## Provenance and integrity

Original31-file provenance: `model-provenance.json`. Frozen selected export identity: `selection.json`; expected SHA256 **32e18a5c4a29f3855bf323f51944a7ccae53659f60982d3d40b284960e63f00b**. Adapter weights SHA256 **7d64d5371be010c0c1fe15936b44f1e1539c2c52b80d2e3c957b53c4c91ea1e9**.

`checksums.json` covers the original export files; those files remain byte-identical. Top-level model card, license and aggregate human-readable report are publication additions outside that original checksum list. The latest resumable optimizer checkpoint remains a separate preserved local artifact; this is an inference adapter release, not the full recovery backup. Canonical raw datasets/labels/predictions are not uploaded here.

## Limits and intended use

Research and human-assisted transcription of isolated Telugu handwritten words. Writer identity, original pretraining overlap, complete human semantic label verification, other-dataset robustness and page-level accuracy remain unknown. One seed/epoch does not establish robustness across seeds. Confidence and output-warning heuristics are uncalibrated. Uniform-pixel abstention is not general blank/unreadable-image recognition. No worldwide ranking or market-leadership claim follows from these results. External vendor scores use different inputs and metrics.

Data source: [IIIT Hyderabad Telugu handwriting words](https://ilocr.iiit.ac.in/dataset/23/), stated [CC BY4.0](https://creativecommons.org/licenses/by/4.0/). These are source-provided transcriptions, not newly human-verified labels.

The base and this derivative use the exact **Indic Open Model License v1.0**, included unmodified in `LICENSE.md`. No MIT/Apache relicensing of the derivative is claimed. Consult its conditions for distribution and hosted access. Original weights are obtained separately from their publisher.
