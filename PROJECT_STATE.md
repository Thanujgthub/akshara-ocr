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

## Verified continuation — 13 October

Six matched 287-word prompt/preprocessing validation comparisons completed. Literal Telugu + official preprocessing selected on original-model validation only. Rank-8 control completed 1,000 words / 250 updates: raw/NFC CER 8.6192%, WER 29.2683%, exact 74.5645%. Matched-policy grouped paired CER-reduction interval [-0.319, +0.641] percentage points is inconclusive. The original pilot test remains the preserved independent baseline. Rank-16 trial is now active, followed by q/k/v/o, LR and augmentation trials; full 80,083-word training and sealed 1,016-word final testing are still pending.

A live code update exposed an analysis-to-training import dependency after control predictions and metrics were saved. Failure records are preserved under recovery/import-error-20261013; moved atomic JSON I/O to a model-independent module, added regression coverage, resumed at the saved optimizer boundary with no replayed training words. Source snapshot after recovery is source-snapshots/20261013T023741Z; it does not claim to describe the earlier control process throughout its execution. Do not edit training modules during an active process.

Local research monitor shows recent speed excluding long pauses; not GPU kernel timing. New /review-v2 shows 488 quarantined training crops and 127 preserved pilot validation errors. Human review annotations are separate versioned records, never automatic training inputs. No final-test examples exposed. Strict exactly-uniform RGB input abstention preserves faint pixel variation; no calibrated confidence or spelling/context repair. Twenty-six software tests pass. API inference remains paused during GPU research.

Resume handles for this session: pipeline tool session 50982 (pipeline-resume-20261013.log); API tool session 44621; CPU uniform-training audit session 38282. Verify OS commands before killing/restarting anything.

## Latest automated milestone
{
  "status": "running",
  "stage": "Controlled training trial: rank16",
  "updated_utc": "2026-10-13T02:35:34Z",
  "note": "1,000 training words; settings selected on validation only.",
  "experiment_directory": "D:\\OCR\\runs\\word-scale-v2\\trials\\rank16"
}
