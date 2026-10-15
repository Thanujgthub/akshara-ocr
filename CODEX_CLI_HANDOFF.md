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


- 2026-10-14T10:04:10.526367+00:00: Prepared APIliveGPUworker guard for observedrecoverybenchmark gap: oldfailedcoordinator state allowedmodel_ready=True despite livebenchmark (model_load_verifiedFalse,no actualAPIinference/modelconflict evidenced). ExactPython-m training/smoke/evaluation/benchmark commands nowblock APIinference evenwith failedstate; APIparity and shelltext excluded.2 focusedregression tests pass,real liveworker detection verified. No activeGPUmoduleedit or liveAPIrestart; activateat selectedAPIlaunch afterstudy. ExistingAPIcurrently correctlypaused for runningstudy. Onfuture recovery markstatuspreparing beforeGPUpreflight. Full77suite pending safeGPUboundary; full75passedbeforecurrentrun. Trainer18796 live at15140. Candidateval/selection/sealedfinal/API stillpending. Evidence reports/colab-migration/windows-gpu-serving-guard-preparation-20261014.json.


- 2026-10-14T15:19:02.189289+00:00: Sitesreadonlyreconnection audit: retained .openai/hosting.json identity appgprj_6accf32e12f08191892e9c788ee1c852; get_site returnedProjectNotFound,successful list_sites(limit50,include_editable) returnedzeroaccessibleSites. No creation,replacement,writecredential,remoteedit/deploy oraudiencechange; credentialsneverprinted/storedon disk. Owner/editoraccountaccess needed for existinghostedSite; oneasynchronousconnectionquestion submitted whileindependentWindowsstudy continues. Localstudio/progressHTTP/API healthy,inferencepaused; trainer18796 live at17080. No cloudGPU/modelaccess claimed. Finish authorizedtraining/val/final/localAPIparity andpreparedpublication work; do notsilentlysubstitute a newSite ormarkfullgoalcomplete withhostedscopeunverified. Evidence reports/colab-migration/windows-sites-reconnection-audit-20261014.json.


- 2026-10-14T15:36:52.620025+00:00: User clarified deploymentorder: finish modeltraining,validation,sealedfinaltests,standardschecks andanalysis first; Vercelaccount deployment andGitHub publication(account thanujgthub) deferred,notauthorizedfornow. User saysconnection is throughcomputer; no cloud/site/GitHub/Vercel auth verified fromthat statement. Do notpush,deploy,createSite orask furtherhosting questions duringresearch. Existinglocalstudio/APIparity/Playwright remainrequired; priorSitespublicationaccess isnotcurrentresearchblocker. Preservehostingidentity/source/artifacts. Same trainer18796 live at17540.


- 2026-10-14T15:42:20.006892+00:00: Trainer18796/coordinator36580/controller23348 exited with CPU MemoryError in PIL image-to-array preprocessing at rawprogress17580/25000. All GPUstudy workers verified absent. Preserved failure/status/rawlog/progress/controller evidence in D:\OCR\runs\word-efficient-v3\recovery\cpu-memory-failure-20261014T154220Z. All35 checkpoint generations SHA-verified including17000 and17500; atomic pointer points to full17500/4375 updates, BF16, unchanged signatures. No restart or precision/model/data changes. Recovery preflight pending; final selection/test/API still incomplete. Deployment deferred per user. Evidence reports\colab-migration\windows-17500-memory-failure-audit-20261014.json.


- 2026-10-14T15:49:34.407924+00:00: CPU-memory recovery passed77fullsoftwaretests, nativeBF16 real-image interrupted/resumed/reload smoke and64-image synchronizedbenchmark (0.618166images/s, peak2154064384bytes). Original31/frozen25k/5k/3k and freepipeline/controller locks reverified. Actual trainer20928/coordinator23964/controller36060 resumed full17500/4375update checkpoint; wrapper processes distinct, not duplicate studies. Sameprecision/config/epoch, process-only coreaffinity0..11/normalpriority, temporaryidle-sleep helper boundcontrollerwrapper11252. 48replayedpost17500losses exactlymatch archivedlog; currentprogress17540. Normal snapshot scheduling remainsactive. No source/model/data/learning change; memoryfailure preserved, exact initiatingpressure cause remainsunknown. Candidateval/selection/sealedfinal/APIparity stillpending. Vercel/GitHub deployment deferred. Evidence reports\colab-migration\windows-17500-memory-recovery-resume-20261014.json.


