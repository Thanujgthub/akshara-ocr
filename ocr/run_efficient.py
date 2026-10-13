"""Capped continuation: existing data, validation initialization, one epoch, sealed test."""
import json,os,sys,time,traceback,subprocess,shutil,zipfile,platform
from pathlib import Path
from importlib.metadata import version
from .run_scale import command,config,evaluate,register,milestone,PROJECT
from .scale_experiment import sha
from .research_io import save
from .scale_analysis import load,paired
from .portable_paths import resolve_path,run_lock

ROOT=Path(os.environ.get('OCR_RUN_ROOT','D:/OCR/runs/word-efficient-v3'))
PILOT=resolve_path(os.environ.get('OCR_PILOT_ADAPTER','D:/OCR/runs/word-pilot-v1/trained/adapter'))


def verify():
    p=json.loads((ROOT/'protocol.json').read_text(encoding='utf-8'))
    counts={k:v['count'] for k,v in p['manifests'].items()}
    if not 0<counts['train']<=25000 or counts['validation']!=5000 or counts['final-test']!=3000:
        raise RuntimeError('Capped frozen counts do not meet the protocol')
    for name,v in p['manifests'].items():
        if sha(ROOT/(name+'.jsonl'))!=v['sha256']:raise RuntimeError('Frozen manifest changed: '+name)
    original=json.loads((PROJECT/'reports/model_provenance.json').read_text(encoding='utf-8'))
    for entry in original['files']:
        if sha(resolve_path(os.environ.get('INDIC_OCR_REPO','D:/OCR/models/indic-ocr'))/entry['file'])!=entry['sha256']:raise RuntimeError('Original checkpoint/processor snapshot changed')
    return p


