# Akshara · Telugu handwriting OCR studio

A clean transcription/review website with a local IndicOCR API, executed word-recognizer LoRA experiment, frozen data manifests and measured original-versus-adapted test results. Read `reports/evaluation.md` for the actual results and limitations. Word-crop performance does not establish full-page quality.

## Open on this computer

From this project folder in PowerShell:

```powershell
.\Start-Akshara.ps1
```

Open http://127.0.0.1:8765 for the studio, or http://127.0.0.1:8765/research.html for training/results. The local service uses the installed D:/OCR/runtime/venv environment, authorized base weights in D:/OCR/models/indic-ocr and saved word adapter in D:/OCR/runs/word-pilot-v1/trained/adapter. Set INDIC_OCR_REPO / INDIC_OCR_ADAPTER / OCR_DEVICE to override these locations. OCR_RUN_ROOT and OCR_DATA_ROOT configure the dashboard paths. Start-Akshara.ps1 uses this computer's runtime location; adjust its ocrPython variable on another machine.

The study reserves the GPU while training/testing; new inference returns 409 until it completes. Local uploads are temporary. Run on loopback only. The hosted private site contains the interface and exported results, while GPU inference runs locally. A hosted HTTPS page may not connect to a local HTTP API; use the local studio for inference.

## Studio tools

- Batch JPG/PNG/WebP uploads, original image preview, zoom and view rotation.
- Word-crop mode for the measured adapter; experimental full-page layout/block reconstruction.
- Editable Telugu text beside immutable raw output, explicit NFC normalization and human review flag.
- TXT, Markdown and JSON export; searchable browser-local library and OCR JSON import.
- CER/WER text comparison, dataset registry, REST API and live study dashboard.
- Light/dark presentation, responsive layouts and accessible labeled controls.

The built-in typeset letter remains an illustrative editor sample. Real test images and unedited predictions appear on the separate research page. Layout scores are not transcription confidence. The application does not invent text when inference fails.

## Reproduce the environment

Python 3.12, NVIDIA CUDA driver, and the exact original gated model are required for the GPU path. `requirements-gpu-lock.txt` records the installed versions, including Torch 2.11.0+cu128, torchvision 0.26.0+cu128, Transformers 5.7.0, PEFT 0.21.2 and Accelerate 1.15.0. Install Torch/torchvision from the official CUDA 12.8 wheel index, then install/sync the remaining lock file with that extra index available. The CPU data/review toolkit can use requirements.txt; CPU training was not viable under this laptop's initial memory pressure.

```powershell
uv venv --python 3.12 D:/OCR/runtime/venv
uv pip install --python D:/OCR/runtime/venv/Scripts/python.exe torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
uv pip sync --python D:/OCR/runtime/venv/Scripts/python.exe requirements-gpu-lock.txt --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match
```

Review/accept the base model terms through your own Hugging Face account, and download revision cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25 of bodhan-ai/indic-ocr, including shipped root Python modules, tokenizer/processor and weights. The original license accompanies the local adapter deliverable. Third-party hosted access is governed by that license. No token belongs in source, logs or browser localStorage.

## Inference CLI and REST API

```powershell
$env:INDIC_OCR_REPO='D:/OCR/models/indic-ocr'
$env:INDIC_OCR_REVISION='cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25'
$env:INDIC_OCR_ADAPTER='D:/OCR/runs/word-pilot-v1/trained/adapter'
& D:/OCR/runtime/venv/Scripts/python.exe -m ocr.cli predict --image word.jpg --mode word --output prediction.json
curl.exe -F 'file=@word.jpg' -F mode=word http://127.0.0.1:8765/api/predict
```

Use mode=page for the official layout → cropped-block recognition → reconstruction pipeline. Page results are experimental and have no measured page benchmark in this pilot. Unset INDIC_OCR_ADAPTER to use unchanged original recognizer weights. Keep the raw Markdown unchanged for evaluation; human corrections belong in the separate reviewed transcription.

## Data and experiments

