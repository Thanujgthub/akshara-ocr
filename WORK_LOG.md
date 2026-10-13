# Work log

## 13 October 2026 — scale-up started
- Inspected experiment objective, LoRA module discovery, streamed original-weight loader, original processor/tokenizer/chat template, inference bridge, metrics, dashboard, dataset audit, pilot report, adapter config and smoke logs.
- Baseline accepted as inconclusive; no claim of demonstrated improvement.
- Found original prompt explicitly requests LaTeX, consistent with wrapper errors. Greedy decoding already used. Existing output strips surrounding whitespace; new research must retain true decoded raw output separately.
- Found pilot seeds set after adapter creation and incomplete accumulation scaling for short final batches; new runner will seed before initialization and scale each accumulation window correctly.
- Found existing checkpoints save optimizer but have no resume path or RNG/scheduler state; new runner will implement atomic resumable generations.
- Started full technical audit of three supplied word archives into a new directory. Exact duplicates retained as graph edges before holdout allocation, preventing a train-first deduplication leak. Page archives remain audit-only.
- Rechecked official word license (CC BY 4.0), page source description and model source. Isolated words do not provide sentence context supervision.

- 2026-10-12T21:31:11Z: Snapshot and full word audit. Inspecting all supplied labeled word pairs; source labels are not newly human verified.

- 2026-10-12T21:31:13Z: Freeze leakage-checked scale manifests. 

- 2026-10-12T21:31:13Z: GPU smoke and checkpoint resume. 

- 2026-10-12T21:31:44Z: Validation: original-official-official. 

- 2026-10-12T21:34:32Z: Validation: original-telugu_literal-official. 

- 2026-10-12T21:36:55Z: Snapshot and full word audit. Inspecting all supplied labeled word pairs; source labels are not newly human verified.

- 2026-10-12T21:36:55Z: Freeze leakage-checked scale manifests. 

- 2026-10-12T21:36:55Z: GPU smoke and checkpoint resume. 

- 2026-10-12T21:39:09Z: Validation: curated-original-official-official. 

- 2026-10-12T21:42:34Z: Validation: curated-original-telugu_literal-official. 

- Full audit completed in 533.7 s: 118,515 paired images, no rejected decode/label records. All label records checked for duplicate/conflicting paths; none found. 7,897 unpaired training ZIP images remain excluded.
- Inspected training and validation error images: some multiword form crops have single-word source labels. Preserved initial freeze and created separate label-blind curated manifests/quarantine. No labels repaired.
- Tokenizer check: 11,737 unique candidate training labels, zero roundtrip failures, maximum 14 target tokens. Original generation EOS configuration already equals actual tokenizer EOS; obsolete vendored comment does not describe this local checkpoint.
- Passed exact interrupted-versus-uninterrupted GPU adapter comparison, including optimizer/scheduler/RNG restoration. Initial completed-run smoke also retained.
- During pipeline restart an orphan evaluation process briefly competed for VRAM; terminated the specifically identified old child and verified only the active experiment process remained. Smoke duration includes contention; do not use it as clean throughput evidence.
- Added local research monitor and uncertainty diagnostics. Existing hosted UI remains unchanged by this operational research run. API unloads model and refuses inference while research is active.
- Reviewed all earlier scratch log files and saved fingerprint/error summaries. Researched separately licensed PaddleOCR Telugu and Kraken line training as later baselines; neither silently replaces IndicOCR.

- 2026-10-12T21:45:31Z: Validation: curated-original-telugu_literal-white_margin. 

- Final software validation: 20 tests passed. Image-token estimates matched the original processor on five image shapes. Mild skew augmentation reverts to the source when expansion would exceed the word budget.

- 2026-10-12T21:48:33Z: Validation: curated-pilot-official-official. 

- 2026-10-12T21:51:26Z: Validation: curated-pilot-telugu_literal-official. 

- 2026-10-12T21:54:24Z: Validation: curated-pilot-telugu_literal-white_margin. 

- 2026-10-12T21:57:30Z: Controlled training trial: control. 1,000 training words; settings selected on validation only.

- Scale pipeline failed: Command '['D:\\OCR\\runtime\\venv\\Scripts\\python.exe', '-u', '-m', 'ocr.scale_experiment', 'train', '--config', 'D:\\OCR\\runs\\word-scale-v2\\configs\\trial-control.json', '--manifest', 'D:\\OCR\\runs\\word-scale-v2\\trial-train-curated.jsonl', '--validation', 'D:\\OCR\\runs\\word-scale-v2\\trial-validation-curated.jsonl', '--output', 'D:\\OCR\\runs\\word-scale-v2\\trials\\control', '--epochs', '1']' returned non-zero exit status 1.

- 2026-10-13T02:35:19Z: Snapshot and full word audit. Inspecting all supplied labeled word pairs; source labels are not newly human verified.

