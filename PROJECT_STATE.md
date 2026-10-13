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

- 2026-10-13T06:43:01.811861+00:00: Colab transfer completed and read-back verified:5 archives,2,945,455,311 bytes,33,000 selected image payload hashes and decodes,3 frozen manifest hashes/counts/group separation,31 original model payload files and pilot adapter. Original preservation snapshot31model/32pilot/6manifests matched with zero mismatches. Source snapshot b672f47.48 software tests and notebook schema/12 AST cells passed. Source ZIP refreshed to include pinned HTTPX/API test dependencies; first source ZIP preserved at work/colab-source-dd79f53.zip. No cloud training/authentication or final-test predictions performed. Notebook and guide delivered; user Drive authorization/GPU assignment remain required.

- 2026-10-13T06:47:24.608164+00:00: Continued migration audit found/fixed two reproducible multi-session recovery defects: restore ignored latest pointer and sorted random snapshot suffixes; restored snapshot-checksums could be recopied into a new snapshot and invalidate it. New metadata nanosecond ordering, validated latest-pointer preference, legacy fallback and exclusion of snapshot bookkeeping from active runs implemented. Added restore→snapshot→restore and corrupt-pointer tests;49 software tests pass. Drive connector rechecked: USER_NOT_LOGGED_IN. Local coordinator10604 remains suspended; no active GPU worker. Full cloud training/evaluation still requires Google authorization and assigned GPU. Preparing version2 transfer source; original version1 archives preserved.

- 2026-10-13T07:16:16.412746+00:00: Recovery updatev2 delivered at outputs/Akshara_Colab_Transfer_v2, source55b2902.49 software tests pass. All5 archives and33,000 image payload hashes/decodes, frozen splits,31model payload files/pilot and original31/32/6 preservation hashes verified again; evidence reports/colab-migration/transfer-verification-v2.json. Originalv1 preserved. Existing Drive upload needs only changed source ZIP/index. Notebook unchanged. Full training/validation/final-testing remain unfinished; Google Drive authorization and actual Colab GPU are still required.

- 2026-10-13T07:38:00.137223+00:00: Blocked audit: same missing Google/Colab authorization condition persisted across initial migration handoff, recovery-update continuation and this continuation. Drive search rechecked after transient transport failure and returned USER_NOT_LOGGED_IN. No Colab job handle/assigned GPU is available; local coordinator10604 is still suspended and has no OCR GPU worker. Migration artifacts/recovery tests are ready, but full25k training, candidate validation, sealed3k testing and API parity remain incomplete. No duplicate local/cloud run launched. Next required external action: user opens notebook, mounts Drive, selects supportedGPU, uploads v2 inputs and returns actual startup/smoke/benchmark output. Goal to be marked blocked, not complete.

- 2026-10-13: Added `CODEX_CLI_HANDOFF.md`, `CODEX_CLI_PROMPT.md` and `handoff/verify_handoff.ps1` for a second Codex CLI account. Git bundle `outputs/Akshara_Codex_Repo_v2.bundle` verifies as a complete history at revision `704ad4a2bc600c0169b1728c641f7084c1f38224`. A fresh clone from that bundle passed the verifier and all 49 tests. The package excludes credentials, raw data and model weights; the separate private `Akshara_Colab_Transfer_v2` package remains required for Colab. Full training, final testing, cloud authorization and API parity remain incomplete.


## Verified account takeover - 2026-10-13T14:06:43Z

Read AGENTS, project state/log, both handoffs, migration guide and the supplied objective. Clean starting checkout at 5cdda2f. Current Win32_Process inspection found no Python OCR process: historical held coordinator PID10604 is absent, rather than still suspended. Existing pipeline.lock was acquired and released without changing its contents; no local run was started. NVIDIA observation: RTX3050 4GB, driver617.42,76MiB/4096MiB used. Run status remains paused_for_colab_handoff; only original5000 validation exists, no full training or locked selection. Historical run status files were preserved.

