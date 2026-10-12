# Project state — 13 October 2026

## Preserved baseline
Original bodhan-ai/indic-ocr revision cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25. Original tokenizer/processor/chat template and official crop clamp. EOS 262146, PAD 262144. Pilot 1,000 train / 500 validation / 500 test, rank-8 q/v LoRA. Test CER 15.93% to 15.35%, WER 43.00% to 41.60%, exact 66.20% to 68.20%. Paired CER-reduction interval [-0.96, 1.79] pp: inconclusive.

## Active milestone
Full word-archive audit completed: 118,515 labeled pairs decoded/hashed. D:/OCR/research-v2; log D:/OCR/full-word-audit.log. Prior datasets/runs untouched. All-label parsing and image/hash checks are technical verification, not a claim of human label verification.

## Prioritized execution plan
1. Snapshot code/model contracts, old frozen manifests and logs; audit all paired word members, labels, duplicates and source documents.
2. Freeze train/validation/new final test with holdout precedence and exclude all old pilot groups from the new final test. Seal final-test manifest before experiments. Preserve old frozen test without further tuning on it.
3. Test Telugu literal prompt, raw-output diagnostics, Unicode metrics and conservative uncertainty; review validation error images and tokenization. No destructive cleanup or guessed no-text output.
4. Run matched validation-only prompt/preprocessing trials, then short one-variable LoRA trials (rank, targets, LR, augmentation). Measure memory/time and use validation-only selection.
5. Train selected settings on all eligible word training examples, checkpoint with resumable optimizer/RNG state; validate per epoch and early-stop. Only then evaluate selected model and matched baseline on the new sealed final test, with grouped paired intervals.
6. Separately investigate page/line labels and licensing. No page training while terms remain unresolved. Context suggestions need real sentence/line supervision and a separate suggestion-quality evaluation.

## Constraints and remaining evidence
RTX 3050 4 GB, 16 GB RAM, Windows. Pilot throughput ~1.65 s/word (~37 h/80k-word epoch), estimate only. API model occupies ~2 GB VRAM and must unload before GPU experiments. Laptop must remain awake with sufficient cooling/power; no system power changes authorized or made.
Word source states CC BY 4.0: https://ilocr.iiit.ac.in/dataset/23/. Page terms unresolved. Source-reported 11 writers does not map individual archive paths to verified writer IDs. Pretraining overlap unknown; full human label review outstanding.

## Resume
Use D:/OCR/runtime/venv/Scripts/python.exe. Read newest run status/failure before launching anything. Do not start a second audit/trainer or use test results for selection. Repository package and original UI remain functional; GPU inference pauses during training.

## Latest automated milestone
{
  "status": "running",
  "stage": "Validation: curated-original-telugu_literal-white_margin",
  "updated_utc": "2026-10-12T21:45:31Z",
  "note": "",
  "experiment_directory": "D:\\OCR\\runs\\word-scale-v2\\experiments\\curated-original-telugu_literal-white_margin"
}
