# Handoff · 13 October 2026

The word adapter improved grapheme CER by 0.58 percentage points on this fixed test set. The paired bootstrap interval does not establish a CER reduction.

| Requirement | Actual status |
| --- | --- |
| Website, local API and preview | Implemented; live training/results dashboard and word/page selector |
| Original authorized model | 31 downloaded files match the published snapshot; original weights unchanged |
| 1,000 / 500 / 500 labeled crop quota | Met with source-provided word labels; image hashes and source-document group isolation checked |
| Human-verification and writer-disjointness | Not established |
| Forward/backward/update | Passed on real images with finite loss and gradients |
| Tiny-subset learning and save/reload | Passed before the clean adaptation run |
| Training | One epoch completed on 1,000 words; 319,488 trainable adapter parameters |
| Original-versus-adapted benchmark | Both evaluated on the same untouched 500-word test; raw predictions and metrics saved |
| Statistical analysis | 2,000 paired source-document bootstrap replicates; per-length/document/error breakdowns |
| Whole-page training and benchmark | Not run; page terms need clarification and word metrics cannot replace page evidence |
| User's original handwriting sample | Not supplied/found; representativeness unknown |
| Full original baseline before adaptation | Not run in that order; unchanged original weights were tested after adaptation; no test-guided retuning |
| Full corpus training | Not run; this is a bounded, prespecified 1,000-word pilot |

## Delivered locations

Project source and Start-Akshara.ps1 are in this directory. The neighboring word-pilot-results folder contains frozen manifests, raw predictions, metrics, audit, contracts and logs. Telugu_Word_Adapter.zip contains adapter weights, configuration and original license. The complete analysis is in Telugu_OCR_Test_Analysis.md and reports/evaluation.md.

The user's D:/OCR archives and original model remain unchanged. Executed run artifacts are in D:/OCR/runs/word-pilot-v1; the isolated CUDA runtime is D:/OCR/runtime/venv. See README.md for commands actually used and the optional, unexecuted Colab path. All source labels retain source provenance; no OCR pseudo-labels were used as gold.

## Remaining work

Establish page dataset terms, obtain authoritative writer metadata and a representative user handwriting sample, review source labels/near-duplicate candidates, and run a separately frozen page/domain evaluation. Do not represent the word pilot as a production-ready full-page or historical-manuscript OCR system. If broader deployment is intended, follow the original model license's hosting conditions.

Executed final checks: 13 unit tests passed; both JavaScript files passed Node syntax checks; real original/adapted API outputs matched their saved test predictions; a real held-out image was uploaded and transcribed in the browser. Screenshot: ../akshara-working-preview.png. The local API remains running on 127.0.0.1:8765.
