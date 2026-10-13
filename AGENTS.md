# Telugu OCR research rules

Extend this project; never replace its original checkpoint/tokenizer or overwrite earlier artifacts. Read PROJECT_STATE.md and WORK_LOG.md before resuming.

Keep D:/OCR/runs/word-pilot-v1 and D:/OCR/research immutable. Reuse data in D:/OCR/research-v2. Historical D:/OCR/runs/word-scale-v2 is retired. Active capped protocol: D:/OCR/runs/word-efficient-v3, at most25,000 training pairs,5,000 validation and3,000 sealed final-test pairs, one initial epoch. Do not revive the old80,083/two-epoch pipeline. Preserve its results. Never select settings using test labels. Source-document and duplicate components must stay in one split. Writer identities and pretraining overlap remain unknown.

Preserve raw output, labels, digits, spelling and Unicode. Suggested contextual corrections must be visibly separate and require human approval. No calibrated confidence or no-text claim without evidence. Word accuracy does not establish page accuracy.

Record measured experiments, failures, configs, seeds, hashes, predictions, memory/time, environment and resume state. Never claim 99% or market leadership without an appropriate independent benchmark. Update state and work log at milestones.

Colab migration must preserve the active capped protocol. Never edit active GPU training/evaluation modules in place: use the isolated migration checkout or wait for a verified safe boundary. Do not run the same stage concurrently on Windows and Colab. No Colab/GPU/Drive authentication or performance claim without actual evidence.