- 2026-10-13T02:35:20Z: Freeze leakage-checked scale manifests. 

- 2026-10-13T02:35:20Z: Validation: curated-original-official-official. 

- 2026-10-13T02:35:20Z: Validation: curated-original-telugu_literal-official. 

- 2026-10-13T02:35:20Z: Validation: curated-original-telugu_literal-white_margin. 

- 2026-10-13T02:35:20Z: Validation: curated-pilot-official-official. 

- 2026-10-13T02:35:20Z: Validation: curated-pilot-telugu_literal-official. 

- 2026-10-13T02:35:20Z: Validation: curated-pilot-telugu_literal-white_margin. 

- 2026-10-13T02:35:20Z: Controlled training trial: control. 1,000 training words; settings selected on validation only.

- 2026-10-13T02:35:34Z: Controlled training trial: rank16. 1,000 training words; settings selected on validation only.

- 2026-10-13T02:39:00.787158+00:00: Continuation verified 6 matched screening comparisons, all 287 control validation predictions, 1,000 trained control words / 250 updates. Matched-policy CER CI [-0.319,+0.641] pp: inconclusive. Training peak 2,115,812,352 bytes. Preserved import failure evidence and checkpoint; removed analysis-to-training dependency; resumed without retraining completed words. Rank16 actively advances. Full 80,083-word run and final testing pending.
- Added separate human review UI/API, exact-uniform input abstention, recent throughput display, dependency-isolation regression. All 26 tests pass; browser verified review source/image/raw output and live rank16 stage. No human annotations fabricated or submitted. Source snapshot recorded after recovery, with its scope limitation.

- Full exact-uniform pixel audit completed on all 80,083 curated TRAIN images: zero uniform images, zero read errors, 1,025.04 s CPU wall time. No final-test examples opened. No data changes were needed. Audit evidence copied to outputs/word-scale-v2-preparation.

- 2026-10-13T02:53:51.995538+00:00: Continued live rank16 trial (160 to 520+ words); pipeline/trainer PIDs verified, no restart. Added model-independent read-only validation diagnosis and label coverage tools, full manifest-hash and identity checks. 87 matched disagreement cases, 12 crop image inspections, 4 fewer-edit / 1 more-edit control cases, 282 same. All source labels remain unmodified and not newly human verified.
- Coverage: train 80,083 pairs / 11,723 distinct labels, 175 numeral examples; full val 29 numeral examples; 287-subset zero. All digit codepoints in scanned labels are Telugu. Zero shared train/val identity hashes/groups. Added current validation review queue and raw-output comparison, API restarted separately with no GPU model loaded. No training runtime edits. 31 tests passed; preserved UTF-8 audit failure v1 and successful v2. Final test still sealed.

- 2026-10-13T03:08:48Z: Controlled training trial: qkvo. 1,000 training words; settings selected on validation only.

- 2026-10-13T03:10:44.369628+00:00: Rank16 finished all 250 updates and 287 validation predictions: CER 8.2845%, WER 29.2683%, exact 74.5645%, matched-policy CER interval [-0.1596,+1.1804] pp remains inconclusive. Q/k/v/o trial advances; no trainer interruption.
- Found shipped inference whitespace stripping versus research raw decode; added isolated word API path with explicit matching decoding, quality/truncation/token metadata and resource abstention. No original model files or active training modules changed. Actual GPU parity pending availability. Studio schema1.1 preserves diagnostics through records/export, distinguishes abstention from verified no-text, adds live local research link. 36 tests + JS syntax check passed; browser constant-image result/import/download verified, no GPU model loaded, no fake OCR benchmark or human verification. API restarted separately with revision set. Sites source helper opened exact existing private project before website edits; publishing follows the skill workflow.

- Studio private deployment succeeded from pushed commit c0a7c8acc33f1a5f9011ccd4e1383e52bec556d6 (deployment appgdep_6acda2186a1c8191aeb8e126b6e5a87a). Follow-up narrow-screen QA found research-link overflow; fixed icon/label layout, added static asset cache versions, and verified both links stay inside the 74 px sidebar at 576 px viewport. Viewport reset afterward. Packaging on Windows uses Git Bash first in session PATH and TAR_OPTIONS=--force-local; no installed helper or system setting changed.

- 2026-10-13T03:23:49.903349+00:00: Final responsive studio publication succeeded, source fbb46e93a2e39cf5cac51ff308926d321803fd2d, private deployment appgdep_6acda3b6f2088191986d839d1fcf91c5. Published UI observed. Current q/k/v/o trainer PID 24556 verified live beyond400/1000. Recorded rank16 metrics/CI and new word API handoff limits; GPU parity still pending. No new final-test access, no numeric accuracy claim and no contextual guesses.
