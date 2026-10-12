# Executed archive audit

The page archive contained 3,496 labeled images; five exact byte/pixel duplicates were removed, leaving 3,491 usable pages. Internal page splits are audit-only. Its 700-image external challenge test has no public reference labels and was excluded from scored evaluation. Page dataset usage terms remain unresolved for training.

The three word archives contained 88,534 / 19,980 / 17,898 image files. Their ground-truth files contained 80,637 / 19,980 / 17,898 unique labeled paths. The training image and label totals do not match; unpaired images were not counted as training examples. A deterministic bounded audit decoded and checked 8,000 pairs per source split, for 24,000 verified source pairs. One cross-split near-duplicate group was moved wholly into a holdout split, leaving pools of 7,997 training, 8,003 validation and 8,000 test words. Frozen pilot subsets contain 1,000 / 500 / 500 words. No augmentations or OCR pseudo-labels were counted.

Images decoded successfully, labels contained Telugu, and byte/pixel hashes plus dHash candidate grouping were checked. Labels are source-provided ground truth, not newly human-verified transcripts. Source-document groups were inferred from archive paths. Writer identity, pretraining overlap, all unsampled archive members, and all visual near-duplicate candidates remain unverified.

Attribution: IIIT Hyderabad, IIIT-INDIC-HW-WORDS Telugu, CC BY 4.0 as stated on https://ilocr.iiit.ac.in/dataset/23/. Page source: https://ilocr.iiit.ac.in/icdar_2024_hwd/dataset.html. The raw archives and original labels remain unchanged on D:/OCR.

