# Akshara — Telugu Handwriting OCR

A Telugu transcription and human-review studio backed by a completed adaptation study of **IndicOCR**. Upload word images to your local GPU service, preserve raw predictions, review/edit Telugu text, and export TXT, Markdown or JSON. The analysis dashboard explains measured improvements and the limits of comparisons with other OCR systems.

**Built with IndicOCR from Bodhan AI / AI4Bharat.** This independent adaptation is not endorsed by the upstream organizations.

## Website and model

**[Live website](https://akshara-ocr-seven.vercel.app/) ? [Analysis](https://akshara-ocr-seven.vercel.app/analysis.html) ? [Completed study dashboard](https://akshara-ocr-seven.vercel.app/progress.html) ? [GitHub source](https://github.com/Thanujgthub/akshara-ocr)**

**[Hugging Face selected model](https://huggingface.co/thanujhf/akshara-telugu-handwriting-ocr) ? [Hugging Face Space](https://huggingface.co/spaces/thanujhf/akshara-ocr-studio)**

GitHub is public at the owner?s request. The Vercel URL is also recorded in the repository?s About / Website field. Vercel and the Hugging Face static Space host the website and completed results; they do **not** contain a running GPU inference endpoint. The selected adapter is a separate Hugging Face model release.

Locally: [Studio](http://127.0.0.1:8765/) · [Full analysis](http://127.0.0.1:8765/analysis.html) · [Completed dashboard](http://127.0.0.1:8765/progress.html)

## What we did

1. Preserved the original checkpoint, tokenizer, processor and historical pilot.
2. Audited image/label files, duplicates and source-document groups, then froze **25,000 training / 5,000 validation / 3,000 final-test** pairs.
3. Verified native BF16, real-image interrupted/resumed recovery and actual GPU throughput.
4. Selected pilot initialization using validation and completed **one effective training epoch**, with **6,250 optimizer updates**: rank-8 q/v LoRA, learning rate `1e-5`, effective batch 4, seed 42, no augmentation or pseudo-label claims.
5. Locked selection using validation alone, then evaluated original, pilot and selected models on identical sealed final inputs with deterministic decoding.
6. Preserved raw predictions, hashes, optimizer/scheduler/RNG recovery state, environment versions, subgroup metrics and paired uncertainty intervals.
7. Connected the selected adapter to the local API and checked desktop/mobile behavior with Playwright.

**The epoch is complete.** Installation and deployment do not restart training. Smoke/benchmark adapters are not the selected model.

## Final results and analysis

All three variants used the same 3,000 held-out Telugu word crops. Lower CER/WER and higher exact match are better.

| Model | Grapheme CER ↓ | WER ↓ | Exact-word match ↑ |
|---|---:|---:|---:|
| Original IndicOCR | 12.7839% | 42.2667% | 66.4333% |
| Preserved pilot | 12.1907% | 40.1667% | 67.4667% |
| **Selected Akshara adapter** | **7.4534%** | **24.4000%** | **76.2000%** |

Akshara got **2,286/3,000 complete words correct**, 293 more than the original. Exact-word gain: **9.7667 percentage points**, paired 95% interval **[8.3444, 11.1631]**. Bootstrap: 2,000 repetitions over 128 source-document/duplicate components, not verified independent writers.

CER counts Unicode grapheme clusters; WER counts whitespace-separated tokens; exact match requires the whole prediction to match. Raw and explicitly NFC-normalized aggregate values coincide on this sample. Spelling/numerals were not silently repaired. Validation exact match **81.38%** is a separate selection result; **76.20%** is the final-test headline.

The Windows RTX 3050 Laptop 4 GB evaluation measured **0.6274 s** median generation time per crop, **0.9228 s** p95, and approximately **1.80 GiB** peak allocated GPU memory. Generation time excludes upload/input processing. These are **local Windows results, not Colab/cloud results**.

Read the [full study report](reports/akshara-capped-study-20261015-v1.md), [aggregate JSON](dist/capped-study-results-20261015.json) and [metrics CSV](dist/capped-study-metrics-20261015.csv). The website separates vendor handwriting benchmarks, document parsing and competitions: different datasets/scores cannot produce one global ranking. **No worldwide rank, 99% accuracy or market leadership is established.**

## Prerequisites

Website/report only: Git, **Node.js 20+** to build and Python 3 to preview. No model/GPU is needed to read reports, import/edit text or export files.

For measured model inference:

- Windows, **Python 3.12**, Git and an NVIDIA driver compatible with CUDA **12.8**.
- A CUDA GPU with **native BF16**. Verified hardware: RTX 3050 Laptop 4 GB, 16 GB system RAM; adequate free memory is still required.
- Authorized original `bodhan-ai/indic-ocr` revision **`cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25`** and the selected adapter release.
- Several GB of free disk space for environment/model/cache. Base weights and training images are not embedded in Git.

Exact measured versions: [requirements-gpu-lock.txt](requirements-gpu-lock.txt). Other operating systems/GPUs are not certified as numerically identical. Do not silently substitute FP16 or another checkpoint.

## Step-by-step installation — Windows PowerShell

### 1. Clone

```powershell
New-Item -ItemType Directory -Force D:/CODEX/OCR | Out-Null
Set-Location D:/CODEX/OCR
git clone https://github.com/Thanujgthub/akshara-ocr.git
Set-Location akshara-ocr
```

### 2. Create an isolated environment

On a new computer, use fresh folders. On the original research computer, reuse the preserved environment/model/run folders.

```powershell
py -3.12 -m venv D:/OCR/runtime/akshara-public-venv
$ocrPython = 'D:/OCR/runtime/akshara-public-venv/Scripts/python.exe'
$env:HF_HOME = 'D:/OCR/cache/huggingface'
$env:PIP_CACHE_DIR = 'D:/OCR/cache/pip'
& $ocrPython -m pip install --upgrade pip
& $ocrPython -m pip install -r requirements-gpu-lock.txt --extra-index-url https://download.pytorch.org/whl/cu128
```

### 3. Authenticate and download

Read the [base model license](licenses/Indic-Open-Model-License-v1.0.md). Sign in through your own browser; never put tokens in source or chat.

```powershell
& $ocrPython -m huggingface_hub.cli.hf auth login
& $ocrPython -m huggingface_hub.cli.hf download bodhan-ai/indic-ocr --revision cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25 --local-dir D:/OCR/models/indic-ocr-pinned
```

Download the pinned selected Hugging Face model release:

```powershell
& $ocrPython -m huggingface_hub.cli.hf download thanujhf/akshara-telugu-handwriting-ocr --revision 329268ff4169b496b2e6727bfe421cc76bfb2be8 --local-dir D:/OCR/releases/akshara-selected
```
 Retain the complete structure: `adapter/`, `checksums.json`, `full-config.json`, `model-provenance.json` and metadata. Never substitute smoke/benchmark weights. The pinned release includes the original export metadata and unchanged selected weights.

### 4. Verify and launch

```powershell
& $ocrPython scripts/serve_selected.py --base D:/OCR/models/indic-ocr-pinned --release D:/OCR/releases/akshara-selected --verify-only
& $ocrPython scripts/serve_selected.py --base D:/OCR/models/indic-ocr-pinned --release D:/OCR/releases/akshara-selected
```

The launcher verifies the original **31 file hashes**, selected release checksums, native BF16 and port ownership. It preserves precision, binds only to loopback and invokes the existing API. Stop if verification fails; do not replace the frozen base with another revision.

Open **http://127.0.0.1:8765/**. Upload a Telugu word crop, keep **Word crop** mode and the trained adapter, transcribe, then review against the image. The first request loads the model; a health response alone is not evidence of successful inference.

On the original machine use `./Start-AksharaSelected.ps1` after checking no API owns port 8765. The portable launcher does not recreate the original live recovery monitor; the analysis and published dashboard retain the completed results.

### 5. Call the API

```powershell
curl.exe -F 'file=@word.png' -F 'mode=word' -F 'variant=adapted' http://127.0.0.1:8765/api/predict
```

Responses preserve raw Markdown and report model identity, token/diagnostic metadata and review requirements. Page mode is experimental; word results do not establish page accuracy. Confidence is uncalibrated.

### 6. Run software checks

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
& $ocrPython -m unittest discover -s tests -q
```

The study recorded **85 software tests**, **64/64 actual API parity requests** on 32 predeclared validation crops, and headed desktop/mobile Playwright checks. Publication added three reproducibility checks: **88 total software tests passed**, and both deployed sites passed desktop/mobile Playwright checks and actual CSV downloads. Software pass counts are not model accuracy. Thread limits avoid excessive Windows BLAS memory allocation during tests.

## Website-only preview and deployment

```powershell
node scripts/build_public_site.mjs
py -m http.server 8787 --directory public-release --bind 127.0.0.1
```

Open `http://127.0.0.1:8787/`, `/analysis.html` or `/progress.html`. The build explicitly labels the completed results snapshot and never pretends a GPU is connected. It refuses to overwrite existing output; use a fresh directory for later builds. See [deployment instructions](docs/DEPLOYMENT.md) for Vercel and Hugging Face.

## Project map

| Path | Purpose |
|---|---|
| `dist/` | Studio, analysis, aggregate downloads and preserved pilot assets |
| `ocr/` | Inference, metrics, dataset checks, training and recovery modules |
| `scripts/serve_selected.py` | Verify released checkpoint and start local inference |
| `scripts/build_public_site.mjs` | Build static website and completed-study snapshot |
| `tests/`, `reports/` | Software checks, measured reports and evidence receipts |
| `notebooks/`, `COLAB_MIGRATION.md` | Preserved cloud handoff; no completed Colab run claimed |
| `PROJECT_STATE.md`, `WORK_LOG.md`, handoffs | Current state and historical research records |

Historical 80,083-example/two-epoch plans are retired. Do not launch their training scripts. Training reproduction needs separately licensed data, frozen manifests and every preflight/recovery requirement in `AGENTS.md`; it is unnecessary for installation/inference.

## Limitations and attribution

- These are word crops, not whole pages/layouts. Other datasets, camera images and unseen-writer robustness remain unbenchmarked.
- Writer identity and original pretraining overlap are unknown. Technical file/label checks do not equal complete human semantic verification. One seed/epoch does not establish between-seed robustness.
- **714 final crops were not exact matches.** Diagnostic flags are heuristics; zero refusal/contamination flags does not mean zero transcription errors. Constant-pixel abstention does not prove general blank-image detection.
- Akshara is first among its three local variants by final CER, with no established global position. External rankings need matching datasets and scoring.
- Dataset: [IIIT Hyderabad Telugu handwriting words](https://ilocr.iiit.ac.in/dataset/23/), stated [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Preserved example crops retain that source; no newly human-verified labels are claimed.
- Base model and selected derivative use the **[Indic Open Model License v1.0](licenses/Indic-Open-Model-License-v1.0.md)**, not an alternative MIT/Apache license. Other third-party components retain their own terms. No upstream endorsement is implied.
- This is a selected model/source/report publication, not a complete offsite backup of every raw dataset/recovery artifact.

The [pre-publication README](docs/README-before-publication-20261015.md) is preserved as history.