def resource_snapshot():
    import psutil
    nvidia=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used,temperature.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
    return {'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'gpu_observation':nvidia.stdout.strip(),
        'ram_total_bytes':psutil.virtual_memory().total,'ram_available_bytes':psutil.virtual_memory().available,
        'storage_free_bytes':shutil.disk_usage(ROOT).free,'python':sys.version,'platform':platform.platform(),
        'versions':{n:version(n) for n in ['torch','transformers','peft','accelerate','safetensors','regex','Pillow']},
        'model':os.environ.get('INDIC_OCR_REPO','D:/OCR/models/indic-ocr'),'revision':'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25'}


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    if not (ROOT/'protocol.json').exists():raise RuntimeError('Allow the existing capped data audit to finish before starting this pipeline')
    lock_context=run_lock(ROOT/'pipeline.lock');lock_context.__enter__()
    if (ROOT/'final-summary.json').exists() and (ROOT/'status.json').exists() and json.loads((ROOT/'status.json').read_text())['status']=='completed':
        print('Capped study already completed; no repeated final evaluation.');lock_context.__exit__(None,None,None);return
    try:
        protocol=verify()
        if not (ROOT/'resource-environment.json').exists():save(ROOT/'resource-environment.json',resource_snapshot())
        base={'seed':42,'prompt':'telugu_literal','preprocessing':'official','rank':8,'targets':['q','v'],
              'lr':1e-5,'augmentation':False,'accumulation':4,'microbatch_size':1,'gradient_clip':1.0,
              'maximum_training_examples':25000,'maximum_epochs':1}
        original=evaluate('curated-efficient-original',base,ROOT/'validation.jsonl',root=ROOT)
        register('curated-efficient-original',original,root=ROOT)
        pilot=evaluate('curated-efficient-pilot',base,ROOT/'validation.jsonl',PILOT,root=ROOT)
        original_path=ROOT/'experiments/curated-efficient-original/predictions.jsonl'
        pilot_path=ROOT/'experiments/curated-efficient-pilot/predictions.jsonl'
        initial_ci=paired(load(original_path),load(pilot_path));register('curated-efficient-pilot',pilot,initial_ci,root=ROOT)
        # A small point-estimate difference is not evidence to inherit pilot weights.
        use_pilot=pilot['micro_cer']<original['micro_cer'] and initial_ci['cer_improvement_supported']
        cfg={**base}
        if use_pilot:cfg.update(initial_adapter=str(PILOT),initial_adapter_sha256=sha(PILOT/'adapter_model.safetensors'))
        save(ROOT/'initialization-selection.json',{'variant':'pilot' if use_pilot else 'original','paired':initial_ci,
            'basis':'Pilot initialization only for supported CER reduction on5000 validation; otherwise original base conservatively. New optimizer/scheduler for this new manifest, not historical optimizer resume.'})
        cf=config('full',cfg,root=ROOT);smoke=ROOT/'smoke-resume'
        expected_smoke=__import__('hashlib').sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
        if (smoke/'smoke_passed.json').exists() and json.loads((smoke/'smoke_passed.json').read_text()).get('config_signature')!=expected_smoke:smoke=ROOT/('smoke-resume-'+expected_smoke[:12])
        if not (smoke/'smoke_passed.json').exists():
            milestone('Capped training smoke and exact resume',smoke,root=ROOT)
            command(['smoke','--config',str(cf),'--manifest',str(ROOT/'train.jsonl'),'--output',str(smoke)],smoke/'execution.log')
        smoke_peak=json.loads((smoke/'resumed/training_progress.json').read_text())['peak_allocated_vram_bytes']
        if smoke_peak>3.5*2**30:raise RuntimeError('Smoke peak exceeds conservative4GB GPU budget')
        full=ROOT/'full';verify();milestone('Capped25000-word training: epoch1',full,note='One initial epoch only. No additional epochs scheduled.',root=ROOT)
        if not (full/'training_complete.json').exists():
            command(['train','--config',str(cf),'--manifest',str(ROOT/'train.jsonl'),'--validation',str(ROOT/'validation.jsonl'),'--output',str(full),'--epochs','1'],full/'execution.log')
        best=json.loads((full/'best.json').read_text());validation=full/f"epoch-{best['epoch']}/validation"
        candidate=json.loads((validation/'metrics.json').read_text())
        ci_base=paired(load(original_path),load(validation/'predictions.jsonl'))
        ci_pilot=paired(load(pilot_path),load(validation/'predictions.jsonl'))
        save(ROOT/'candidate-validation-comparisons.json',{'original':ci_base,'pilot':ci_pilot})
        register('efficient-candidate-epoch1',candidate,ci_base,root=ROOT)
        baseline_variant='pilot' if use_pilot else 'original';baseline_metrics=pilot if use_pilot else original
        supported=(ci_pilot if use_pilot else ci_base)['cer_improvement_supported']
        selected_variant='candidate' if candidate['micro_cer']<baseline_metrics['micro_cer'] and supported else baseline_variant
        adapters={'original':None,'pilot':str(PILOT),'candidate':best['adapter']}
        selection={'variant':selected_variant,'adapter':adapters[selected_variant],'config':cfg,
            'basis':'Locked using validation only; candidate promotion requires supported CER reduction over chosen baseline. Final-test outcomes cannot change selection.',
            'candidate_improvement_supported':supported,'scope':'word crops only; no page/sentence benchmark'}
        selection_file=ROOT/'selection.json'
        if selection_file.exists():
            if json.loads(selection_file.read_text(encoding='utf-8'))!=selection:raise RuntimeError('Locked validation selection changed; do not inspect final outcomes or replace the lock')
        else:save(selection_file,selection)
        verify()
        results={};predictions={}
        for name in ['original','pilot','candidate']:
            out=ROOT/'final'/name;milestone('Sealed3000-word final evaluation: '+name,out,root=ROOT)
            if not (out/'metrics.json').exists():
                args=['evaluate','--config',str(cf),'--manifest',str(ROOT/'final-test.jsonl'),'--output',str(out)]
                if adapters[name]:args+=['--adapter',adapters[name]]
                command(args,out/'execution.log')
            results[name]=json.loads((out/'metrics.json').read_text());predictions[name]=load(out/'predictions.jsonl')
        verify()
        summary={'selection':selection,'counts':{n:v['count'] for n,v in protocol['manifests'].items()},'validation':{'original':original,'pilot':pilot,'candidate':candidate},
            'final_metrics':results,'final_paired_original_candidate':paired(predictions['original'],predictions['candidate']),
            'final_paired_pilot_candidate':paired(predictions['pilot'],predictions['candidate']),
            'limitations':['Source labels not all human verified','Unknown writer identity and possible pretraining overlap','Isolated words, not page or sentence recognition','No99% or market-leadership claim','One training seed/epoch; no additional epochs scheduled']}
        save(ROOT/'final-summary.json',summary)
        package=PROJECT.parent/'Telugu_OCR_Capped_Selected_Model.zip'
        with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
            if selection['adapter']:
                for p in Path(selection['adapter']).rglob('*'):
                    if p.is_file():z.write(p,'adapter/'+str(p.relative_to(selection['adapter'])))
            for p in [ROOT/'protocol.json',ROOT/'selection.json',cf,ROOT/'final-summary.json',ROOT/'resource-environment.json']:
                z.write(p,p.name)
            z.writestr('README.txt','Selected using validation only. Requires the exact original licensed IndicOCR checkpoint; original weights are not redistributed. Word crops only. Read final metrics and limitations. No further epochs scheduled.')
        save(ROOT/'status.json',{'status':'completed','stage':'Capped word study complete; selected-model API parity and user handoff remain','selection':selected_variant})
        with (PROJECT/'WORK_LOG.md').open('a',encoding='utf-8') as f:f.write('\n- Capped study completed with sealed3000 final evaluation. No further training scheduled; verify selected-model API and finish human-readable handoff.\n')
    except Exception as e:
        if isinstance(e,subprocess.CalledProcessError) and e.returncode==75:
            save(ROOT/'status.json',{'status':'paused_at_checkpoint','stage':'Safe runtime-budget/stop boundary; resume same run and configuration'});return
        save(ROOT/'failure.json',{'error':str(e),'traceback':traceback.format_exc()})
        save(ROOT/'status.json',{'status':'failed','stage':'Capped study needs attention','error':str(e)})
        raise
    finally:lock_context.__exit__(None,None,None)


if __name__=='__main__':main()