Fresh49 software tests passed (2.029s). All31 original checkpoint/processor/tokenizer hashes,3 capped manifest hashes and line counts (25000/5000/3000),3 pilot adapter file hashes and all5 v2 archive hashes/sizes passed in5.62s. Stored baseline5000 predictions/metrics agree: raw/NFC CER10.6956%,WER32.38%,exact73.24%. Evidence: reports/colab-migration/takeover-audit-20261013T140643Z.json. Prior33000-image hash/decode verification was reused, not repeated; final labels were not inspected. Notebook JSON format4 and12 code-cell ASTs passed; nbformat package is unavailable in this runtime, so no fresh full schema validation is claimed.

Corrected only upload instructions in COLAB_MIGRATION.md and notebook Markdown to the actual sibling Akshara_Colab_Transfer_v2 package; compatible Drive inbox remains inputs/colab-transfer-v1. Notebook code cells verified identical to HEAD after the edit. Transfer archives and all training/evaluation modules remain unchanged. No new GPU smoke/benchmark, Colab access or performance result claimed.

External gate: actual Colab authorization/assigned native-BF16 GPU plus startup, interrupted/resumed smoke and synchronized benchmark output have not been supplied. Next: upload v2 inputs to private MyDrive/akshara-telugu-ocr/inputs/colab-transfer-v1/, upload the current notebook, run cells1-7 and return their actual output before enabling cell8. Cloud lineage remains word-efficient-v3-colab-bf16 with fresh matched original/pilot validation. Full25k training, validation selection, sealed3k comparison and API parity remain incomplete.


## Analytics dashboard and Space handoff - 2026-10-13T14:29:30.201413+00:00

Created outputs/ocr-analytics-20261013/Akshara_OCR_Analytics_Dashboard.xlsx from the retained Analytics Dashboard reference, using verified OCR metrics rather than synthetic business data. Three original sheets and four native editable charts retained. Formula error scan found zero matches; changed-input and blank-accuracy checks passed. All three sheets rendered and visually reviewed. The export lost hidden-helper state, restored surgically in workbook XML; original reference remains unchanged. Export/native-feature verification is in outputs/ocr-analytics-20261013/verification.json. Native Excel application and Space rendering were not exercised. No training/evaluation module, source label, frozen manifest, transfer archive or historical prediction was changed.

User requested a new Space: created Akshara OCR Model (page_space_ceadbcf5817c8191876774b695225a78) and saved the workbook to its Akshara OCR Research Dashboard Page, https://chatgpt.com/space/page_6ace3e987584819195cfd07b3cfcc0db . Attachment access and matching SHA256 were confirmed; Page readback contains the workbook link and exact evidence scope. This is an attached Excel file, not a newly created native spreadsheet.

User requested adding the dashboard to the existing Akshara Studio site. sites_get_site and write-credential requests for the preserved .openai/hosting.json project appgprj_6accf32e12f08191892e9c788ee1c852 returned Sites project not found under the current account. No source edit, new replacement Site or deployment was performed; the awaiting source-helper session was cancelled. Access to that existing Site through its owner/editor account is required to continue publication. Full research execution still awaits actual Colab GPU/smoke/benchmark evidence; capped25k/5k/3k, one initial epoch and sealed final-test policy remain unchanged.

- 2026-10-13: User requested running the project and showing the website. Existing Start-Akshara.ps1 launched in background with capped-v3 paths. Launcher PID17348 and API PID7568 verified. GET http://127.0.0.1:8765/ returned HTTP200; health status=ok, model_ready=true, model_load_verified=false, training_active=false. Logs: outputs/akshara-server-20261013-200210.stdout.log and .stderr.log. Browser inventory empty; default-browser launch was rejected by execution policy. Website link provided instead; visual rendering unverified. No training, evaluation or model inference launched.



## Recovery and Colab browser preflight - 2026-10-13T16:05:55.219201+00:00

