# Architecture decision · 12 October 2026

Preserve Route B, the official layout → block recognition → reading order pipeline. This is an integration decision, **not a verified fine-tuning decision**.

The public model card identifies IndicDocLayout (PP-DocLayoutV3 / RT-DETR), IndicBlockOCR (Qwen3.5-0.8B), and the Sarvam-30B tokenizer. Model metadata API returned revision `cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25`, gated=`auto`. No checkpoint downloaded. An unauthenticated request to the recognizer config was attempted; see research log. No alternate checkpoint was substituted.

The official repository OCR README states that its training recipe trains layout only. It provides a Transformers path and a vLLM path, but no recognizer training recipe. The snapshot model card documents `IndicOCR.from_pretrained(repo).parse(path)` returning a dict with Markdown and ordered block JSON. The included model bridge follows that documented API and rejects an incompatible output schema. It is unverified against real weights.

Route A is deferred: checkpoint configs, processor/chat-template, actual model class, prompt-token masking, image resolution and one backward update cannot be verified without access. Route B recognizer adaptation is also deferred until authorized crop/transcript pairs and the exact checkpoint training contract are available. The official repository's layout script is deliberately not relabeled recognizer training.

## Environment observed

Windows, Python 3.9.4, Node 25.6.0. NVIDIA RTX 3050 laptop GPU, 4096 MiB VRAM, driver 617.42. No Torch, PIL, regex or huggingface_hub in the initial Python environment; an isolated CPU/toolkit environment was created and tested. GPU fit is not established. Use a separately provisioned Linux CUDA machine for model experiments; do not assume the weight file size predicts memory usage.

## Model gate still required

Accept terms yourself in Hugging Face; download an immutable revision; use the official installer in an isolated Linux environment. Inspect tokenizer, processor, chat template, generation defaults and modules from that exact snapshot. Establish inference parity, finite loss/gradients, prompt masking, changed adapter weights, save/reload parity and tiny-subset overfit before implementing a scaled LoRA run. No generic LoRA training script is provided as a false substitute for that proof.

Sources: https://huggingface.co/bodhan-ai/indic-ocr and https://github.com/Bodhan-AI/bodhan_genai/blob/main/src/bodhan_genai/ocr/README.md
