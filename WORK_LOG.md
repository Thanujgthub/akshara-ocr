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

- 2026-10-13T04:17:51Z: Controlled training trial: lr3e-5. 1,000 training words; settings selected on validation only.

- 2026-10-13T04:29:17.054350+00:00: Completed q/k/v/o training+287 validation, LR trial active. Saved user-requested planning report Telugu_OCR_Progress_Report_2026-10-13_095917_IST.md with distinct example counts, measured scores/CIs, full-run not-started status, realistic80–105h active planning range and two-epoch early-stop limitation. Preserved original/pilot hash check 31/32/6 files, zero mismatches.
- Added completed-trial hash/resource-scope audit. Control metrics recovery reused predictions; full validation VRAM peak unavailable, original scores untouched. Matched controlled CIs saved, all inconclusive. 38 tests pass. Local monitor/API updated and restarted independently of trainer; no active training-module edits. Account-window snapshot64% used,36% remaining, reset12:49:24 IST; no reset/purchase action.

- Planning-report correction before delivery: recent100-word LR median slowed to3.97s/word. Included both prior80–105h and sustained-slow187–203h full-plan scenarios; cause unverified, no system settings changed. Report now clearly budgets four to eight-plus active days rather than relying on earlier optimistic throughput.

- 2026-10-13T05:23:07Z: Validation: curated-efficient-original. 

- 2026-10-13T05:44:12.319583+00:00: User requested Colab migration. Read complete updated objective. Verified active capped25k/5k/3k one-epoch protocol, frozen33k technical checks, local original5k validation live. Oldv2 parent retired afterLR child finished; old80k stage blocked. Preparing isolated portable source/notebook without altering the active evaluation. Historical pilot Colab notebook inspected and preserved. No Google/Colab access or performance claimed.

## Verified Colab migration milestone — 2026-10-13T06:31:46.517660+00:00

Original5000 validation finished without interruption: CER10.6956%, WER32.38%, exact73.24%,3063.94s,1.80GiB peak allocated. No candidate gain claimed. Local portability GPU smoke passed exact resumed/uninterrupted adapter tensor equality and reload inference.64-example benchmark:0.63117images/s,1.54281s median batch,2.01GiB peak,11.00h training-only projection for25k.48 software tests passed; new notebook schema and12 code cells validated. Source/processor/model/labels/manifests/pilot and historical results preserved.

Coordinator10604 is suspended with no live children; original worker29648 exited. No active local GPU training remains. Do not resume this coordinator while using Colab. Active capped25k/5k/3k, one-epoch protocol unchanged. Cloud uses named word-efficient-v3-colab-bf16 lineage with matched frozen examples and fresh matched original/pilot validation; it never mixes Windows and cloud prediction files. No full25k training, full pilot5k comparison, candidate validation, sealed3k final evaluation or API parity completed yet.

Preferred notebook notebooks/akshara_ocr_colab_training.ipynb and COLAB_MIGRATION.md added; scripts reuse existing trainer. Versioned checksummed optimizer/RNG checkpoints, immutable epoch exports, safe-boundary stops, private archive staging, verified Drive snapshots/restore and actual-GPU benchmark implemented. Old pilot notebook untouched. Linux/Colab installation, actual cloud GPU/Drive authorization, throughput and cross-session resume remain pending. Drive connector returned USER_NOT_LOGGED_IN.

Next action: upload outputs/Akshara_Colab_Transfer_v1 files to private MyDrive/akshara-telugu-ocr/inputs/colab-transfer-v1, open notebook in Colab, select GPU, authorize Drive, run cells1–7 and inspect actual smoke/benchmark before enabling cell8. Native BF16 required; no silentFP16/precision conversion. Reuse the same cloud run name/config for resumption; retain previous snapshots.

