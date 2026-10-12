# Telugu handwriting OCR · executed word pilot

13 October 2026 · Local RTX 3050 4 GB laptop · 1,000 training / 500 validation / 500 test words.

The word adapter improved grapheme CER by 0.58 percentage points on this fixed test set. The paired bootstrap interval does not establish a CER reduction. These measurements establish word-crop performance only. Whole-page accuracy and performance on the user's own handwriting have not been established.

| Measure | Original IndicOCR | Telugu word adapter |
| --- | ---: | ---: |
| NFC grapheme CER | 15.93% | 15.35% |
| Raw grapheme CER | 15.93% | 15.35% |
| WER | 43.00% | 41.60% |
| Raw exact word match | 66.20% | 68.20% |
| Test samples | 500 | 500 |
| Truncated predictions | 0 | 0 |
| Median inference latency | 0.513 s | 0.538 s |
| 95th percentile latency | 0.793 s | 0.822 s |

The 95% interval for original-minus-adapted CER is [-0.96, 1.79] percentage points, using 2,000 paired bootstrap replicates over 378 source-document candidate groups. These are not verified writer groups. 16 words improved, 4 worsened, and 480 had unchanged edit counts.

## What actually ran

The downloaded bodhan-ai/indic-ocr snapshot matches revision cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25. All 31 downloaded model/code/processor files matched published Git or LFS hashes. The 1,734,372,747-byte recognizer SHA-256 is 40f6a5ce321d65ce18db429c9e8c8b2d2d22d4ec7d71737d150cc0a6edf9ae5f.

The original Qwen3_5ForConditionalGeneration, Qwen3VLProcessor, tokenizer, chat template, prompt, EOS 262146, PAD 262144 and crop area clamp were retained. No alternate checkpoint was substituted. A tensor-by-tensor loader avoided Windows memory-map allocation failure without converting or quantizing the weights.

The smoke test ran 64 real optimizer updates on four training examples. It recorded finite loss/gradients, changed adapter parameters, an exact transcription on its demonstration example, and identical output after adapter save/reload. The smoke adapter was discarded for the real study. Its measured peak allocated CUDA memory was 1.86 GiB; this is a smoke-run peak, not a calibrated whole-study memory benchmark.

The pilot used a clean base model, 319,488 trainable LoRA parameters, rank 8, alpha 16, dropout 0.05, q/v projections in six full-attention layers, one epoch, learning rate 1e-5, microbatch 1, gradient accumulation 4, gradient clipping 1.0 and seed 42. Only answer-token logits were used for the ordinary causal cross-entropy, reducing memory while preserving the objective. Training took 27.5 minutes.

The final adapter was loaded from disk into a fresh original model for test evaluation. Greedy decoding used a 64-token word limit. Original and adapted outputs used exactly the same 500 test examples. Hyperparameters and test manifests were fixed before the training run. The full original test evaluation ran after adaptation, with unchanged original weights; it was not a pre-training full-corpus run. No hyperparameter change was made from test results.

## Dataset evidence

The page archive contained 3,496 labeled images; five exact byte/pixel duplicates were removed, leaving 3,491 usable pages. Internal page splits are audit-only. Its 700-image external challenge test has no public reference labels and was excluded from scored evaluation. Page dataset usage terms remain unresolved for training.

The three word archives contained 88,534 / 19,980 / 17,898 image files. Their ground-truth files contained 80,637 / 19,980 / 17,898 unique labeled paths. The training image and label totals do not match; unpaired images were not counted as training examples. A deterministic bounded audit decoded and checked 8,000 pairs per source split, for 24,000 verified source pairs. One cross-split near-duplicate group was moved wholly into a holdout split, leaving pools of 7,997 training, 8,003 validation and 8,000 test words. Frozen pilot subsets contain 1,000 / 500 / 500 words. No augmentations or OCR pseudo-labels were counted.

Images decoded successfully, labels contained Telugu, and byte/pixel hashes plus dHash candidate grouping were checked. Labels are source-provided ground truth, not newly human-verified transcripts. Source-document groups were inferred from archive paths. Writer identity, pretraining overlap, all unsampled archive members, and all visual near-duplicate candidates remain unverified.