- 2026-10-14T16:10:57.963133+00:00: Second CPUmemory failure inthis recovery atprogress18160 (array1.06MiB); Windowsevents2004/1003 at16:07:06UTC explicitlydiagnose lowvirtualmemory (prior15:37:48event alsoverified), notnewlabel/imagecorruption evidence. Preservedfailure/rawlog/controller/progress inD:\OCR\runs\word-efficient-v3\recovery\cpu-memory-failure-20261014T160801Z. Allstudyworkers includingcontroller nowexited; lastcontrollerdurablesnapshot snapshot-20261014T160728Z-8b4089a7 SHA-verified with full18000checkpoint/statebyteidentity. Win32_PageFileSetting configuresC andD 8000..10000MB each, butWin32_PageFileUsage reports onlyC (8508MB); currentcommitlimit25752944640bytes. D localNTFS has~119GiBfree; C~10.45GiBfree. No OSsettingchanged/reboot/processkill/trainingrestart. Need usertosavework andrestartWindows; pagefilesettingtakes effectatstartup perMicrosoftdocs, actualDactivation mustbecheckedafterreconnect. Thenfreshfulltests/nativeBF16/smoke/benchmark/free-lock/provenancegates before resume verifiedfull18000,not smoke. No extraprecision/epochs/final-labelchoice. Candidateval/selection/sealedfinal/API incomplete; deploymentdeferred. Evidence reports\colab-migration\windows-18160-memory-failure-audit-20261014.json.


- 2026-10-14T16:14:39.590548+00:00: Addedread-only ocr.windows_memory pre-loadgate usingnativeGetPerformanceInfo, distinguishescommitcapacity fromfreeRAM andfailclosed oninvalid/unsupportedmeasurement. Conservative6GiBmodelallowance (recent~6GBprivate) plus3GiBoperationalreserve; noclaimof calibratedsafety orchangedscientificsettings.3newtests coverhighRAM/lowcommit rejection, invalidallowances/measurements andunsupportedplatform; full80softwaretests pass withallGPUstudyworkerabsent. Actualgatefails at4928962560bytes headroom versus9GiB requirement; evidence savedwithoutOSchanges/GPUload. Windowsbootunchanged,Dpagefileinactive,userrestartquestionstillpending; do notretrytrainingblindly. Afterreconnect first run `D:/OCR/runtime/venv/Scripts/python.exe -m ocr.windows_memory --output <fresh-path.json>` thenverifyruntimeDpagefile/provenance/free locks/tests/nativeBF16/real smoke/synchronizedbenchmark beforefull18000resume. APIparity/websitefinaltesting remainafterstudy. Evidence reports\colab-migration\windows-memory-gate-preparation-20261014.json.


- 2026-10-14T16:16:21.082327+00:00: Externalmemoryblock audited thirdconsecutivegoalturn: sameboot,noactiveDpagefile,noGPUstudyworkers, measuredcommitheadroom5020626944bytes belowpre-loadallowance/reserve; full18000checkpoint/index integrity stillverified anddurablebackup retained. Newread-only guard and80fullsoftwaretests completed; no remainingauthorized GPUdependentstage canstart safely untilcapacity changes. Userrestartquestionpending,notrepeated; noOSsetting/reboot/processkill/newtraining performed. Goalblockedpendinguser savework/restartWindows/reconnect,notcomplete oruserpaused. Freshruntimepagefile/capacity+fullpreflight beforefull18000resume; validation/final/API/selectedwebsite stillunfinished anddeploymentdeferred. Evidence reports\colab-migration\windows-memory-external-block-audit-20261014.json.


- 2026-10-15T04:50:52.743491+00:00: Userreactivatedgoal; newcwdD:/CODEX isnotAksharacheckout. LocatedoriginalcheckoutunchangedatC:/Users/ASUS/Documents/Codex/2026-10-12/co/outputs/akshara-ocr. UserrevokedpreviousAGENTSinstructions; directtask cappedprotocol/artifactpreservation stillapply. NewWindowsbootverified(timestamp1792034071500), Dpagefilestillnotactive, GPUidle/noOCRworkers. Original31/frozen25k/5k/3k/freepipeline+controllerlocks andfull18000checkpoint/durablebackup SHA/statebyteidentityverified.80fullsoftwaretests passafterrestart. Currentmemorygatefails(~6.35GiBheadroomvs9GiB operationalallowance); Ollama apphas~3.86GiBprivate/~3GiBRSS, largestcurrentconsumer. Nextconcreteuseraction isquitOllamasafely,thenrecheckactualmemorybeforefreshnativeBF16/realresume smoke/64benchmark/full18000resume. Nootherapps/processesstopped,noOSsettingschange,noGPUmodel/traininglaunch. Existingcompletedoriginal/pilotvalretained; candidate/final/API/Playwrightpending; Vercel/GitHubdeferred. Evidence reports\colab-migration\windows-postrestart-audit-20261015.json.