- 2026-10-13T06:43:01.811861+00:00: Colab transfer completed and read-back verified:5 archives,2,945,455,311 bytes,33,000 selected image payload hashes and decodes,3 frozen manifest hashes/counts/group separation,31 original model payload files and pilot adapter. Original preservation snapshot31model/32pilot/6manifests matched with zero mismatches. Source snapshot b672f47.48 software tests and notebook schema/12 AST cells passed. Source ZIP refreshed to include pinned HTTPX/API test dependencies; first source ZIP preserved at work/colab-source-dd79f53.zip. No cloud training/authentication or final-test predictions performed. Notebook and guide delivered; user Drive authorization/GPU assignment remain required.

- 2026-10-13T06:47:24.608164+00:00: Continued migration audit found/fixed two reproducible multi-session recovery defects: restore ignored latest pointer and sorted random snapshot suffixes; restored snapshot-checksums could be recopied into a new snapshot and invalidate it. New metadata nanosecond ordering, validated latest-pointer preference, legacy fallback and exclusion of snapshot bookkeeping from active runs implemented. Added restore→snapshot→restore and corrupt-pointer tests;49 software tests pass. Drive connector rechecked: USER_NOT_LOGGED_IN. Local coordinator10604 remains suspended; no active GPU worker. Full cloud training/evaluation still requires Google authorization and assigned GPU. Preparing version2 transfer source; original version1 archives preserved.

- 2026-10-13T07:16:16.412746+00:00: Recovery updatev2 delivered at outputs/Akshara_Colab_Transfer_v2, source55b2902.49 software tests pass. All5 archives and33,000 image payload hashes/decodes, frozen splits,31model payload files/pilot and original31/32/6 preservation hashes verified again; evidence reports/colab-migration/transfer-verification-v2.json. Originalv1 preserved. Existing Drive upload needs only changed source ZIP/index. Notebook unchanged. Full training/validation/final-testing remain unfinished; Google Drive authorization and actual Colab GPU are still required.

- 2026-10-13T07:38:00.137223+00:00: Blocked audit: same missing Google/Colab authorization condition persisted across initial migration handoff, recovery-update continuation and this continuation. Drive search rechecked after transient transport failure and returned USER_NOT_LOGGED_IN. No Colab job handle/assigned GPU is available; local coordinator10604 is still suspended and has no OCR GPU worker. Migration artifacts/recovery tests are ready, but full25k training, candidate validation, sealed3k testing and API parity remain incomplete. No duplicate local/cloud run launched. Next required external action: user opens notebook, mounts Drive, selects supportedGPU, uploads v2 inputs and returns actual startup/smoke/benchmark output. Goal to be marked blocked, not complete.

- 2026-10-13: Account handoff completed. Added the CLI prompt, transfer instructions and clean-clone verifier. `Akshara_Codex_Repo_v2.bundle` was verified with complete history; fresh clone at `704ad4a2bc600c0169b1728c641f7084c1f38224` passed all 49 tests. The initial clean-clone check exposed and fixed a `PYTHONPATH` portability issue in the verifier. No credentials or large private model/data files were added to Git.


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

- 2026-10-13T16:30:28Z: Approved Windows native BF16 preflight. 50 software tests pass. Fresh smoke then synchronized benchmark. Full training not started.


## Approved Windows continuation - 2026-10-13T16:36:03.941611+00:00

User approved local preflight, complete capped study, website integration and Playwright testing. 50 software tests pass. Fresh RTX3050 native BF16 exact-resume/reload smoke passed. Fresh64-example benchmark: 0.641863 images/s, 2.01GiB peak, [0.1332559999991645]s checkpoint cost, 10.82h training-only projection. Losses all finite; no accuracy gain claimed. Details: reports/colab-migration/windows-approved-preflight-20261013.json. Full training checkpoint absent; smoke/benchmark checkpoints are excluded from initialization. Original5000 validation hashes recorded for reuse verification.

