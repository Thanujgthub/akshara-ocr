"""Render the frozen 2026-10-15 Windows v3 study; no inference or model selection.

The dated narrative describes this measured run, not arbitrary future experiments.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def render(root, output, snapshot):
    root, output, snapshot = map(Path, (root, output, snapshot))
    if output.exists() or snapshot.exists():
        raise FileExistsError('Use fresh report paths; preserve earlier reports')
    selection = read(root / 'selection.json')
    analysis = read(root / 'reports/final-selected-analysis-v1.json')
    summary = read(root / 'final-summary.json')
    parity = read(root / 'api-parity-selected-v1/parity.json')
    protocol = read(root / 'protocol.json')
    if sha(root / 'selection.json') != '32e18a5c4a29f3855bf323f51944a7ccae53659f60982d3d40b284960e63f00b':
        raise RuntimeError('This dated renderer is bound to the frozen Windows v3 selection')
    if read(root / 'status.json')['status'] != 'completed' or summary['selection'] != selection:
        raise RuntimeError('Complete the locked study first')
    if analysis['selection_sha256'] != sha(root / 'selection.json') or analysis['final_summary_sha256'] != sha(root / 'final-summary.json'):
        raise RuntimeError('Reporting evidence differs from locked study')
    if not parity['passed'] or parity['mismatches'] or parity['selection_sha256'] != analysis['selection_sha256'] or parity['validation_manifest_sha256'] != protocol['manifests']['validation']['sha256']:
        raise RuntimeError('Actual selected API parity has not passed')
    names = {'original': 'Original IndicOCR', 'pilot': 'Preserved pilot', 'candidate': 'Akshara candidate (selected)'}
    final = analysis['raw_nfc_final_metrics']
    timing_keys = ['latency_median_seconds', 'latency_p95_seconds', 'peak_allocated_vram_bytes', 'peak_reserved_vram_bytes', 'peak_vram_scope', 'resumed_predictions_count', 'generated_predictions_this_process', 'elapsed_seconds_this_process']
    diagnostic_keys = ['script_contamination_rate', 'refusal_rate', 'malformed_output_rate', 'repetition_candidate_rate', 'abstention_rate', 'resource_abstention_rate', 'truncated_count']
    data = {'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'selection': selection['variant'], 'selection_sha256': analysis['selection_sha256'], 'final_summary_sha256': analysis['final_summary_sha256'], 'protocol': protocol['manifests'], 'model_revision': 'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25', 'training_config': {k: v for k, v in selection['config'].items() if not k.startswith('initial_adapter')}, 'initialization': 'Validation-selected preserved pilot; new optimizer/scheduler for capped manifest.', 'models': {}, 'paired_original_selected': analysis['paired_original_selected'], 'api_parity': parity, 'software_tests_passed': 85, 'limitations': summary['limitations'], 'external_global_rank': None, 'external_rank_scope': 'No common external benchmark submission establishes an Akshara worldwide rank.'}
    for variant, values in final.items():
        if sha(root / 'final' / variant / 'predictions.jsonl') != analysis['prediction_sha256'][variant]:
            raise RuntimeError('Frozen final predictions changed')
        measured = summary['final_metrics'][variant]
        data['models'][variant] = {'label': names[variant], 'final': values, 'validation': {k: summary['validation'][variant][k] for k in ['examples', 'micro_cer', 'micro_wer', 'raw_exact_match']}, 'timing': {k: measured[k] for k in timing_keys}, 'diagnostics': {k: measured[k] for k in diagnostic_keys}, 'subgroups': measured['subgroups'], 'predictions_sha256': analysis['prediction_sha256'][variant]}
    p = lambda value: f'{100 * value:.4f}%'
    lines = ['# Akshara capped Telugu word-crop study', '', f"Measured locally on Windows; report generated {data['generated_utc']}.", '', f"The validation-selected candidate achieved **{p(final['candidate']['raw_exact_match'])} exact-word match** on 3,000 sealed crops, versus **{p(final['original']['raw_exact_match'])}** for the original checkpoint. This is agreement with source-provided labels, not whole-page accuracy or a worldwide rank.", '', '## Protocol and preservation', '', 'Frozen 25,000 training / 5,000 validation / 3,000 final-test pairs; one effective training epoch, 6,250 optimizer updates, seed42, native BF16. Original31-file IndicOCR revision, processor/tokenizer, prompt, preprocessing, deterministic decoding, labels and historical artifacts were preserved. Validation alone chose pilot initialization and locked the candidate before final inference. Each model used the identical final inputs; the baseline resumed its saved2,227 records and generated only the remaining773.', '', 'LoRA rank8 on q/v; learning rate1e-5, microbatch1, accumulation4, clipping1.0, augmentation disabled. The raw training log retains26,054 rows:25,000 unique positions plus1,054 historical recovery-replayed rows, not additional verified examples or an extra effective epoch. Recorded cumulative training-loop time84,164.822s (23.38h) excludes later validation and some discarded recovery/preflight work; the initial short-benchmark estimate is not actual epoch time.', '', '## Independent final results', '', '| Model | Crops | Raw CER | NFC CER | Raw WER | NFC WER | Raw exact | NFC exact |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for variant, m in final.items():
        lines.append('| ' + ' | '.join([names[variant], str(m['examples'])] + [p(m[k]) for k in ['raw_micro_cer', 'nfc_micro_cer', 'raw_micro_wer', 'nfc_micro_wer', 'raw_exact_match', 'nfc_exact_match']]) + ' |')
    lines += ['', 'CER uses Unicode grapheme clusters. WER uses whitespace-separated tokens. Raw strings, spelling, punctuation and numerals are preserved; NFC is used only for explicitly named NFC metrics. All six raw/NFC aggregate values coincide on this sample. Lower CER/WER and higher exact match are better.', '', '## Paired uncertainty: original versus selected', '', 'Percentile bootstrap with2,000 repetitions, seed42, resampling128 frozen source-document/duplicate components. These are not verified independent writers. Positive differences favor the already-selected candidate; final results did not change selection.', '', '| Measure | Difference (percentage points) | Paired95% interval |', '|---|---:|---:|']
    paired = analysis['paired_original_selected']
    for key, value in paired['point_differences'].items():
        lo, hi = paired['intervals_95'][key]
        lines.append(f'| {key} | {100*value:.4f} | [{100*lo:.4f}, {100*hi:.4f}] |')
    lines += ['', '## Validation and generalization', '', '| Model | Validation crops | CER | WER | Exact word |', '|---|---:|---:|---:|---:|']
    for variant, m in summary['validation'].items():
        lines.append(f"| {names[variant]} | {m['examples']} | {p(m['micro_cer'])} | {p(m['micro_wer'])} | {p(m['raw_exact_match'])} |")
    lines += ['', 'Candidate validation exact match81.38% is separate from final exact match76.20%; the held-out gap is retained, not tuned away. The final result contains714 non-exact crops. Zero heuristic diagnostic flags do not mean zero transcription errors.', '', '## Latency, VRAM and output diagnostics', '', 'RTX3050 Laptop4GB; Torch2.11.0+cu128, CUDA12.8, nativeBF16. Generation latency excludes upload/HTTP, input processing and transfer. Hardware load and thermal conditions varied; these are local observations, not universal speed rankings.', '', '| Model | Median generation(s) | p95(s) | Peak allocated(GiB) | VRAM scope |', '|---|---:|---:|---:|---|']
    for variant, model in data['models'].items():
        t = model['timing']
        lines.append(f"| {names[variant]} | {t['latency_median_seconds']:.4f} | {t['latency_p95_seconds']:.4f} | {t['peak_allocated_vram_bytes']/2**30:.4f} | {t['peak_vram_scope']} |")
    lines += ['', 'Baseline elapsed427.19s and peak VRAM cover only its remaining773 predictions; its latency distribution retains all3,000 records. Pilot elapsed2,093.52s and candidate2,116.18s cover their full3,000-example evaluations. Never divide baseline3,000 by the remaining-process elapsed time.', '', '| Model | Script contamination | Refusal | Malformed | Repetition flag | Abstention | Truncated count |', '|---|---:|---:|---:|---:|---:|---:|']
    for variant, model in data['models'].items():
        m = model['diagnostics']
        lines.append('| ' + ' | '.join([names[variant]] + [p(m[k]) for k in ['script_contamination_rate', 'refusal_rate', 'malformed_output_rate', 'repetition_candidate_rate', 'abstention_rate']] + [str(m['truncated_count'])]) + ' |')
    lines += ['', 'The recovery benchmark used64 real training crops with8 warm-up crops:0.628564 steady images/s, median input/transfer0.039404s,98 GPU samples (mean utilization81.27%), peak allocation2,154,064,384bytes, checkpoint0.105579s. Losses were finite (range0.004829..4.998307). Diagnostic weights were never promoted or credited as more verified training.', '', '## Shared input-defined subgroups: original versus selected', '', 'Output-dependent error-flag groups are excluded from this paired input subgroup table. Detailed source-document and diagnostic subgroups remain in each immutable metrics JSON.', '', '| Subgroup | N | Original CER | Selected CER | Original WER | Selected WER | Original exact | Selected exact |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    original = summary['final_metrics']['original']['subgroups']
    selected = summary['final_metrics'][selection['variant']]['subgroups']
    for key in sorted(set(original) & set(selected)):
        if key.startswith(('document:', 'error:')):
            continue
        b, a = original[key], selected[key]
        lines.append('| ' + ' | '.join([key, str(a['examples'])] + [p(m[k]) for k in ['micro_cer', 'micro_wer', 'raw_exact_match'] for m in [b, a]]) + ' |')
    lines += ['', '## Software, API and website evidence', '', '85 post-study software tests passed. Actual original/selected API parity passed64/64 HTTP requests on the first32 declared validation crops, matching exact decoded text, token IDs, truncation and intended adapter. Headed Playwright verified selected upload, review/edit reset, copy, TXT/Markdown/JSON downloads, constant-pixel abstention, desktop1440x1000/mobile390x844 layout, final metrics and uncertainty display. No final-test crops were replayed for these checks. Studio/dashboard consoles reported zero application errors or warnings. Real mobile filename/toolbar overflow and a completed-progress display bug were fixed and rechecked. Heuristic text confidence remains uncalibrated; uniform-pixel abstention does not establish general blank/unreadable-image detection.', '', 'Live studio: http://127.0.0.1:8765/ . Completed dashboard: http://127.0.0.1:8765/progress.html . Restart with Start-AksharaSelected.ps1 after checking no API already owns port8765. Latest resumable checkpoint, best-validation adapter and versioned selected export are separate. Source and artifacts useD:; original C: work remains preserved. Local D: snapshots are checksum verified but share the physical SSD; no offsite/Drive backup or executed full-snapshot restore is claimed here.', '', '## Limitations', '', *['- ' + value for value in summary['limitations']], '- Writer identities are unknown: source-document/duplicate grouping does not prove writer-disjoint generalization.', '- Historical-exposure and split audits found no known held-out overlap; original pretraining overlap remains unknown.', '- Technical image/label checks are not complete human semantic label verification.', '- One seed and one capped continuation epoch do not establish between-seed robustness.', '- Page/layout, faint-camera-image robustness and other datasets remain unbenchmarked.', '- No worldwide ranking follows from this single controlled word-crop study. External scores require matching datasets, units, normalization and protocols.', '', '## Artifact identities', '', f"- Locked selection SHA256: `{analysis['selection_sha256']}`", f"- Final summary SHA256: `{analysis['final_summary_sha256']}`", f"- Final manifest SHA256: `{analysis['final_manifest_sha256']}`", *[f'- {name} final prediction SHA256: `{digest}`' for name, digest in analysis['prediction_sha256'].items()], '', 'Canonical evidence lives in D:/OCR/runs/word-efficient-v3: protocol.json, selection.json, full/ checkpoints, final/*/ raw predictions and metrics, reports/final-selected-analysis-v1.json, api-parity-selected-v1/, selected-exports/latest.json and recovery/windows-d-drive-preflight-v7/. Browser evidence and measured milestones are indexed by reports/colab-migration/windows-selected-api-playwright-20261015.json. Original checkpoint is licensed separately and is not redistributed in the adapter ZIP. No GitHub push or Vercel deployment was performed.', '']
    output.parent.mkdir(parents=True, exist_ok=True)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(lines), encoding='utf-8')
    snapshot.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='D:/OCR/runs/word-efficient-v3')
    parser.add_argument('--output', required=True)
    parser.add_argument('--snapshot', required=True)
    args = parser.parse_args()
    render(args.run, args.output, args.snapshot)
