# Akshara capped Telugu word-crop study

Measured locally on Windows; report generated 2026-10-15T17:09:27.836300+00:00.

The validation-selected candidate achieved **76.2000% exact-word match** on 3,000 sealed crops, versus **66.4333%** for the original checkpoint. This is agreement with source-provided labels, not whole-page accuracy or a worldwide rank.

## Protocol and preservation

Frozen 25,000 training / 5,000 validation / 3,000 final-test pairs; one effective training epoch, 6,250 optimizer updates, seed42, native BF16. Original31-file IndicOCR revision, processor/tokenizer, prompt, preprocessing, deterministic decoding, labels and historical artifacts were preserved. Validation alone chose pilot initialization and locked the candidate before final inference. Each model used the identical final inputs; the baseline resumed its saved2,227 records and generated only the remaining773.

LoRA rank8 on q/v; learning rate1e-5, microbatch1, accumulation4, clipping1.0, augmentation disabled. The raw training log retains26,054 rows:25,000 unique positions plus1,054 historical recovery-replayed rows, not additional verified examples or an extra effective epoch. Recorded cumulative training-loop time84,164.822s (23.38h) excludes later validation and some discarded recovery/preflight work; the initial short-benchmark estimate is not actual epoch time.

## Independent final results

| Model | Crops | Raw CER | NFC CER | Raw WER | NFC WER | Raw exact | NFC exact |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original IndicOCR | 3000 | 12.7839% | 12.7839% | 42.2667% | 42.2667% | 66.4333% | 66.4333% |
| Preserved pilot | 3000 | 12.1907% | 12.1907% | 40.1667% | 40.1667% | 67.4667% | 67.4667% |
| Akshara candidate (selected) | 3000 | 7.4534% | 7.4534% | 24.4000% | 24.4000% | 76.2000% | 76.2000% |

CER uses Unicode grapheme clusters. WER uses whitespace-separated tokens. Raw strings, spelling, punctuation and numerals are preserved; NFC is used only for explicitly named NFC metrics. All six raw/NFC aggregate values coincide on this sample. Lower CER/WER and higher exact match are better.

## Paired uncertainty: original versus selected

Percentile bootstrap with2,000 repetitions, seed42, resampling128 frozen source-document/duplicate components. These are not verified independent writers. Positive differences favor the already-selected candidate; final results did not change selection.

| Measure | Difference (percentage points) | Paired95% interval |
|---|---:|---:|
| raw_cer_reduction | 5.3305 | [4.3664, 6.4936] |
| nfc_cer_reduction | 5.3305 | [4.3664, 6.4936] |
| raw_wer_reduction | 17.8667 | [15.4798, 20.3005] |
| nfc_wer_reduction | 17.8667 | [15.4798, 20.3005] |
| raw_exact_gain | 9.7667 | [8.3444, 11.1631] |
| nfc_exact_gain | 9.7667 | [8.3444, 11.1631] |

## Validation and generalization

| Model | Validation crops | CER | WER | Exact word |
|---|---:|---:|---:|---:|
| Original IndicOCR | 5000 | 10.6956% | 32.3800% | 73.2400% |
| Preserved pilot | 5000 | 9.1996% | 30.3800% | 74.1400% |
| Akshara candidate (selected) | 5000 | 5.7027% | 19.3000% | 81.3800% |

Candidate validation exact match81.38% is separate from final exact match76.20%; the held-out gap is retained, not tuned away. The final result contains714 non-exact crops. Zero heuristic diagnostic flags do not mean zero transcription errors.

## Latency, VRAM and output diagnostics

RTX3050 Laptop4GB; Torch2.11.0+cu128, CUDA12.8, nativeBF16. Generation latency excludes upload/HTTP, input processing and transfer. Hardware load and thermal conditions varied; these are local observations, not universal speed rankings.

| Model | Median generation(s) | p95(s) | Peak allocated(GiB) | VRAM scope |
|---|---:|---:|---:|---|
| Original IndicOCR | 0.5656 | 0.8829 | 1.7897 | remaining_examples_in_this_process_only |
| Preserved pilot | 0.6224 | 0.9285 | 1.8018 | entire_evaluation |
| Akshara candidate (selected) | 0.6274 | 0.9228 | 1.8018 | entire_evaluation |

Baseline elapsed427.19s and peak VRAM cover only its remaining773 predictions; its latency distribution retains all3,000 records. Pilot elapsed2,093.52s and candidate2,116.18s cover their full3,000-example evaluations. Never divide baseline3,000 by the remaining-process elapsed time.

| Model | Script contamination | Refusal | Malformed | Repetition flag | Abstention | Truncated count |
|---|---:|---:|---:|---:|---:|---:|
| Original IndicOCR | 0.0000% | 0.0000% | 0.0000% | 0.0667% | 0.0000% | 1 |
| Preserved pilot | 0.0000% | 0.0000% | 0.0000% | 0.0333% | 0.0000% | 0 |
| Akshara candidate (selected) | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 0 |

The recovery benchmark used64 real training crops with8 warm-up crops:0.628564 steady images/s, median input/transfer0.039404s,98 GPU samples (mean utilization81.27%), peak allocation2,154,064,384bytes, checkpoint0.105579s. Losses were finite (range0.004829..4.998307). Diagnostic weights were never promoted or credited as more verified training.