Temporary progress page /progress.html added to existing studio; live frozen counts, active-stage progress, validation metrics, selection and API status come from current research endpoints. Playwright visible Chrome confirmed desktop/mobile rendering and API inference paused during GPU work; screenshots output/playwright/akshara-progress-preflight.png and akshara-progress-mobile.png. New coordinator will continue at pilot5000 validation, then selected-initialization smoke, one25000 epoch, validation selection and sealed3000 evaluation. Local recovery snapshots use D:/OCR/backups/word-efficient-v3-local-approved-v1 via existing verified snapshot/controller code. No Colab run or final model claim.

- 2026-10-13T16:36:28Z: Validation: curated-efficient-original. 

- 2026-10-13T16:36:28Z: Validation: curated-efficient-pilot. 

- 2026-10-13T16:42:41.680814+00:00: Approved capped Windows coordinator is live (controller26260/wrapper30668, coordinator11224, GPU evaluator28016), pilot validation 660/5000; original validation hashes unchanged. Periodic local recovery snapshot snapshot-20261013T164133Z-efc2b133 verified. 52 software tests pass. Playwright desktop/mobile progress rendering and studio navigation checked; actual API returns409 while GPU study is active. Prepared gated selected-model launcher and actual API parity checker; these remain unexecuted until study completion. Full epoch, validation selection, sealed3000 test, selected-model connection and API parity remain pending.

- 2026-10-13T16:52:58.644037+00:00: While the existing pilot validation worker remains active, extended only the progress-page frontend with a completed-study gate for final word-crop metrics, paired intervals and raw diagnostics/subgroup metadata. API final summary remains unavailable until coordinator status completed; no final labels, predictions or GPU modules changed. Node syntax check passed and Playwright visibly confirmed the sealed state; screenshot output/playwright/akshara-final-results-sealed.png. Actual final-results rendering must still be verified after the study finishes.

- 2026-10-13T17:01:09.008056+00:00: Existing pilot validation worker28016 and controller26260 verified live. Pilot validation reached 2580/5000, elapsed 1470.11s. No full-validation quality result or initialization selection yet; original5000 validation remains preserved, full25000 epoch and sealed3000 testing still pending. Continue the same coordinator; do not restart or use smoke/benchmark weights for full training.

- 2026-10-13T17:25:27Z: Capped training smoke and exact resume. 

- 2026-10-13T17:26:28Z: Capped25000-word training: epoch1. One initial epoch only. No additional epochs scheduled.


## Validation-selected pilot initialization - 2026-10-13T17:26:48.012990+00:00

Pilot5000 validation completed: raw/NFC CER9.1996%, WER30.38%, raw exact74.14%, 2925.96s, 1.80GiB peak. Original5000 prediction/metric hashes unchanged. Paired215 source-document/duplicate groups,2000 bootstrap replicates seed42: CER reduction interval [0.3548,3.6485]pp supports pilot initialization on validation. Writer identity remains unknown; this is not an independent final result. Config fixes25k maximum, one epoch, seed42, rank8 q/v, LR1e-5, effective batch4 and preserved pilot adapter SHA. New optimizer/scheduler, not a historical optimizer resume. Exact-resume smoke for selected initialization is now live (worker15852); full training, candidate selection, sealed3k and API parity pending. Evidence reports/colab-migration/windows-initialization-selection-20261013.json.

- 2026-10-13T17:28:10.829375+00:00: Validation-selected pilot BF16 exact-resume/reload smoke passed with full config signature 266194952cff5629b36fd132285ca79fe297e1dbcec3c99c37e0ef9bf46ed929. New capped25000 epoch is live, trainer496/wrapper29860, current 40/25000 and 10 updates. Full initialization record confirms preserved pilot path/SHA and new optimizer/scheduler; no smoke/benchmark weights inherited. Original31-file provenance and capped manifests verified again. Checkpoint cadence125 updates; full resume pointer pending its first boundary. Playwright live training screenshot output/playwright/akshara-training-started.png. Candidate validation, selection, sealed3000 comparisons and selected-model API parity remain incomplete.

