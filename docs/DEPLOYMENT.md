# Publishing the completed Akshara checkpoint

The model study is complete. Deployment does not start training or repeat the sealed test.

## Services and boundaries

| Destination | Published content | GPU inference |
|---|---|---|
| GitHub | Existing source/history, installation guide, aggregate reports, reproducible deployment configuration | Runs on your separately configured machine |
| Vercel | Existing studio, analysis, downloadable aggregate results and completed study snapshot | No GPU runtime is included |
| Hugging Face model repository | Exact selected LoRA adapter, original export metadata/checksums, model card and upstream license | Downloadable weights; not an inference endpoint |
| Hugging Face static Space | Same website and completed report | No GPU runtime is included |

The interface can review/edit/export text without a model. Fresh OCR requires the native-BF16 GPU service. A successful website deployment is not evidence of cloud inference parity. No paid hardware is selected automatically. An HTTPS site cannot reliably call an HTTP localhost API; run the local studio for local inference.

## Build and inspect the public website

Requires Node.js 20 or newer. From the repository root:

```powershell
node scripts/build_public_site.mjs
python -m http.server 8787 --directory public-release --bind 127.0.0.1
```

Open `http://127.0.0.1:8787/` and `/analysis.html` and `/progress.html`. The build copies only the existing `dist` assets and generates a clearly labeled results snapshot; it never packages runtime caches, credentials, base weights or the training dataset. It refuses to overwrite an existing build. For another preview use a fresh path, e.g. `node scripts/build_public_site.mjs output/public-preview-2`.

## Vercel

```powershell
npx vercel login
npx vercel --prod
```

Select your own account and the Akshara project. Root `vercel.json` builds the static site using Node and serves `public-release`. No Python server or model is deployed to Vercel. Add the returned production URL to GitHub's About / Website field and README. Use Vercel's GitHub connection for subsequent pushes; no tokens belong in committed files.

## Hugging Face

Authenticate using `python -m huggingface_hub.cli.hf auth login` in the intended environment. The browser device flow does not require pasting a token into chat. Publish the exact selected export in a model repository; keep `adapter/adapter_model.safetensors`, `adapter/adapter_config.json` and every checksum-covered file byte-identical. Add the original full license and a model card outside the checksum-covered files. Do not merge into or replace the original base model.

The static Space uses YAML `sdk: static` and `app_file: index.html`, and receives the built site assets. It incurs no selected GPU hardware charge. Moving to an online model service requires separate GPU provisioning, preserved precision/input contracts, access controls, upstream license compliance and actual hosted API parity verification.

## Preservation

The Windows canonical run, original 31-file base, frozen manifests, raw labels/predictions, latest resumable checkpoint, best validation adapter and final selected export remain separate and untouched. The publication contains aggregate results and the selected derivative; it is not an offsite backup of every raw dataset/run artifact. Never tune on the published final outcomes.
