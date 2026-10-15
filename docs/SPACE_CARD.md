---
title: Akshara Telugu OCR Studio
emoji: ✍️
colorFrom: purple
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
license: other
license_name: indic-open-model-license-v1.0
license_link: LICENSE.md
---

# Akshara Telugu OCR Studio

[Website](https://akshara-ocr-seven.vercel.app/) · [Source and installation](https://github.com/Thanujgthub/akshara-ocr) · [Selected model](https://huggingface.co/thanujhf/akshara-telugu-handwriting-ocr)

**Built with IndicOCR from Bodhan AI / AI4Bharat.** Independent project; no upstream endorsement.

This free static Space hosts the existing studio, completed study snapshot and measured analysis. **No GPU inference runs in this Space.** Use the documented local native-BF16 service for new image transcription. Imports, editing, exports and reports work here. No paid hardware was selected.

Completed frozen **25,000 training / 5,000 validation / 3,000 sealed-test** word-crop study, one effective epoch. Selected final exact **76.20%**, grapheme CER **7.4534%**, WER **24.40%**; original exact **66.4333%**. Validation alone selected the candidate. Unknown writer identity/pretraining overlap and label-quality/word-crop limitations remain; no worldwide rank is established.

The original study recorded 85 software tests, 64/64 local API parity and desktop/mobile Playwright checks. Publication checks are separate from model accuracy and cloud inference.

Data: [IIIT Hyderabad Telugu words](https://ilocr.iiit.ac.in/dataset/23/), stated [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The base/derivative license is included unmodified. Original base weights are obtained separately from their publisher.
