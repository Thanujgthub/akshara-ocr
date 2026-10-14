# Akshara Telugu OCR — Codex CLI account handoff

This file is the operational handoff for another Codex CLI account. It is deliberately separate from the research objective and does not contain credentials. The other account must inspect the repository and current files before acting.

## What is already preserved

- Repository: `C:\Users\ASUS\Documents\Codex\2026-10-12\co\outputs\akshara-ocr`
- Current Git checkpoint: see `git rev-parse HEAD`; the handoff package records the exact bundle revision.
- Original IndicOCR checkpoint: `D:\OCR\models\indic-ocr`, revision `cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25`; 31-file provenance is recorded in `reports/model_provenance.json`.
- Source data: `D:\OCR\research-v2`.
- Active capped run: `D:\OCR\runs\word-efficient-v3`.
- Pilot adapter: `D:\OCR\runs\word-pilot-v1\trained\adapter`.
- Python runtime: `D:\OCR\runtime\venv\Scripts\python.exe`.
- Private Colab transfer: `..\Akshara_Colab_Transfer_v2` from this repository's `outputs` directory.

The active frozen counts are 25,000 training, 5,000 validation and 3,000 final-test pairs. The final set is sealed and must not be inspected until validation-only model selection is locked. Source labels are not all human semantically verified; writer identity and possible pretraining overlap are unknown. Word-crop results do not establish page or sentence accuracy.

Current measured evidence:

- Original-model 5,000-example validation: CER 10.6956%, WER 32.38%, exact word 73.24%, 1.80 GiB peak allocated VRAM.
- Local BF16 resume smoke: interrupted/resumed and uninterrupted adapter tensors matched; reload inference matched.
- Local 64-example benchmark: 0.63117 images/second, 1.54281-second median batch, 2.01 GiB peak allocated, about 11 active hours projected for the 25,000-example epoch. This is not a Colab benchmark.
- 49 software tests pass. Notebook schema and 12 code cells pass AST validation.

The local coordinator is intentionally held between stages. Verify live processes before any action. Never launch a duplicate local or cloud stage, and never terminate an active process merely because a historical PID appears in a document.

## Same Windows computer

If the second Codex account runs on this same computer, keep the existing repository and `D:\OCR` paths in place. Do not copy model weights or raw data. Open PowerShell and run:

```powershell
Set-Location 'C:\Users\ASUS\Documents\Codex\2026-10-12\co\outputs\akshara-ocr'
git status --short
git log --oneline -8
& 'D:\OCR\runtime\venv\Scripts\python.exe' -m unittest discover -s tests -q
Get-Content .\CODEX_CLI_PROMPT.md | Set-Clipboard
codex
```

Paste the clipboard contents as the first message in the new Codex CLI session. If `codex` is not installed, install or update it using the official Codex instructions, then check `codex --version`. Do not copy the current account's `.codex` credentials or any token into the repository.

## Different computer

Copy these items through a private, trusted channel:

1. `Akshara_Codex_Repo.bundle` from the handoff package.
2. `CODEX_CLI_HANDOFF.md`, `CODEX_CLI_PROMPT.md` and `handoff\verify_handoff.ps1`.
3. The complete private `Akshara_Colab_Transfer_v2` directory if using Colab.

The transfer directory is about 2.74 GiB and contains five archives. It includes the original model snapshot, pilot adapter, frozen manifests and selected images. It does not contain credentials. Keep it private and do not upload it to a public repository.

For a new local Windows machine, also provide the original `D:\OCR\research-v2`, `D:\OCR\models\indic-ocr`, and `D:\OCR\runs\word-pilot-v1` paths, or set the documented environment variables to equivalent paths. The original model license and attribution files must travel with the model. Do not recreate labels from predictions.

Clone the Git bundle into a new checkout:

```powershell
New-Item -ItemType Directory -Force 'C:\OCR-Handoff' | Out-Null
Set-Location 'C:\OCR-Handoff'
git bundle verify 'C:\path\to\Akshara_Codex_Repo.bundle'
git clone 'C:\path\to\Akshara_Codex_Repo.bundle' akshara-ocr
Set-Location .\akshara-ocr
git log --oneline -8
```

Then place the private transfer directory where the prompt expects it, or edit only the path variables in the prompt after verifying the new absolute paths. Run the verification script before training:

```powershell
powershell -ExecutionPolicy Bypass -File .\handoff\verify_handoff.ps1 -ProjectRoot (Get-Location)
```

## Colab continuation

