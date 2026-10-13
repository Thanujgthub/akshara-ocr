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

Local research monitor shows recent speed excluding long pauses; not GPU kernel timing. New /review-v2 shows 488 quarantined training crops and 127 preserved pilot validation errors. Human review annotations are separate versioned records, never automatic training inputs. No final-test examples exposed. Strict exactly-uniform RGB input abstention preserves faint pixel variation; no calibrated confidence or spelling/context repair. Full exact-uniform pixel audit completed: 80,083 / 80,083 curated training images, zero uniform images and zero read errors, 1,025 seconds. This is not human label verification. Twenty-six software tests pass. API inference remains paused during GPU research.

Resume handles for this session: pipeline tool session 50982 (pipeline-resume-20261013.log); API tool session 44621; CPU uniform-training audit session 38282. Verify OS commands before killing/restarting anything.

## Coverage and error diagnosis continuation

Read-only scans of all 80,083 train / 13,462 validation labels completed, frozen hashes checked. Distinct train labels 11,723; numeral-bearing train examples 175, full-validation 29, trial-validation zero. Observed digits are Telugu, no Arabic numerals. No empty/NFC-change/orphan-mark/control-or-replacement/non-Telugu-letter source labels under the audit definitions. This does not verify image/label semantic alignment. Train/validation share zero example/file-hash/pixel-hash/leakage-group IDs.

New diagnostics/control-v2 review queue has 87 matched 287-subset disagreements, retaining original/literal/control raw outputs and token IDs; four control fewer-edit cases, one more-edit case, 282 same-edits. Twelve crop images visually inspected; pending human source-label review. Current /review-v2 offers these 87 cases with expandable matched outputs. No final-test data exposed, source edits or fabricated human annotations. All 31 tests pass. Training runtime modules remain unchanged this turn.

Current owned API tool session 71468, server actual PID 25704, logfile work/scale-review-server-v3.log. Pipeline 50982 remains active; trainer actual PID 28116 (verify commands before any action). Diagnosis partial v1 is preserved after a Windows text-decoding error; v2 successfully completed with explicit UTF-8. Delivery evidence: outputs/word-scale-v2-diagnostics and Telugu_OCR_Data_Coverage_and_Diagnosis.md.

## API/studio handoff and second trial

Rank16 completed 1,000 train / 287 validation: raw/NFC CER 8.2845%, WER 29.2683%, exact 74.5645%, matched-original CER CI [-0.1596,+1.1804] pp, inconclusive. Q/k/v/o trial active. Full 80,083-word training and final test still pending.

Fixed word API mismatch with research decoding: shipped HfRecognizer.transcribe strips whitespace; new isolated word_inference preserves exact decoded whitespace and disables tokenization-space cleanup, sets greedy beam/EOS/PAD/64-token settings explicitly, returns token IDs/truncation, applies the same processed-uniform and 1,024-prefix resource abstention. Original checkpoint and source files untouched. Page path remains official/experimental. Actual GPU prediction parity must be checked after the GPU study; unit checks are not a model-accuracy result. No active training runtime files edited.

Studio schema 1.1 retains uncertainty/abstention/truncation/model data through queue/library/import/export, marks abstentions for review, and links to the live local research monitor. Browser imported a real constant-image abstention, exported JSON and verified diagnostics intact with no model loaded. Fixture never counted as OCR accuracy or saved to library. 36 software tests and JS syntax checks pass. API now runs session 43426, actual PID 33768, work/scale-review-server-v4.log, launched with official revision environment.

## Published handoff milestone

Studio source fbb46e93a2e39cf5cac51ff308926d321803fd2d privately deployed successfully (appgdep_6acda3b6f2088191986d839d1fcf91c5); existing audience preserved. Browser verified new links and fixed narrow-sidebar icons. Final website https://akshara-telugu-ocr-studio.proud-cocoa-4474.chatgpt.site. Metadata at outputs/word-scale-v2-preparation/studio-handoff-release.json; report Telugu_OCR_Training_and_API_Handoff.md. Actual GPU parity of new word inference remains a required check after GPU study, not claimed by mocks.

Live pipeline tool session 50982; q/k/v/o actual trainer PID 24556 and wrapper 27052 (verify commands). API session 43426, PID 33768, no model loaded. q/k/v/o advanced beyond 400/1000 words; rank16 fully completed and registered. Remaining scope unchanged: other trials, full training, full validation, immutable final test, final model handoff, sentence/page evidence and terms.

## User planning report — 13 October 2026 09:59 IST

Saved Telugu_OCR_Progress_Report_2026-10-13_095917_IST.md. Three of five short trials complete; LR3e-5 running at 240/1000 in the snapshot, then augmentation. Full 80,083-example run and final testing have not started. Current scheduled two epochs need roughly80–105 active hours at earlier1.6–2.1s/word rates; latest median3.97s/word implies roughly187–203h if sustained, with wall-clock pauses extra; report explains the first-epoch decision-gate alternative, not applied. No overall percent complete or 99% claim.