- 2026-10-15T05:05:31.212180+00:00: UserexplicitlyrequestedallactiveworkunderD:/CODEX/OCR, Ollamaremovalifunused,andlocalhostwebsite. ClonedexistingGit history toD:/CODEX/OCR/akshara-ocr andSHA-verified26historicaluntrackedartifacts; originalCcheckoutuntouched. Existingmodel/data/checkpoints remainD:/OCR tokeepfrozenpaths/hashes. Ollama notdependency; registereduninstallersucceeded(exit0,noreboot), noOllamaprocess/executable; recursiveleftoverdatacleanup rejectedbyautomaticreview(blockedbypolicy), leftoverfoldersuntouched,no bypass. Localwebsite/API nowservedfromD: at127.0.0.1:8765, logs/tempD:. HeadedPlaywright actualdesktop/mobile rendering/screenshots inspected, width375<=390,no consoleerrors in freshbrowser, HTTP200/204 andmultipart409 guardverified; fixedfavicon404, pausedETA andfalseGPUactivity wording. Ownautomationbrowserclosedformemory; userURLremainslive.83fullsoftwaretests andJS/PowerShellsyntaxchecks pass. AddedWindowscontroller early2GiBcommit STOP guardwithpreservedmanualreason/probefailure handling. Explicitoperationalpre-loadreserve2.5GiB+6GiBmodelallowance passesafterOllamaremoval; originalCLI3GiBdefault unchanged, nolearning/precision/config/fingerprint/epoch change. FreshnativeBF16/realresume smoke/64benchmark pendingbeforefull18000resume. Modelquality/selectedAPIparity/finalwebsiteinference stillunfinished; Vercel/GitHubdeferred. Evidence reports\colab-migration\windows-d-drive-migration-and-website-20261015.json.


- 2026-10-15T05:12:30.118165+00:00: D-drive recovery complete: original31/frozen25k/5k/3k/free locks andfull18000checkpoint verified;83fullsoftwaretests pass; actualnativeBF16RTX3050/Torch2.11cu128/CUDA12.8, freshreal-image interrupted/resumed/reloadsmoke allpass.64images synchronizedbenchmark:0.639324images/s,warm8=12.401216s,medianinput/transfer0.040673s,peak2154064384B,checkpoint0.118799s,finite losses; rawutilization/input/loss records retained. With explicit2.5GiBpreloadreserve+6GiBallowance andearly2GiBruntimeSTOPguard, singleactualtrainer10768/coordinator8412/controller10000 (wrappers20712/10788/7600) resumedfull18000/4500updates,not smoke/benchmarkweights. AllworkerscwdD:/CODEX/OCR/akshara-ocr; temp/logsD:. Coreaffinity0..11/normalpriority processonly, temporaryidle-sleephelper16544boundcontrollerwrapper7600; nohardware/powerplanchange. 55replayedpost18000losses exactlymatch archive; latestprogress18040,freshrawrows55,noSTOP. OriginalCcheckout/artifacts untouched; existingoriginal/pilotval reused; remainingcandidateval/selection/sealedfinal/analysis/export/APIparity/selectedwebsiteinference pending. Website127.0.0.1:8765 livefromD:, usercaninspect; softwarePlaywrightdesktop/mobile passed, not OCRqualityproof. Ollamaappuninstalled, leftoverdatadeletionblockedbyautomaticreview, no bypass. Vercel/GitHubdeferred. Evidence reports\colab-migration\windows-d-drive-full18000-resume-20261015.json.


- 2026-10-15T05:30:10.677748+00:00: Verified graceful Windows memory-guard stop at 18,380/25,000 (4,595 updates), BF16 unchanged. Full step-0004595 and final durable snapshot snapshot-20261015T052237Z-122595b7 checksum-verified; source/snapshot state bytes match. All study workers exited; no new allocation crash, historical failure.json preserved. STOP and terminal state archived under recovery/memory-guard-stop-20261015T052700Z and STOP remains pending explicit verified recovery. User directs core training, validation, sealed final testing and website/API verification first; comparison page and ranking research deferred until afterward. Fixed API guard so paused/failed unfinished capped study cannot advertise historical pilot as selected; completed capped study ignores retired-run busy status. 85 full software tests pass. Fresh recovery preflight pending; current native commit headroom below explicit 8.5GiB pre-load requirement, so no GPU model/training launched. Frozen25k/5k/3k and one initial epoch preserved. Evidence reports/colab-migration/windows-18380-safe-memory-stop-20261015.json.


