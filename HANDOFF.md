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

## Current continuation state — 13 October 2026

The earlier pilot summary above is historical. The active protocol is now the capped v3 study: 25,000 training pairs, 5,000 validation pairs, 3,000 sealed final-test pairs and one initial epoch. The exact frozen manifests are under `D:/OCR/runs/word-efficient-v3`; the original model and all prior runs remain unchanged.

The original-model v3 validation completed: raw/NFC grapheme CER 10.6956%, WER 32.38%, exact-word accuracy 73.24%, 5,000 examples, 1.80 GiB peak allocated VRAM. No candidate improvement has been demonstrated. A real local BF16 resume smoke passed, and the 64-example local benchmark measured 0.63117 images/second with a short-run 25,000-example training projection of about 11 active hours. These are local measurements, not Colab results.

The preferred continuation is the Colab workflow in `notebooks/akshara_ocr_colab_training.ipynb`, documented in `COLAB_MIGRATION.md`. The private transfer package is `../Akshara_Colab_Transfer_v2`; it contains the original model snapshot, pilot adapter, frozen protocol and selected image archives. Google Drive authorization, a supported Colab GPU, full training, candidate validation, sealed final testing and API parity are still pending. Do not resume the held local coordinator while a cloud run is active. Use `CODEX_CLI_HANDOFF.md` and `CODEX_CLI_PROMPT.md` when moving this work to another Codex CLI account.

## Latest continuation - 15 October 2026

The historical Colab preference above has been superseded by the approved local Windows continuation. Active checkout: `D:/CODEX/OCR/akshara-ocr`; runtime: `D:/OCR/runtime/venv/Scripts/python.exe`; unchanged artifacts: `D:/OCR/runs/word-efficient-v3`. Training is safely stopped at full checkpoint `step-0004937`, next_index19,748, updates4,937, BF16. The initial25,000-example epoch is unfinished. STOP is deliberately preserved. Current capacity is below the8.5GiB pre-load gate; the user has been asked to close unused apps and reply Closed. Recheck actual memory; do not restart from a smoke checkpoint. Fresh CPU preflight in `recovery/windows-d-drive-preflight-v3` passes85tests, original31 and all33,000 image checks. Fresh GPU BF16/smoke/benchmark, remaining training, candidate5000 validation, locked selection, sealed3000 final comparisons, reporting/export, selected API parity and real selected website OCR checks remain pending. Latest verified backup: `snapshot-20261015T063232Z-9b46b751`. Read latest PROJECT_STATE.md and WORK_LOG.md. Ranking/comparison page and Vercel/GitHub publication are deferred.


- 2026-10-15T10:57:00Z: User resumed work and closed Brave; native commit headroom recovered to9.86GiB. Fresh v4 preflight passes85tests, original31/frozen25k/5k/3k, native BF16 RTX3050/Torch2.11cu128/CUDA12.8, real-image exact interrupted/resumed optimizer/RNG/scheduler and adapter-reload smoke. Synchronized64-image benchmark: 0.654316images/s; warm8=12.545151s; median input/transfer=0.036150s; peak=2154064384B; checkpoint=0.129504s; finite losses, raw input/GPU utilization retained. Full19748/4937 checkpoint and latest durable snapshot verified, state identical; postbenchmark preload9.80GiB. Verified STOP archived/consumed after gates. Single actual trainer31428/coordinator25716/controller31864 (wrappers31404/15848/27660) resumed FULL19748; observed contiguous finite raw19749..19761; diagnostic weights never used. Existing2GiB runtime safe-stop and300s snapshots unchanged; scoped temporary keep-awake/affinity0..11/normal priority only, no OS setting changes. Local website127.0.0.1:8765 and progress.html live with inference guarded. About2.23 active training hours estimated, excluding candidate validation/final comparisons. Candidate validation/locked selection/sealed testing/analysis/export/selected API parity/browser OCR pending. Rankings/comparison page and publication deferred. Evidence reports/colab-migration/windows-full19748-recovery-resume-20261015.json; raw recovery/windows-d-drive-preflight-v4.


- 2026-10-15T10:59:45Z: Fresh v4 full19748 resume advanced56 examples, then Windows runtime memory guard requested safe STOP at10:58:08UTC (headroom1,910,312,960B, below unchanged2GiB reserve). Gracefully saved FULL19,804/25,000,4,951updates,BF16,step0004951. Controller final exit0 and snapshot snapshot-20261015T105848Z-b2dd69f3 independently verified allSHA/state byte identity; archive recovery/memory-guard-stop-20261015T1058Z retains STOP/terminal logs/pointer. Workers exited; STOP preserved. Memory recovered to9.46GiB after exit; exact transient pressure source not established. Checking capacity stability before next resume; no weakening guard, killing user apps, OS/precision/protocol changes or smoke-weight promotion. Candidate validation, selection, sealed final and selected API/website checks remain pending; comparisons/rankings/publication deferred. Evidence reports/colab-migration/windows-19804-safe-memory-stop-20261015.json.