- 2026-10-13T17:44:43.643825+00:00: First full-training checkpoint step0000125 verified: 125 updates, next_index500, epoch0, BF16, effective batch4 and accumulation_progress0. Adapter/state checksums, optimizer/scheduler, Python/NumPy/Torch/CUDA/augmentation RNG fields and exact dataset/config signature verified by CPU-only load. Initial standalone fingerprint audit used file order rather than reader's seed42 shuffle; corrected audit matches without modifying trainer or checkpoint. Verified snapshot snapshot-20261013T174312Z-6426e08b contains a byte-identical full state.pt and intact recovery checkpoint. Evidence reports/colab-migration/windows-first-full-checkpoint-20261013.json. Training remains active; candidate validation/final test/API parity not complete.

- 2026-10-13T17:55:40.728522+00:00: Full trainer496 continues at 880/25000. Sustained recent100-word median 1.629s/example; current epoch remainder about 10.91h excluding validation/final testing and pauses. Longer than the short preflight projection; no settings or epoch count changed. Laptop power plugged=True; resource evidence reports/colab-migration/windows-sustained-training-observation-20261013.json. First full step125 checksum/RNG/optimizer checkpoint remains preserved; later checkpoints continue every125 updates. No candidate accuracy or final-test claim.

- 2026-10-13T18:00:39.067920+00:00: Capped full training passed1000/25000, 250 optimizer updates, one epoch unchanged. step0000250 checksums and original dataset/config signature verified; step0000125 remains intact. Latest verified snapshot has recovery update 125; full-state bytes match latest=False. Evidence reports/colab-migration/windows-1000-training-milestone-20261013.json. Trainer496 remains active; no restart, precision conversion or training-module edit. Candidate validation, sealed3000 testing and API parity still pending.

- 2026-10-13T18:07:45.859439+00:00: Scheduled snapshot snapshot-20261013T180353Z-fcee5b1c now contains full step0000250 (250 updates, next_index1000). Entire snapshot and checkpoint checksums verified; saved state.pt is byte-identical to live full checkpoint. This supersedes the earlier observed sync lag without changing or deleting any earlier snapshot. Trainer496 remained live at1140/25000; validation/final testing/API parity still pending.

- 2026-10-13T18:55:17.108285+00:00: Sustained slowdown observed near1500 words: recent median~5s/word, GPU utilization16-30%, thermal/power slowdown flags inactive, <2GiB availableRAM, other Chrome renderer using~one CPU core. Closed only the owned idle Playwright window; trainer/server/user browsers preserved. Native Windows CPU topology verified six faster cores (logical0..11, EfficiencyClass1) plus efficiency cores (12..19,class0). Applied reversible CPU-affinity-only trial to trainer496, keeping normal priority, four Torch threads, all model settings, BF16, data, code and system power plan unchanged. Conservative post-change 171-word median 2.370s versus pre-change recent100-word median 5.093s; different words/resource conditions confound causal attribution. Keep observed faster scheduling and monitor; original affinity recorded for rollback. step375 checkpoint verifies next_index1500 and preserved signature. Evidence windows-training-affinity-trial-20261013.json and windows-training-affinity-result-20261013.json. No candidate accuracy or final-test result claimed.

- 2026-10-13T19:02:05.107322+00:00: Full epoch reached2000/25000 and500 optimizer updates. step0000500 checksums, BF16, epoch0, next_index2000 and unchanged config/dataset signature verified. All4 existing full checkpoint generations remain intact. Source code, frozen manifests and one-epoch protocol unchanged; trainer496 continues with recorded performance-core affinity. Candidate validation, sealed3000 and API parity remain pending. Evidence reports/colab-migration/windows-2000-training-milestone-20261013.json.

- 2026-10-13T19:20:34.421758+00:00: One periodic snapshot attempt failed with empty error text (exception type unavailable in controller log); failed .partial-9b0eb1ab43e0486db4e96e5e4e5e3937 preserved. Diagnostic snapshot to separate durable directory succeeded, then normal scheduled snapshot snapshot-20261013T191652Z-de6243de succeeded and its full recovery checkpoint verified. Measured committed memory23.52/25.44GiB near failure inspection; causal attribution unknown. No trainer restart, GPU module edit or earlier artifact deletion. Failure/recovery evidence reports/colab-migration/windows-sync-failure-recovery-20261014.json and windows-sync-diagnostic-20261014.json. Goal remains incomplete while full epoch continues.