- 2026-10-15T05:37:04.641615+00:00: Fresh D-drive recovery preflight passed85fullsoftwaretests, original31/frozen25k/5k/3k/free-lock checks, actualnativeBF16RTX3050, real-image interrupted/resumed/uninterrupted/reloadsmoke. Fresh64-image benchmark passed directprocess exit0:0.592348images/s,warm8=13.688713s,medianinput/transfer0.043399s,peak2154064384B,checkpoint0.118706s,finite losses; rawinput/GPUutil/loss records retained. Source history bundle and215trackedfileSHAindex preserved. Verified full18380/4595update checkpoint and durable snapshotstate identical; explicitlyarchived/consumed STOP only aftergates. Singleactualtrainer23612/coordinator11248/controller22600 (wrappers13116/23632/11976) nowadvancedto18400,finite losses,BF16/config/dataset/oneepoch unchanged. Existing2GiBearlymemorysafe-stop unchanged; noOSsettings orotherapptermination. Temporaryidle-sleephelper2888 boundcontrollerwrapper11976; processaffinity0..11/normalpriorityonly. APIrestartedfromD:; realHTTPhealthmodel_readyFalse/model_load_verifiedFalse andmultipart409 confirmed; no concurrentOCRinference. Trainingremainingprojectionabout3.1activehours excludesvalidation/finaltests/disconnects. Completedoriginal/pilot5000validationreused. Candidatevalidation/selection/sealedfinal/APIparity unfinished; ranking/comparisonresearch/page deferreduntilcorecompletion; Vercel/GitHubpublicationdeferred. Evidence reports/colab-migration/windows-full18380-recovery-resume-20261015.json.


- 2026-10-15T05:54:47.478984+00:00: Singleactualtrainer23612 reached19,000/25,000 (76%oneepoch,notaccuracy),4750updates; newstep0004750/index/atomicpointerSHAverified. Frozen25k/5k/3k hashes/BF16/signature/datasetfingerprint unchanged. Rawpost18380segment contiguouswithfinite losses andzero saved-boundaryreplay. Tenminute/20sample nativeWindowsmemorytrajectory preserved withSHA: headroommin5118988288B,max5311500288B; actualtrainerprivateabout5.5GB. Monitorreadonly,noGPUmodel/OS/processrestart; noSTOP. Normalcontroller backupscontinue; nextselection/candidatevalidation/sealedfinal/APIparity/selectedbrowser gates pending. Ranking/comparison page andpublication stilldeferred. Evidence reports/colab-migration/windows-19000-training-checkpoint-20261015.json and reports/colab-migration/windows-18380-recovery-memory-trajectory-20261015.json.


- 2026-10-15T05:58:03.350175+00:00: RealheadedPlaywright verifiedupdateddatasetregistryandlivedashboarddesktop/mobile. Fixedremainingstaticpilotpoolcards toshowactivefrozen25k/5k/3k; allhistoricalpilotcountsretainedexplicitlyinhistorynote. ActualDOMandvisuallyinspectedscreenshotspass,375documentwidth<=390viewport,zeroconsoleerrors/warnings. Bothownbrowsersclosed; screenshotSHAcopiesinrunrecovery fornormalsnapshots. NotselectedOCRinference/APIparity/accuracyproof. Sameactualtrainer23612 liveat19100,noSTOP. Normaldurablesnapshot snapshot-20261015T055718Z-bb067a2a independentlyverifiedallhashes/full19000andstatebyteidentity. Full85softwaretests passedbeforelaunch; UI-onlychangescheckedbyJSsyntax/liveHTTP/realbrowser; noGPUsource/config/model/restart/newlabels. Ranking/comparisonpage anddeploymentdeferred. Evidence reports/colab-migration/windows-19000-website-playwright-20261015.json.


- 2026-10-15T06:09:38.574699+00:00: Sameactualtrainer23612 reached19,500/25,000 (78%oneepoch,notaccuracy),4875updates. Immutable step0004875/index/atomicpointerSHAverified; frozen25k/5k/3k, BF16/signature/fingerprint unchanged. Actualpost18380rawsegment remainscontiguous/finite withbatch4updatepositions; no replay/restart/newGPUmodel/extraepoch. Readonlymemory/checkpointwatch terminatednormallyafterseeing19500; all21samples andSHA preserved, noSTOP. Candidateval/lockedselection/sealedfinal/selectedAPIparity andrealselectedwebsiteOCR stillpending; ranking/comparisonpage andpublication deferred. Evidence reports/colab-migration/windows-19500-training-checkpoint-20261015.json.


