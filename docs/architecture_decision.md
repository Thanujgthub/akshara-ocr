# Verified architecture · 13 October 2026

Preserve the original IndicOCR page layout → block recognition → reconstruction route. Adapt its actual Qwen3.5 recognizer on isolated handwritten word crops; no line alignment or replacement model is invented. The word adapter improved grapheme CER by 0.58 percentage points on this fixed test set.

Actual local weights, processor and original repository source were inspected and matched the published snapshot hashes. The official repository supplies layout training only, so this project implements a separately verified recognizer LoRA path. The exact prompt/template/EOS, image preprocessing, module names, parameter counts and environment are saved in the executed run contract.

The initial Windows page-file allocation failures were resolved by tensor-by-tensor original-weight loading and freeing unused apps. CPU inference worked but CPU training exceeded available memory. GPU answer-token-only cross-entropy, BF16, gradient checkpointing and batch size one passed. The 64-step smoke experiment demonstrated learning and save/reload parity before the clean 1,000-word epoch.

Full pages still use the official layout and block reconstruction pipeline. Word test metrics do not establish page quality. Page corpus training remains unapproved pending terms clarification. A separate page experiment and authoritative writer IDs are required before broader claims.