Verified no local OCR trainer is active and the pipeline lock is available. Original31 checkpoint hashes and frozen25k/5k/3k manifest hashes/counts match. Full training has no resumable full checkpoint yet; original validation remains CER10.6956%, WER32.38%, exact73.24%. No candidate gain or final-test result is claimed. Fixed the shared milestone writer, which previously truncated state after an old automated milestone heading and erased later migration/handoff notes. Successive milestones now preserve all existing history; 50 software tests pass and all12 notebook code cells compile. Notebook adds an early native-BF16 guard, explicit hardware evidence, strict benchmark JSON and checkpoint paths. Preparing version3 source package while preserving v1/v2 and unchanged model/data/pilot archives.

Colab browser is signed in and the existing named notebook was visibly empty. Only T4 is selectable; H100/G4/A100/L4 options are disabled. Attempted prepared-notebook upload remained at Uploading and was cancelled. Added a hardware-only diagnostic to the empty cloud notebook, selected T4 and queued it; allocation is still pending at this milestone. No Drive mount, package installation, smoke, benchmark, training or evaluation has been executed in the cloud. Notebook tools remain unavailable despite successful bootstrap connection.


## Actual Colab GPU preflight blocked - 2026-10-13T16:08:17.072429+00:00

Executed a hardware-only cell in the signed-in existing Colab notebook: Tesla T4,15360MiB total VRAM,14913MiB free, driver580.82.07, Torch2.11.0+cu130, CUDA13.0; native_bf16_supported=false. Output and screenshot saved to reports/colab-migration/colab-hardware-preflight-20261013.json and colab-t4-preflight-20261013.jpg. This establishes cloud runtime access and hardware only. No Drive mount, dependency installation, actual-image smoke, benchmark, training or evaluation has run. H100/G4/A100/L4 choices are disabled in this account. Stop before training: no FP16/FP32 conversion or duplicate local run. Existing formerly blank notebook contains only this diagnostic, not the complete prepared training notebook. Upload attempt stalled and was cancelled.

Version3 transfer bundle now exists at the sibling Akshara_Colab_Transfer_v3 directory, source commit cfcc3b0. All5 archives passed read-back SHA256, ZIP CRC, unique-entry and entry-count checks; model/pilot/frozen protocol/33000-image archives are byte-identical to v2. Evidence: reports/colab-migration/transfer-verification-v3.json. Earlier bundles preserved. The prepared local notebook has all12 workflow cells; compile check and50 software tests pass. Full25000 training, validation-only selection, sealed3000 final testing and API parity remain incomplete. Required external action: obtain a native-BF16 GPU (such as L4/A100/H100), upload the prepared notebook/v3 package and run preflight through smoke/benchmark. No project-completion claim.

## Latest automated milestone
{
  "status": "running",
  "stage": "Approved Windows native BF16 preflight",
  "updated_utc": "2026-10-13T16:30:28Z",
  "note": "50 software tests pass. Fresh smoke then synchronized benchmark. Full training not started.",
  "experiment_directory": "D:\\OCR\\runs\\word-efficient-v3\\local-preflight-approved-v1"
}


## Approved Windows continuation - 2026-10-13T16:36:03.941611+00:00

User approved local preflight, complete capped study, website integration and Playwright testing. 50 software tests pass. Fresh RTX3050 native BF16 exact-resume/reload smoke passed. Fresh64-example benchmark: 0.641863 images/s, 2.01GiB peak, [0.1332559999991645]s checkpoint cost, 10.82h training-only projection. Losses all finite; no accuracy gain claimed. Details: reports/colab-migration/windows-approved-preflight-20261013.json. Full training checkpoint absent; smoke/benchmark checkpoints are excluded from initialization. Original5000 validation hashes recorded for reuse verification.

Temporary progress page /progress.html added to existing studio; live frozen counts, active-stage progress, validation metrics, selection and API status come from current research endpoints. Playwright visible Chrome confirmed desktop/mobile rendering and API inference paused during GPU work; screenshots output/playwright/akshara-progress-preflight.png and akshara-progress-mobile.png. New coordinator will continue at pilot5000 validation, then selected-initialization smoke, one25000 epoch, validation selection and sealed3000 evaluation. Local recovery snapshots use D:/OCR/backups/word-efficient-v3-local-approved-v1 via existing verified snapshot/controller code. No Colab run or final model claim.

