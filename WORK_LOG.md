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