Open `notebooks/akshara_ocr_colab_training.ipynb`, choose a GPU runtime, and mount private Drive. Upload the contents of `Akshara_Colab_Transfer_v2` to `MyDrive/akshara-telugu-ocr/inputs/colab-transfer-v1/` (the notebook's configured folder name remains v1 for compatibility). Run cells 1–7 first. Review the actual GPU name, native BF16 support, smoke result and throughput. Enable the launch flag in cell 8 only after the benchmark succeeds and single-runtime ownership is confirmed.

If the v1 archives are already uploaded, replace only `akshara-source.zip` and `transfer-index.json` with the v2 copies. The model and image archives are unchanged. Use the same cloud run name, precision and configuration when resuming. Do not claim a speedup until the assigned GPU has been measured.

## Required order for the next Codex

1. Read `AGENTS.md`, `PROJECT_STATE.md`, `WORK_LOG.md`, this file and `CODEX_CLI_PROMPT.md`.
2. Verify the current Git revision, active processes and frozen manifest hashes.
3. Run the software tests before making changes.
4. Check whether the user has supplied actual Colab GPU/smoke/benchmark output. If not, prepare or explain the external handoff; do not fabricate cloud results.
5. Continue the capped workflow: original/pilot validation, validation-only initialization choice, resume smoke, one 25,000-pair epoch, validation selection, then one sealed 3,000-pair final evaluation.
6. Update `PROJECT_STATE.md` and `WORK_LOG.md` at every milestone.
7. Report measured metrics, uncertainty, runtime, VRAM, limitations and exact next action. Never promise 99% accuracy or market leadership without evidence.

- 2026-10-14T05:12:46.105788+00:00: While verified trainer30976 continues at9740, prepared independent post-study selected export module without editing active GPU modules. Existing coordinator uses legacy unversionedZIP (currently absent); newmodule gates on completedstudy/locked selection/final counts/frozen hashes/oneepoch evidence, copies selectedadapter into separate immutable versionedfolder, includes original31 provenance,fsyncs staged bytes,verifies source/destination/ZIP CRC+SHA,atomically commits fresh folder/archive and then latestpointer. Never modifies original/best/resumable/legacyZIP.6 focused synthetic filesystem tests pass; actual live-study invocation rejected withno exportside effects. Actual export stillpending afterstudy; run python -m ocr.export_selected --run D:/OCR/runs/word-efficient-v3 before final artifact handoff. Full65 tests pending safeGPUboundary. API/parity launcher continues to reference locked selectedsource; delivery copy is byte-identical,independent artifact. Evidence windows-selected-export-preparation-20261014.json.

- 2026-10-14T06:03:47.747078+00:00: Confirmed existing generation preserves raw decodedstrings (no whitespace/tokenization cleanup). Prepared independent reporting supplement for rawWER plus raw/NFC metrics and original-versus-selected paired95 intervals (includingselectedPilot case absent from coordinator summary). Gated oncompletedstudy/lockedselection/frozen3k; verifies rawinput IDs/references/leakagegroups and hashes before/after; never rerunsinference or changesmodelchoice.6 focused synthetic metric/gating tests pass after correcting Unicodefixture to canonically decomposable TeluguAI(U0C48); sourceUnicode15 normalization verified. Actual live-study gate refused withoutreadingsealeddata orcreatingoutput. Export caninclude supplement onlywhenselectionSHA/variant/finalmanifestSHA match;8 exporttests pass. No activeGPUmodule edit; trainer30976 live at11140. Aftercompletedstudy run selected_analysis to ROOT/reports/final-selected-analysis-v1.json BEFORE export_selected; actualanalysis/export stillpending. Full73 suite pending safeGPUboundary. Evidence windows-selected-analysis-preparation-20261014.json.


- 2026-10-14T06:23:54.386239+00:00: Prepared dashboard supplement exposure gated oncompletedstudy and matching lockedselection,summary and frozenfinalmanifest hashes; never reads finalpredictions. Frontend displays raw/NFC CER,WER,exact plus original-versus-selected six paired95 intervals whenverifiedsupplement available.4 focused monitor tests pass (2newgatingtests),JS syntax passed; full75 suite pending safeGPUboundary. WebsiteAPI module only; no activeGPUmodule edit or liveAPIrestart. Newroute activates atselectedAPIlaunch afterstudy. Actual headedPlaywright livepage verified frozen25k/5k/3k,priorvalmetrics,sealedfinalresults and inferencepaused; screenshot visually inspected,ownbrowserclosedaftercheck. Onlyfavicon404 consoleerror observed. Completed-results render/APIparity remainpending. Same trainer30976 live at11800/25000. Evidence reports/colab-migration/windows-dashboard-selected-report-preparation-20261014.json.


- 2026-10-14T08:55:00.930140+00:00: CUDA-memory recovery passed75fulltests,fresh nativeBF16 exact-resume/reload smoke (adapterbyte-identicalto previous) and64-image synchronizedbenchmark:0.571078images/s,2.01GiB peak,0.182867s checkpointcost,finite losses. Original31/frozenprotocol/free locks verified beforelaunch; no precision/dataset/model/epoch change. Single controller23348/coordinator36580/newtrainer18796 resumed full13000/3250update checkpoint,not smoke/benchmarkweights; freshrawlog starts13001,latest13114. All114 comparedreplayed losses exactlymatch archivedpost13000 logs; unsavedworkreplays withoutnewuniqueexamples/extraepoch. Process-only fastercoreaffinity0..11,normalpriority reapplied; temporarykeepawake boundtonewcontroller,hardwarepowerlimitsunchanged. Independent freshsnapshot snapshot-20261014T085418Z-498f3db7 fullyverified with identicalfull13000state; normal scheduledcontrollerretry pending,oldMemoryError retained. Failurearchive immutable. Candidatevalidation,selection,sealed3000,website/API parity and actualanalysis/export remainpending. Evidence reports/colab-migration/windows-cuda-memory-recovery-resume-20261014.json.