## Latest automated milestone
{
  "status": "running",
  "stage": "Validation: curated-efficient-original",
  "updated_utc": "2026-10-13T16:36:28Z",
  "note": "",
  "experiment_directory": "D:\\OCR\\runs\\word-efficient-v3\\experiments\\curated-efficient-original"
}

## Latest automated milestone
{
  "status": "running",
  "stage": "Validation: curated-efficient-pilot",
  "updated_utc": "2026-10-13T16:36:28Z",
  "note": "",
  "experiment_directory": "D:\\OCR\\runs\\word-efficient-v3\\experiments\\curated-efficient-pilot"
}

- 2026-10-13T16:42:41.680814+00:00: Approved capped Windows coordinator is live (controller26260/wrapper30668, coordinator11224, GPU evaluator28016), pilot validation 660/5000; original validation hashes unchanged. Periodic local recovery snapshot snapshot-20261013T164133Z-efc2b133 verified. 52 software tests pass. Playwright desktop/mobile progress rendering and studio navigation checked; actual API returns409 while GPU study is active. Prepared gated selected-model launcher and actual API parity checker; these remain unexecuted until study completion. Full epoch, validation selection, sealed3000 test, selected-model connection and API parity remain pending.

- 2026-10-13T16:52:58.644037+00:00: While the existing pilot validation worker remains active, extended only the progress-page frontend with a completed-study gate for final word-crop metrics, paired intervals and raw diagnostics/subgroup metadata. API final summary remains unavailable until coordinator status completed; no final labels, predictions or GPU modules changed. Node syntax check passed and Playwright visibly confirmed the sealed state; screenshot output/playwright/akshara-final-results-sealed.png. Actual final-results rendering must still be verified after the study finishes.

- 2026-10-13T17:01:09.008056+00:00: Existing pilot validation worker28016 and controller26260 verified live. Pilot validation reached 2580/5000, elapsed 1470.11s. No full-validation quality result or initialization selection yet; original5000 validation remains preserved, full25000 epoch and sealed3000 testing still pending. Continue the same coordinator; do not restart or use smoke/benchmark weights for full training.

## Latest automated milestone
{
  "status": "running",
  "stage": "Capped training smoke and exact resume",
  "updated_utc": "2026-10-13T17:25:27Z",
  "note": "",
  "experiment_directory": "D:\\OCR\\runs\\word-efficient-v3\\smoke-resume"
}

## Latest automated milestone
{
  "status": "running",
  "stage": "Capped25000-word training: epoch1",
  "updated_utc": "2026-10-13T17:26:28Z",
  "note": "One initial epoch only. No additional epochs scheduled.",
  "experiment_directory": "D:\\OCR\\runs\\word-efficient-v3\\full"
}


## Validation-selected pilot initialization - 2026-10-13T17:26:48.012990+00:00

Pilot5000 validation completed: raw/NFC CER9.1996%, WER30.38%, raw exact74.14%, 2925.96s, 1.80GiB peak. Original5000 prediction/metric hashes unchanged. Paired215 source-document/duplicate groups,2000 bootstrap replicates seed42: CER reduction interval [0.3548,3.6485]pp supports pilot initialization on validation. Writer identity remains unknown; this is not an independent final result. Config fixes25k maximum, one epoch, seed42, rank8 q/v, LR1e-5, effective batch4 and preserved pilot adapter SHA. New optimizer/scheduler, not a historical optimizer resume. Exact-resume smoke for selected initialization is now live (worker15852); full training, candidate selection, sealed3k and API parity pending. Evidence reports/colab-migration/windows-initialization-selection-20261013.json.

- 2026-10-13T17:28:10.829375+00:00: Validation-selected pilot BF16 exact-resume/reload smoke passed with full config signature 266194952cff5629b36fd132285ca79fe297e1dbcec3c99c37e0ef9bf46ed929. New capped25000 epoch is live, trainer496/wrapper29860, current 40/25000 and 10 updates. Full initialization record confirms preserved pilot path/SHA and new optimizer/scheduler; no smoke/benchmark weights inherited. Original31-file provenance and capped manifests verified again. Checkpoint cadence125 updates; full resume pointer pending its first boundary. Playwright live training screenshot output/playwright/akshara-training-started.png. Candidate validation, selection, sealed3000 comparisons and selected-model API parity remain incomplete.

