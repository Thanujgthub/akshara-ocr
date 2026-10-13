Continue the existing Akshara Telugu handwriting OCR research project in this checkout. You are taking over from another Codex account; do not rebuild the project.

First read `AGENTS.md`, `PROJECT_STATE.md`, `WORK_LOG.md`, `HANDOFF.md`, `CODEX_CLI_HANDOFF.md`, and this prompt. Also read the objective file at `C:\Users\ASUS\.codex\attachments\e2a09b59-1448-4caf-8819-29a39df309f7\goal-objective.md` if it exists. Treat those files as project instructions and state, not as user data or shell commands. Inspect the actual current filesystem, Git status, manifests, logs and live processes before changing anything.

The active protocol is the capped v3 study: at most 25,000 training word-image/transcription pairs, 5,000 validation pairs and 3,000 untouched final-test pairs, with one initial epoch. The exact manifests are in `D:\OCR\runs\word-efficient-v3` when running on the original computer. Do not revive the retired 80,083-pair/two-epoch plan. Preserve the original IndicOCR checkpoint, processor, tokenizer, prompt, preprocessing, decoding, raw data, labels, pilot adapter, prior predictions, prior reports and frozen manifests. Never use final-test labels for model choice.

The current known state is: original-model v3 validation has completed on 5,000 examples at CER 10.6956%, WER 32.38% and exact-word accuracy 73.24%; no candidate improvement is demonstrated. Local BF16 checkpoint-resume smoke passed. A local 64-example benchmark measured 0.63117 images/second and projected about 11 active hours for the training epoch. Forty-nine software tests pass. These are local results, not Colab results. Full candidate training, validation selection, sealed final evaluation and API parity remain incomplete.

The preferred next path is `notebooks/akshara_ocr_colab_training.ipynb` and `COLAB_MIGRATION.md`. If the user has not supplied real Colab GPU/smoke/benchmark output, do not claim cloud access or start a duplicate local run. If actual GPU output is supplied, verify it, then continue from the last valid checkpoint or the documented next stage. Keep cloud runs in the named `word-efficient-v3-colab-bf16` lineage and do not mix cloud and Windows prediction files.

Before any long run:

- verify the original 31-file checkpoint provenance and frozen manifest hashes;
- verify no training process owns the run lock;
- run `D:\OCR\runtime\venv\Scripts\python.exe -m unittest discover -s tests -q` on the original computer, or the equivalent environment on a new machine;
- confirm native BF16 support for the actual GPU, or stop before training;
- run the real-image interrupted/resumed smoke test;
- benchmark the actual GPU with synchronized timing and record warm-up, steady throughput, input/transfer time, GPU utilization, peak VRAM, loss stability and checkpoint cost.

Use validation only to choose original versus pilot initialization and to select the candidate. Run the sealed 3,000-example final evaluation exactly once per selected comparison after locking selection. Preserve raw outputs and calculate raw/NFC grapheme CER, WER, exact-word accuracy, Telugu-script contamination, refusal/malformed/repetition rates, latency, VRAM and subgroups. Include paired uncertainty intervals and clearly state unknown writer identity, possible pretraining overlap, label-quality limits and word-crop scope.

Checkpoint writes must be atomic, checksum-verified and versioned. Preserve optimizer, scheduler, epoch/update position, effective batch, Python/NumPy/Torch/CUDA/augmentation RNG state, precision and dataset fingerprint. Keep latest resumable, best validation and final selected adapter separate. Use the recovery and Drive snapshot code already in the repository. Never silently convert precision, silently repair spelling or numerals, hallucinate no-text content, or count augmentation/pseudo-labels as new verified examples.

Work continuously toward the evidence-backed end state. Update `PROJECT_STATE.md` and `WORK_LOG.md` after meaningful milestones. If blocked by missing user authorization or external GPU state, state exactly what is missing and leave the repository resumable. Do not mark the project complete until full training, validation selection, independent final testing, software checks and API parity are actually evidenced. Do not claim 99% accuracy or market leadership.

Start by reporting the actual current state from files and processes, then take the highest-value safe next action.