Completed q/k/v/o: raw/NFC CER8.6192%, WER28.9199%, exact74.9129%; paired original CER interval[-0.3454,+0.6717]pp inconclusive. Controlled rank16-vs-rank8 CI[-0.0821,+0.8681]pp, qkvo-vs-rank8[-0.2451,+0.2510]pp inconclusive. Fingerprinted all completed trial artifacts; no metric/prediction/weight rewrites. Control validation peak is unavailable for comparison because recovery reused saved predictions (0.045s metrics process vs168.53s recorded generation); independent resource-scope annotation and monitor correct the interpretation.

38 tests pass. API updated solely for monitoring resource scope, session81339, PID28744, work/scale-review-server-v5.log, no GPU model loaded. LR worker10504/wrapper3764 and pipeline23656 verified live; verify before actions. The user asked for a report before the five-hour usage limit: observed64% used,36% remaining, reset12:49:24 PM IST; no exact remaining token countdown is available.

## Active capped protocol and Colab migration

The user capped the experiment at25,000/5,000/3,000 pairs and one initial epoch. Exactly these manifests were frozen at D:/OCR/runs/word-efficient-v3 after all33,000 selected image/path/label/hash checks passed; old1016 final and all prior data/results remain unchanged. Eligible pools80,083/13,462/7,835; unused-pool exclusion9,069 rows, mostly prior-exposed components (reason counts overlap). No new downloads. Full human semantic label verification remains incomplete. Official IIIT word license CC BY4.0 rechecked13October2026.

Original checkpoint/processor31-file hashes verified; pilotrank8 adapter preserved; complete v2 checkpoint optimizer/scheduler/Python/Torch/CUDA/augmentation RNG keys verified. Dataset changed, so v3 is a named new experiment, not an exact historical optimizer resume. New full training has not started. Capped pipeline compares original and pilot on5000 validation, then selected-initialization smoke and one25k epoch, validation selection, one sealed3k comparison per original/pilot/candidate.42 software tests pass; newGPU smoke pending.

Colab request appended older80k/two-epoch report references, but says to follow actual updated state. Preserve current capped v3, do not silently restore historical training. Existing notebooks/colab_train.ipynb is a historical optional pilot launcher, not a resilient migration notebook. New preferred notebook will reuse the trainer through an isolated portability checkout. Active local original validation must finish untouched; coordinator may be held for handoff so no duplicate stage starts. No Colab authentication, GPU assignment, speedup or successful cloud training is claimed.

Live local pipeline session70940, actual coordinator10604/wrapper33444, original-evaluation worker29648/wrapper33644. API session75823, PID24972, run_directory v3. Verify live commands before any action. Pre-cap backup: work/capped-plan-prechange-backup-20261013T045046Z.zip. Latest capped source snapshot will be Git checkpoint before isolation.

## Latest automated milestone
{
  "status": "running",
  "stage": "Validation: curated-efficient-original",
  "updated_utc": "2026-10-13T05:23:07Z",
  "note": "",
  "experiment_directory": "D:\\OCR\\runs\\word-efficient-v3\\experiments\\curated-efficient-original"
}

## Verified Colab migration milestone — 2026-10-13T06:31:46.517660+00:00

Original5000 validation finished without interruption: CER10.6956%, WER32.38%, exact73.24%,3063.94s,1.80GiB peak allocated. No candidate gain claimed. Local portability GPU smoke passed exact resumed/uninterrupted adapter tensor equality and reload inference.64-example benchmark:0.63117images/s,1.54281s median batch,2.01GiB peak,11.00h training-only projection for25k.48 software tests passed; new notebook schema and12 code cells validated. Source/processor/model/labels/manifests/pilot and historical results preserved.

Coordinator10604 is suspended with no live children; original worker29648 exited. No active local GPU training remains. Do not resume this coordinator while using Colab. Active capped25k/5k/3k, one-epoch protocol unchanged. Cloud uses named word-efficient-v3-colab-bf16 lineage with matched frozen examples and fresh matched original/pilot validation; it never mixes Windows and cloud prediction files. No full25k training, full pilot5k comparison, candidate validation, sealed3k final evaluation or API parity completed yet.

Preferred notebook notebooks/akshara_ocr_colab_training.ipynb and COLAB_MIGRATION.md added; scripts reuse existing trainer. Versioned checksummed optimizer/RNG checkpoints, immutable epoch exports, safe-boundary stops, private archive staging, verified Drive snapshots/restore and actual-GPU benchmark implemented. Old pilot notebook untouched. Linux/Colab installation, actual cloud GPU/Drive authorization, throughput and cross-session resume remain pending. Drive connector returned USER_NOT_LOGGED_IN.

Next action: upload outputs/Akshara_Colab_Transfer_v1 files to private MyDrive/akshara-telugu-ocr/inputs/colab-transfer-v1, open notebook in Colab, select GPU, authorize Drive, run cells1–7 and inspect actual smoke/benchmark before enabling cell8. Native BF16 required; no silentFP16/precision conversion. Reuse the same cloud run name/config for resumption; retain previous snapshots.