- 2026-10-13T19:35:43.764620+00:00: Full epoch reached3000/25000 and750 optimizer updates. step0000750 checksums, BF16, epoch0, next_index3000 and unchanged configuration/dataset signatures verified. All6 prior full checkpoint generations intact. Trainer496/controller26260 verified live; latest scheduled snapshot status verified. One epoch and frozen25k/5k/3k unchanged; no candidate validation, final testing or selected-model API parity claim. Evidence reports/colab-migration/windows-3000-training-milestone-20261014.json.

- 2026-10-13T20:04:34.552182+00:00: One full epoch passed4000/25000,1000 optimizer updates. step0001000 checksums, BF16, epoch0,next_index4000 and unchanged config/dataset signature verified; all8 full checkpoint generations remain intact. Existing trainer496/controller26260 continue; latest sync reports verified. No additional epoch, source/label/manifest change, candidate accuracy or sealed-test claim. Evidence reports/colab-migration/windows-4000-training-milestone-20261014.json.

- 2026-10-13T20:31:18.598528+00:00: Full trainer/coordinator/controller exited after a CPU image-processor allocation failure (~10.3MiB), not CUDA OOM. Versioned failure logs preserved in recovery/cpu-memory-failure-20261013T202629Z. Full step0001125 checksums verified:4500 committed examples,1125 updates,epoch0,BF16,unchanged dataset/config signature. Later unsaved work must replay from optimizer/RNG checkpoint; no epoch reset or smoke initialization. At verified safe boundary, released duplicate prefix image batch before supervised processing and previous training batch/loss after backward/scalar recording.53 software tests pass including token/label preservation and prefix-buffer lifetime regression. Original31-file provenance and frozen25k/5k/3k hashes reverified; both run locks free and RTX3050 nativeBF16 confirmed. Fresh exact-resume smoke in recovery/cpu-memory-preflight-v1/smoke is running; benchmark and safe full resume pending. Candidate validation, sealed final3k and selected-model API parity remain incomplete.

- 2026-10-13T20:34:37.376723+00:00: Fresh recovery smoke passed every actual forward/backward, finite gradient, changed-weight, mid-epoch exact-resume and final-reload inference check in BF16, unchanged selected-init signature 266194952cff5629b36fd132285ca79fe297e1dbcec3c99c37e0ef9bf46ed929. User confirmed unused apps closed; afterward availableRAM~5.0GiB and commit headroom~5.7GiB. Fresh64-example synchronized benchmark now running in recovery/cpu-memory-preflight-v1/benchmark; its weights are excluded from full training. Snapshot exceptions now retain type and traceback instead of empty-message-only evidence.53 tests passed again. Full4500 checkpoint remains preserved, full resume pending benchmark.

- 2026-10-13T20:36:54Z: Validation: curated-efficient-original. 

- 2026-10-13T20:36:54Z: Validation: curated-efficient-pilot. 

- 2026-10-13T20:36:56Z: Capped25000-word training: epoch1. One initial epoch only. No additional epochs scheduled.

- 2026-10-13T20:37:48.289614+00:00: Recovery64-word benchmark completed:0.646752images/s,2.01GiB peakVRAM,0.154448s checkpoint cost; all losses finite. Fresh smoke adapter byte-identical to previous selected-init smoke. User closed unused apps; host memory rechecked before launch. Single existing coordinator resumed full checkpointstep1125 at4500 examples, preserving optimizer/scheduler/RNG/BF16/manifest signature. Actual new log advanced to4525; first8 replayed losses match exactly=True. Reapplied reversible faster-core affinity0..11 only to verified new trainer20148, normal priority/system power unchanged. Controller9084/coordinator18732; new controller logs under recovery/cpu-memory-preflight-v1. Durable snapshot still contains identical4500 checkpoint; old artifacts/failure logs preserved.53 tests pass. Candidate validation, sealed3000 evaluation and selected-model website/API parity still pending. Evidence windows-cpu-memory-recovery-resume-20261014.json.

