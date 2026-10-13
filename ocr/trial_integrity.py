"""Read-only completed-trial hashes and honest resumed-evaluation resource scope."""
import argparse, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path('D:/OCR/runs/word-scale-v2')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def resource_scope(metrics, predictions):
    latencies=[r.get('latency_seconds') for r in predictions]
    valid=bool(latencies) and all(isinstance(x,(int,float)) and math.isfinite(x) and x>=0 for x in latencies)
    total=sum(latencies) if valid else None
    elapsed=metrics.get('elapsed_seconds_this_process')
    evidence=valid and isinstance(elapsed,(int,float)) and elapsed+.5<total
    return {'generation_latency_sum_seconds':total,'metrics_process_elapsed_seconds':elapsed,
            'prediction_reuse_evidence':bool(evidence),
            'validation_peak_comparable':False if evidence else None,
            'validation_peak_scope':'Resumed process only; full evaluation peak unavailable' if evidence else
                'Recorded metrics process only; complete fresh evaluation cannot be proved from stored metadata alone',
            'method':'Single-sample serial generation: stored generation latencies exceed metrics-process elapsed time when earlier predictions were reused. No peak is reconstructed or estimated.',
            'scores_changed':False}


def audit(root, output):
    if output.exists():raise FileExistsError('Use a new audit path')
    completed={};skipped=[]
    for folder in sorted((root/'trials').iterdir()):
        if not folder.is_dir():continue
        barrier=folder/'training_complete.json'
        if not barrier.exists():skipped.append(folder.name);continue
        barrier_hash=sha(barrier)
        best=json.loads((folder/'best.json').read_text(encoding='utf-8'))
        evaluation=folder/f"epoch-{best['epoch']}/validation"
        metric_file=evaluation/'metrics.json';metric_hash=sha(metric_file)
        metrics=json.loads(metric_file.read_text(encoding='utf-8'))
        predictions=[json.loads(s) for s in (evaluation/'predictions.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
        if len(predictions)!=metrics['examples']:raise RuntimeError('Prediction count mismatch: '+folder.name)
        scope={**resource_scope(metrics,predictions),'metrics_sha256':metric_hash}
        files={str(p.relative_to(folder)):sha(p) for p in sorted(folder.rglob('*'))
               if p.is_file() and p.name!='resource-scope.json'}
        if sha(barrier)!=barrier_hash or sha(metric_file)!=metric_hash:raise RuntimeError('Trial changed during audit')
        # Add an annotation file; never rewrite the original metric or predictions.
        sidecar=evaluation/'resource-scope.json'
        if sidecar.exists():
            if json.loads(sidecar.read_text(encoding='utf-8'))!=scope:raise RuntimeError('Preserve existing scope annotation; investigate changed evidence')
        else:
            with sidecar.open('x',encoding='utf-8') as f:json.dump(scope,f,indent=2)
        completed[folder.name]={'files':files,'resource_scope':scope}
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'completed_trials':completed,
            'skipped_incomplete_trials':skipped,'original_metrics_predictions_weights_modified':False,
            'scope':'Completed v2 trials only; immutable originals and test examples not interpreted'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    r=audit(ROOT,Path(a.output));print(json.dumps({'completed':list(r['completed_trials']),
        'skipped':r['skipped_incomplete_trials'],'reuse_evidence':[n for n,v in r['completed_trials'].items() if v['resource_scope']['prediction_reuse_evidence']]}))
