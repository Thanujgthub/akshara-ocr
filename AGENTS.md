# Telugu OCR research rules

Extend this project; never replace its original checkpoint/tokenizer or overwrite earlier artifacts. Read PROJECT_STATE.md and WORK_LOG.md before resuming.

Keep D:/OCR/runs/word-pilot-v1 and D:/OCR/research immutable. New research lives in D:/OCR/research-v2 and D:/OCR/runs/word-scale-v2. Never select settings using test labels. Source-document and duplicate components must stay in one split. Writer identities and pretraining overlap remain unknown.

Preserve raw output, labels, digits, spelling and Unicode. Suggested contextual corrections must be visibly separate and require human approval. No calibrated confidence or no-text claim without evidence. Word accuracy does not establish page accuracy.

Record measured experiments, failures, configs, seeds, hashes, predictions, memory/time, environment and resume state. Never claim 99% or market leadership without an appropriate independent benchmark. Update state and work log at milestones.
