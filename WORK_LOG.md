# Work log

## 13 October 2026 — scale-up started
- Inspected experiment objective, LoRA module discovery, streamed original-weight loader, original processor/tokenizer/chat template, inference bridge, metrics, dashboard, dataset audit, pilot report, adapter config and smoke logs.
- Baseline accepted as inconclusive; no claim of demonstrated improvement.
- Found original prompt explicitly requests LaTeX, consistent with wrapper errors. Greedy decoding already used. Existing output strips surrounding whitespace; new research must retain true decoded raw output separately.
- Found pilot seeds set after adapter creation and incomplete accumulation scaling for short final batches; new runner will seed before initialization and scale each accumulation window correctly.
- Found existing checkpoints save optimizer but have no resume path or RNG/scheduler state; new runner will implement atomic resumable generations.
- Started full technical audit of three supplied word archives into a new directory. Exact duplicates retained as graph edges before holdout allocation, preventing a train-first deduplication leak. Page archives remain audit-only.
- Rechecked official word license (CC BY 4.0), page source description and model source. Isolated words do not provide sentence context supervision.