- 2026-10-15T06:23:43.752874+00:00: SecondgracefulWindowsmemoryguardSTOP inD-drive recovery at19,748/25,000,4937updates; nativeheadroom2124046336B below2GiBreserve at06:16:12UTC. Allstudyworkers verifiedexited; finalcontroller exit0. Fullstep0004937/index/atomicpointerandfinalsnapshot snapshot-20261015T061642Z-8b0b1487 verifiedallSHA/statebyteidentity. Notnewallocationcrash; historicalfailure.json preserved. STOP/terminalstate/controller/progress archivedrecovery/memory-guard-stop-20261015T0616Z; STOP remainsunconsumed. Fresh85fullsoftwaretests passedinwindows-d-drive-preflight-v3, noGPUlaunch. Currentpreloadgate fails(~7.71GiBheadroomvs8.5GiB); oneconcreteuserquestionpending tocloseunusedapps whilekeepingCodexopen, thenremeasurebeforefreshBF16/smoke/benchmark/full19748resume. C8000MBpagefileonlyruntime; C/D8000..10000MB configured, DsamehealthybootNVMe, noOSchanges. Candidateval/selection/sealedfinal/APIparity unfinished; ranking/comparisonpage andpublicationdeferred. Evidence reports/colab-migration/windows-19748-safe-memory-stop-20261015.json.


- 2026-10-15T06:25:38.447875+00:00: Fresh85fullsoftwaretests passafter19748safeSTOP. NativeEnumPageFilesW independentlyenumeratesonlyCpagefile(2048000pages); configured/registryDentrydoesnotproveactivecapacity. Notadmin,noOS/pagefile/fan/power changes; Dinactivationcause unresolved. Current8.5GiBpre-loadgate stillfails; unused-app closure questionpending. Dashboardnowexplicitlysaysverifiedsaved19748withlastperiodicrecord19740; preservedarchivedterminalstate. Newmanualappend-onlysnapshot snapshot-20261015T062537Z-9cc2752a allSHA/full19748/statebyteidentity verified, includesSTOParchive/newCPUpreflight/nativepagefileevidence. Closedto20000watchterminateduponactualsafeSTOP,not20kcompletion; rawSHA preserved. Remainresumableatfull19748; noGPUmodel/restart/smoke/benchmark launched. Finalselection/test/API unfinished; rankingdeferred. Evidence reports/colab-migration/windows-19748-recovery-readiness-20261015.json.


- 2026-10-15T06:31:20.334010+00:00: Secondconsecutivepost19748memoryblockaudit; checkpoint/freeworkers/freelocks reverified. CPUpreflightnowcomplete:85fullsoftwaretests, original31fileSHA, all33,000frozenimagebytehashes/paths/headers, exact25k/5k/3k counts/hashes andnobyte/pixel/leakageidentitycross-split overlap. Identity-onlyaudit scanned118,515source metadata rows and3277knownhistorical trained/evaluated/probe identities: final3000 haszeroID/source-document/byte/pixel overlaps withknownhistoricalexposure. Nofinalprediction/label-basedchoice/human-label-quality orunknownwriter/pretraining claim. Currentpreloadgatepassed=False; userunused-appclosure actionstillpending,noGPUmodel/smoke/benchmark/restart/STOPconsumption. Allnextrequiredremainingstages dependonactualmemorycapacity. Evidence reports/colab-migration/windows-19748-cpu-preflight-integrity-20261015.json.


- 2026-10-15T06:32:57.495148+00:00: PreservedallCPU-readyrecoveryevidence/new19748handoff/sourcehistorybundleHEAD560c9e0 inappend-onlysnapshot snapshot-20261015T063232Z-9b46b751, allsnapshotSHAverified. ActualpausedAPIhealthmodel_load_verifiedFalse andmultipartpredict409 verified; keep-awakehelperreleased, noGPUmodelrun. Currentpreloadgatepassed=False, headroom7978913792Bvs9126805504Brequired. Userunused-appclosure questionpending. AllusefulCPU-onlypreparationcomplete; nextactualGPUdependentstage requirescapacityrecovery,notgenericpermission/credentials. Secondconsecutivepost19748blockaudit,goalincompleteandactive. Evidence reports/colab-migration/windows-19748-cpu-ready-backup-20261015.json.