## Shared input-defined subgroups: original versus selected

Output-dependent error-flag groups are excluded from this paired input subgroup table. Detailed source-document and diagnostic subgroups remain in each immutable metrics JSON.

| Subgroup | N | Original CER | Selected CER | Original WER | Selected WER | Original exact | Selected exact |
|---|---:|---:|---:|---:|---:|---:|---:|
| crop_quality:eligible | 3000 | 12.7839% | 7.4534% | 42.2667% | 24.4000% | 66.4333% | 76.2000% |
| length:1-3 | 976 | 16.9783% | 11.7512% | 34.2213% | 25.6148% | 67.3156% | 74.4877% |
| length:4-6 | 1804 | 11.7171% | 6.6033% | 41.9069% | 23.5588% | 67.4058% | 77.1064% |
| length:7+ | 220 | 11.6447% | 5.0420% | 80.9091% | 25.9091% | 54.5455% | 76.3636% |
| numerals:absent | 2993 | 12.6807% | 7.3912% | 42.0982% | 24.2900% | 66.5553% | 76.3114% |
| numerals:present | 7 | 107.1429% | 64.2857% | 114.2857% | 71.4286% | 14.2857% | 28.5714% |
| quality:low_contrast | 1 | 1850.0000% | 325.0000% | 2300.0000% | 200.0000% | 0.0000% | 0.0000% |
| quality:other | 2999 | 12.2102% | 7.3542% | 41.5138% | 24.3414% | 66.4555% | 76.2254% |
| script:Telugu | 3000 | 12.7839% | 7.4534% | 42.2667% | 24.4000% | 66.4333% | 76.2000% |
| source:iiit-words | 3000 | 12.7839% | 7.4534% | 42.2667% | 24.4000% | 66.4333% | 76.2000% |

## Software, API and website evidence

85 post-study software tests passed. Actual original/selected API parity passed64/64 HTTP requests on the first32 declared validation crops, matching exact decoded text, token IDs, truncation and intended adapter. Headed Playwright verified selected upload, review/edit reset, copy, TXT/Markdown/JSON downloads, constant-pixel abstention, desktop1440x1000/mobile390x844 layout, final metrics and uncertainty display. No final-test crops were replayed for these checks. Studio/dashboard consoles reported zero application errors or warnings. Real mobile filename/toolbar overflow and a completed-progress display bug were fixed and rechecked. Heuristic text confidence remains uncalibrated; uniform-pixel abstention does not establish general blank/unreadable-image detection.

Live studio: http://127.0.0.1:8765/ . Completed dashboard: http://127.0.0.1:8765/progress.html . Restart with Start-AksharaSelected.ps1 after checking no API already owns port8765. Latest resumable checkpoint, best-validation adapter and versioned selected export are separate. Source and artifacts useD:; original C: work remains preserved. Local D: snapshots are checksum verified but share the physical SSD; no offsite/Drive backup or executed full-snapshot restore is claimed here.

## Limitations

- Source labels not all human verified
- Unknown writer identity and possible pretraining overlap
- Isolated words, not page or sentence recognition
- No99% or market-leadership claim
- One training seed/epoch; no additional epochs scheduled
- Writer identities are unknown: source-document/duplicate grouping does not prove writer-disjoint generalization.
- Historical-exposure and split audits found no known held-out overlap; original pretraining overlap remains unknown.
- Technical image/label checks are not complete human semantic label verification.
- One seed and one capped continuation epoch do not establish between-seed robustness.
- Page/layout, faint-camera-image robustness and other datasets remain unbenchmarked.
- No worldwide ranking follows from this single controlled word-crop study. External scores require matching datasets, units, normalization and protocols.

## Artifact identities

- Locked selection SHA256: `32e18a5c4a29f3855bf323f51944a7ccae53659f60982d3d40b284960e63f00b`
- Final summary SHA256: `214253fbefcd37adf53e6b2ba8b3f6c11cdce42780b1c8179ebd2c7b75a28e9f`
- Final manifest SHA256: `5247e8ff10612838ac251bea3c41407b904034e9301be302078a4bb4fb85b1f4`
- original final prediction SHA256: `cd41c6d96553367fb6500bf0eec3a00d389b645774bb2a02ddfaba617a8363a0`
- pilot final prediction SHA256: `575a195a3526596a360edfa59bc1c2d9f5a129c85448fedc1973177060aa2d1c`
- candidate final prediction SHA256: `b814e9a19c7db104e1f9b51f10acda4669a4829d18e435c49a95346978282e31`

Canonical evidence lives in D:/OCR/runs/word-efficient-v3: protocol.json, selection.json, full/ checkpoints, final/*/ raw predictions and metrics, reports/final-selected-analysis-v1.json, api-parity-selected-v1/, selected-exports/latest.json and recovery/windows-d-drive-preflight-v7/. Browser evidence and measured milestones are indexed by reports/colab-migration/windows-selected-api-playwright-20261015.json. Original checkpoint is licensed separately and is not redistributed in the adapter ZIP. No GitHub push or Vercel deployment was performed.