```powershell
& D:/OCR/runtime/venv/Scripts/python.exe -m ocr.audit_archives --root D:/OCR --output D:/OCR/research --word-limit 8000
& D:/OCR/runtime/venv/Scripts/python.exe -m ocr.experiment probe --manifest D:/OCR/research/manifests/word_train.jsonl --limit 4 --steps 64 --output D:/OCR/runs/new-probe
& D:/OCR/runtime/venv/Scripts/python.exe -m ocr.experiment train --manifest D:/OCR/runs/word-pilot-v1/train.jsonl --validation D:/OCR/runs/word-pilot-v1/validation.jsonl --output D:/OCR/runs/new-training
& D:/OCR/runtime/venv/Scripts/python.exe -m ocr.experiment evaluate --manifest D:/OCR/runs/word-pilot-v1/test.jsonl --output D:/OCR/runs/new-baseline
& D:/OCR/runtime/venv/Scripts/python.exe -m ocr.experiment evaluate --manifest D:/OCR/runs/word-pilot-v1/test.jsonl --adapter D:/OCR/runs/new-training/adapter --output D:/OCR/runs/new-adapted
& D:/OCR/runtime/venv/Scripts/python.exe -m unittest discover -s tests -v
```

Do not rerun audit or overwrite frozen study outputs during an experiment. Use a separate output directory for new audits and new runs. The audit's word-limit is a bounded sample count per official split, not a claim that the full archives have been verified. Review dataset versions, source labels, visual duplicate candidates and writer metadata before larger studies. Original images/labels/weights remain unchanged.

The original pilot experiment CLI also accepts --repo, --data-root, --device, --epochs, --limit and --adapter. It uses the official tokenizer, template, prompt and preprocessing. Checkpoints and optimizer state are saved every 100 examples; automatic interrupted-run resume is not implemented. A clean rerun is reproducible by seed; the same GPU/kernel environment is needed for strict numerical parity. The Colab notebook is an optional launch path, not a claim of a cloud run.

## Evidence and limits

The results deliverable contains 1,000 / 500 / 500 frozen manifests, raw prediction JSONL, metrics, source-document bootstrap intervals, per-length/error breakdowns, loss logs and model provenance. Source-provided labels are not newly human-verified. Group isolation is based on source-document paths and conservative near-duplicate candidates; verified writer identity and original-model pretraining overlap are unavailable. Page data remains audit-only pending clarification of its terms. No page/line alignment, historical-domain adaptation or claim of production accuracy is made.

Dataset attribution: IIIT Hyderabad, IIIT-INDIC-HW-WORDS Telugu, CC BY 4.0 stated at https://ilocr.iiit.ac.in/dataset/23/. Page source: https://ilocr.iiit.ac.in/icdar_2024_hwd/dataset.html. See data_registry and reports/data_audit.md for actual counts and version discrepancies.

Model connection includes an original/adapted weight selector; the REST/CLI variant parameter accepts original or adapted. API parity and browser transcription were verified on a held-out word.

## Scale research and validation-selected handoff

Resume the existing scale pipeline with `./Resume-Scale-Training.ps1`; it refuses a second active pipeline and restores optimizer, scheduler and RNG checkpoints. It preserves the original model and frozen pilot. New data/runs live under D:/OCR/research-v2 and D:/OCR/runs/word-scale-v2. Do not edit training modules while a process is active.

Open http://127.0.0.1:8765/research-v2 for measured progress and /review-v2 for separate versioned annotations. Word training uses 80,083 eligible image/label pairs with 11,723 distinct labels; source labels are not all human verified. Trial results are exploratory validation evidence, not independent test performance. Inference remains paused while GPU experiments run.

After completed full training, validation selection and sealed final testing, use `./Start-Selected-Scale-Model.ps1`. It refuses unfinished runs, serves the validation-selected original/pilot/scale variant and applies the selected word prompt/preprocessing. Original and adapted selectors use identical selected input policy. Actual GPU parity of the new word API path remains to be checked after training; unit checks establish explicit greedy/EOS/PAD settings and raw whitespace preservation only. Page inference retains the official experimental pipeline and has no measured page benchmark.

Word API responses include uncertainty flags, truncation, generated token IDs and resource abstention where applicable. No-text is not inferred from an empty abstention. Studio JSON schema 1.1 retains these diagnostics and model identity in queue/library/export records. Text confidence is not calibrated. Literal transcription is never silently spelling-corrected or replaced with contextual guesses.