- 2026-10-13T17:44:43.643825+00:00: First full-training checkpoint step0000125 verified: 125 updates, next_index500, epoch0, BF16, effective batch4 and accumulation_progress0. Adapter/state checksums, optimizer/scheduler, Python/NumPy/Torch/CUDA/augmentation RNG fields and exact dataset/config signature verified by CPU-only load. Initial standalone fingerprint audit used file order rather than reader's seed42 shuffle; corrected audit matches without modifying trainer or checkpoint. Verified snapshot snapshot-20261013T174312Z-6426e08b contains a byte-identical full state.pt and intact recovery checkpoint. Evidence reports/colab-migration/windows-first-full-checkpoint-20261013.json. Training remains active; candidate validation/final test/API parity not complete.

- 2026-10-13T17:55:40.728522+00:00: Full trainer496 continues at 880/25000. Sustained recent100-word median 1.629s/example; current epoch remainder about 10.91h excluding validation/final testing and pauses. Longer than the short preflight projection; no settings or epoch count changed. Laptop power plugged=True; resource evidence reports/colab-migration/windows-sustained-training-observation-20261013.json. First full step125 checksum/RNG/optimizer checkpoint remains preserved; later checkpoints continue every125 updates. No candidate accuracy or final-test claim.

- 2026-10-13T18:00:39.067920+00:00: Capped full training passed1000/25000, 250 optimizer updates, one epoch unchanged. step0000250 checksums and original dataset/config signature verified; step0000125 remains intact. Latest verified snapshot has recovery update 125; full-state bytes match latest=False. Evidence reports/colab-migration/windows-1000-training-milestone-20261013.json. Trainer496 remains active; no restart, precision conversion or training-module edit. Candidate validation, sealed3000 testing and API parity still pending.

- 2026-10-13T18:07:45.859439+00:00: Scheduled snapshot snapshot-20261013T180353Z-fcee5b1c now contains full step0000250 (250 updates, next_index1000). Entire snapshot and checkpoint checksums verified; saved state.pt is byte-identical to live full checkpoint. This supersedes the earlier observed sync lag without changing or deleting any earlier snapshot. Trainer496 remained live at1140/25000; validation/final testing/API parity still pending.

- 2026-10-13T18:55:17.108285+00:00: Sustained slowdown observed near1500 words: recent median~5s/word, GPU utilization16-30%, thermal/power slowdown flags inactive, <2GiB availableRAM, other Chrome renderer using~one CPU core. Closed only the owned idle Playwright window; trainer/server/user browsers preserved. Native Windows CPU topology verified six faster cores (logical0..11, EfficiencyClass1) plus efficiency cores (12..19,class0). Applied reversible CPU-affinity-only trial to trainer496, keeping normal priority, four Torch threads, all model settings, BF16, data, code and system power plan unchanged. Conservative post-change 171-word median 2.370s versus pre-change recent100-word median 5.093s; different words/resource conditions confound causal attribution. Keep observed faster scheduling and monitor; original affinity recorded for rollback. step375 checkpoint verifies next_index1500 and preserved signature. Evidence windows-training-affinity-trial-20261013.json and windows-training-affinity-result-20261013.json. No candidate accuracy or final-test result claimed.

- 2026-10-13T19:02:05.107322+00:00: Full epoch reached2000/25000 and500 optimizer updates. step0000500 checksums, BF16, epoch0, next_index2000 and unchanged config/dataset signature verified. All4 existing full checkpoint generations remain intact. Source code, frozen manifests and one-epoch protocol unchanged; trainer496 continues with recorded performance-core affinity. Candidate validation, sealed3000 and API parity remain pending. Evidence reports/colab-migration/windows-2000-training-milestone-20261013.json.
