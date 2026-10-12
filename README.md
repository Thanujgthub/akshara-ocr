# Akshara · Telugu OCR Studio

A responsive Telugu transcription and review website, local REST API bridge, and tested data/evaluation toolkit. It is usable today for manual transcription, imported OCR review, batch image inspection, exports and text comparison. **It does not include a trained Telugu model, measured OCR accuracy, or a verified training corpus.** The typeset sample is illustrative.

## Windows setup

From this project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m uvicorn ocr.server:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. No model is needed for the review tools. The model endpoint returns 503 when unavailable; it never returns sample text for an uploaded image.

## What works

- Multi-image upload queue (JPEG/PNG/WebP, maximum 20 MB each), original preview, zoom and view-only rotation.
- Editable Telugu text, immutable raw result, separate NFC normalization, human review flag.
- Import official OCR Markdown/blocks JSON or an exported review bundle; plain UTF-8 TXT, Markdown and JSON exports.
- Searchable device-local library; images are never persisted in the library. JSON bundles retain sample/review/model metadata.
- Grapheme CER, WER and exact text comparison; source registry and developer API reference.
- Deterministic grouped train/validation/test splitting, SHA-256 freeze files, corrupt/duplicate/missing label audit, visual near-duplicate candidate grouping and source-supplied raw/NFC labels.
- Light/dark theme, responsive layout and keyboard-accessible form controls.

## Connect real IndicOCR

1. Review and accept the model's terms at https://huggingface.co/bodhan-ai/indic-ocr yourself. Hosting the model for others has separate conditions; the hosted preview contains no model inference service.
2. Download the official snapshot at the recorded revision, following its installation documentation on Linux CUDA. Do not install its GPU stack into the lightweight Windows toolkit environment.
3. Install this project's API requirements in that model-compatible environment. Set `INDIC_OCR_REPO` to the downloaded snapshot and `INDIC_OCR_REVISION` to its exact commit. Run the API in that environment. The documented snapshot Python API is implemented in `ocr/model.py`; actual loading has not been tested here.
4. Use **Model connection** in the UI. `GET /api/health` checks snapshot presence, not proven model compatibility. The first prediction performs the actual load.

The local site and API on the same origin avoid browser mixed-content restrictions. The static hosted site may not reach a local HTTP API. To use a remote API, serve it over HTTPS with your own authentication and set `OCR_ALLOWED_ORIGINS` to the specific frontend origin. The included server is designed for loopback development, not public unauthenticated hosting. No credential is collected by the browser.

## Prepare authorized data

```powershell
python -m ocr.cli audit --root data/my-corpus --source my-corpus --license-ref CC-BY-4.0 --granularity page --output manifests/all.jsonl
python -m ocr.cli split --manifest manifests/all.jsonl --output manifests
python -m ocr.cli evaluate --input predictions.jsonl --output reports/metrics.json
```

Page inputs use same-stem `.txt` labels. For word archives, pass `--labels-tsv train_gt.txt`; paths must match the image paths relative to `--root`. Labels must be tab-separated. Raw text stays unchanged. Telugu presence is a heuristic, not proof of correct language or handwriting: human/domain review is required. Visual hashes conservatively group near-duplicate candidates; review false positives. Writer-disjointness cannot be inferred from filenames and is reported false. Supply authoritative writer/document group IDs in the audited manifest before splitting when available. Split each granularity separately. Split assignment can exceed validation/test targets to preserve groups and reports train shortfalls honestly.

The split command creates immutable-by-convention JSONL files and a checksum ledger; store these read-only before model selection. It does not enforce organizational test-label sealing. Never tune on test labels.

Evaluation input is JSONL: each row has `example_id`, `reference`, `prediction`, `source_dataset`, `granularity`. Empty reference metrics are undefined (`null`), not silently zero. The corpus report includes micro CER/WER, macro CER, raw exact match and per-example metrics. Text comparisons alone do not prove page-level or model accuracy. No bootstrap interval, latency/VRAM benchmark or failure-case image audit has been run.

`python -m ocr.download --source SOURCE_ID --output data/archive.zip` only downloads registry records explicitly approved for the project's scope. It refuses HTML access gates, verifies a published hash when available, and calculates SHA-256 otherwise. It does not extract archives or bypass authentication. Registry approval is a human licensing decision, not a download success flag.

## Cloud model setup

See `notebooks/colab_train.ipynb` for an access/environment checkpoint and baseline bridge. It is a **baseline/setup notebook, not an executed recognizer training recipe**. See `docs/architecture_decision.md` for the mandatory training gate. The official repo trains only layout. A custom recognizer LoRA path must be verified against the actual model, processor and tokenizer before it can be implemented honestly.

## Privacy and assets

Files are sent only when Transcribe is pressed and a server URL is configured. Local library uses browser localStorage and can be cleared; it is not encrypted. Images are temporary in API requests and deleted after processing. Export bundles can contain document text; keep them private as appropriate. No private images/data/model weights are in the published assets. Google Fonts is optional presentation styling; the app has system fallbacks and does not upload documents to Google Fonts.

See `HANDOFF.md` for actual verification and incomplete research deliverables.