Attribution: IIIT Hyderabad, IIIT-INDIC-HW-WORDS Telugu, CC BY 4.0 as stated on https://ilocr.iiit.ac.in/dataset/23/. Page source: https://ilocr.iiit.ac.in/icdar_2024_hwd/dataset.html. The raw archives and original labels remain unchanged on D:/OCR.

## How to read the results

CER uses NFC extended grapheme clusters. WER splits on whitespace. Digits, punctuation, marks and spelling differences count. Raw and NFC metrics are both saved. The displayed test cards show the first examples in the frozen evaluation order; the analysis JSON also lists the largest adapted errors, edit categories, source-document and length breakdowns.

This test covers isolated words from the downloaded corpus. It does not demonstrate layout quality, complete-page exact match, older orthography, palm-leaf manuscripts, camera-photo robustness or the user's own handwriting. Original model pretraining data overlap is unknown. Human review remains part of the studio workflow.

## Files and preview

Open http://127.0.0.1:8765/research.html for measured results and real test images; open the studio for new uploads. Select Word crop for the measured pilot. Whole page invokes the original layout pipeline and is experimental.

The results folder contains frozen manifests, hashes, raw reference/prediction JSONL, metrics, training logs, model contract, source audit and bootstrap analysis. Telugu_Word_Adapter.zip contains the saved adapter and original model license; base weights stay in D:/OCR/models/indic-ocr. Run Start-Akshara.ps1 from the project directory to restart the local API.

## Observed failure patterns

The largest errors include an English “no text” refusal, repeated unrelated Telugu words, Kannada/Bengali output for Telugu input, Telugu numeral substitutions, and unwanted LaTeX delimiters. These raw outputs were retained and counted as errors. The adapter changed edit counts on only 20 of 500 words: 16 improved, four worsened, and 480 were unchanged. One severe refusal expansion contributes substantial uncertainty to corpus CER. The measured improvement is modest and statistically inconclusive; it does not meet a strong, production-quality improvement gate.

Short words are harder in this test: adapted CER is 27.27% for 1–3 graphemes, 12.20% for 4–6, and 7.98% for 7+. These bins have 179, 296 and 25 examples respectively. The longest-word bin is small.

Future work should review source labels and difficult examples, tune only on validation data, and use a newly untouched test set for any later selected model. No settings were changed to correct these test errors in this study.

## Largest error examples

- Reference: **జ్వాలయై**; original: `[No text or transcription provided]`; adapted: `[No text or math present in the provided image]`; grapheme CER: 1566.67%. Image: `word-pilot-results/examples/14bfd1d7295c947b1017312f5ff2008cf60ed63320b1c8103182064b5b4c336f.jpg`.
- Reference: **నటనలోకాని**; original: `______
వినియోగించుకుంటారు
వినియోగించుకుంటారు`; adapted: `______
వినియోగించుకుంటారు
వినియోగించుకుంటారు`; grapheme CER: 383.33%. Image: `word-pilot-results/examples/f8ffb95dd6e181c2309465749ca8eccbe6f8ca4f4ed1fea84c9954926fb23c56.jpg`.
- Reference: **౯౭**; original: `$$52$$`; adapted: `$$52$$`; grapheme CER: 300.00%. Image: `word-pilot-results/examples/bb7ba4721483f59b67d89b6b674dd006b3dfb60e3c7b373acd4d3c57adf01e4c.jpg`.
- Reference: **వర**; original: `$$వ$$`; adapted: `$$వ$$`; grapheme CER: 200.00%. Image: `word-pilot-results/examples/2bca927763747e6d274503b5c8fea98758f7a0e8717da52a60adf1a8d974a8fc.jpg`.
- Reference: **బండ్ల**; original: `ಒಂದ್ಲಿ`; adapted: `ಒಂದ್ಲಿ`; grapheme CER: 150.00%. Image: `word-pilot-results/examples/f667238915e7fb46298169d3dde5951b2c258881bd0fd9133de17b7bf6c5cb1a.jpg`.