- 2026-10-13T20:43:09.982695+00:00: Resumed full training passed previous failure point and4680 words. First periodic snapshot after recovery exposed an evidence-archive naming error: copied resume.json without checkpoint was recursively treated as active recovery. Renamed only archived copy to resume-pointer.evidence.json with identical SHA256; original live4500 checkpoint untouched/verified, no trainer restart or active code edit. Immediate independent recovery snapshot snapshot-20261013T204307Z-be99dfe4 fully verified and contains full checkpoint. Existing scheduled controller will retry normal durable storage; snapshot error/type/trace preserved. Full study remains in progress.

- 2026-10-13T20:54:04.992250+00:00: Full epoch reached5000/25000,1250 updates. step0001250 checksums,epoch0,next_index5000,BF16 verified; signatures match prior4000 verified state,full config matches recovery benchmark,frozen25k/5k/3k streaming hashes unchanged. First CPU-only Torch state audit verified optimizer/scheduler,all RNG fields,effectivebatch4 and zero accumulation before whole-manifest MemoryError; second Torch-loaded audit hit hash-buffer MemoryError. Trainer unaffected. Final lightweight no-Torch audit independently verified all10 checkpoint generations,metadata/config/manifest hashes. Scheduled snapshot snapshot-20261013T205223Z-9bf6a62d independently verified after archive pointer fix; recovery index5000 is recorded sync lag. Trainer20148/coordinator18732/controller9084 live. Avoid extra Torch imports alongside memory-limited GPU work; no active GPU code edit,duplicate epoch or final label use. Candidate validation,selection,sealed3000 and website/API parity pending. Evidence windows-5000-training-milestone-20261014.json.

- 2026-10-13T21:07:49.294778+00:00: Single full epoch passed5500/25000 and1375 updates. step0001375 checksums and recovery metadata verified:epoch0,next_index5500,BF16,unchanged dataset/config signatures. Safe pickle-opcode inspection confirms serialized optimizer,scheduler,all RNG and batch/precision fields present without executing pickle/importing another Torch runtime; scope recorded, not a new GPU smoke. All11 checkpoint generations remain intact. Trainer20148/coordinator18732/controller9084 live at5540; scheduled snapshot snapshot-20261013T210249Z-ca744f60 independently verified, recovery next_index5000. No duplicate run,extra epoch,activeGPUcode edit or final label use. Candidate validation,locked selection,sealed3000,selected-model website/API parity remain pending. Evidence windows-5500-training-milestone-20261014.json.

- 2026-10-13T21:08:42.565662+00:00: Scheduled normal durable snapshot snapshot-20261013T210800Z-a824d781 now contains full5500/1375-update recovery checkpoint. Snapshot/checkpoint checksums and state.pt bytes independently verified identical to live latest; earlier snapshot lag resolved. Live single epoch continues; no new run or code edit. Evidence windows-5500-durable-snapshot-20261014.json.

- 2026-10-13T21:21:36.126936+00:00: Single full epoch passed6000/25000,1500 updates. step0001500 checksums and recovery metadata verified:epoch0,next_index6000,BF16,unchanged dataset/config signatures. Frozen25k/5k/3k streaming SHA256 hashes unchanged. Safe pickle-opcode key inspection confirms optimizer,scheduler,all RNG and batch/precision fields present without executing pickle/importing another Torch runtime; scope recorded. All12 checkpoint generations intact. Trainer20148/coordinator18732/controller9084 live at6040; scheduled snapshot snapshot-20261013T211824Z-30810958 independently verified, recovery next_index5500 (sync lag recorded). No duplicate run,extra epoch,activeGPUcode edit or final label use. Candidate validation,locked selection,sealed3000,selected-model website/API parity pending. Evidence windows-6000-training-milestone-20261014.json.
