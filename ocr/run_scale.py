"""Sequential GPU experiments, validation selection, large training, sealed final testing.

Run once; resumes completed stages and optimizer checkpoints after interruption.
Never changes prior pilot files. No cloud charges, system settings, or alternative models.
"""
import argparse,json,subprocess,sys,time,traceback,zipfile,hashlib
from pathlib import Path
from ocr.scale_experiment import save,sha
from ocr.freeze_scale import main as freeze,ROOT,DATA,PILOT
from ocr.curate_scale import main as curate
from ocr.scale_analysis import load,paired

PROJECT=Path(__file__).resolve().parents[1]
def milestone(stage,directory=None,note='',root=ROOT):
    state={'status':'running','stage':stage,'updated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'note':note}
    if directory:state['experiment_directory']=str(directory)
    save(root/'status.json',state)
    with (PROJECT/'WORK_LOG.md').open('a',encoding='utf-8') as f:f.write(f"\n- {state['updated_utc']}: {stage}. {note}\n")
    text=(PROJECT/'PROJECT_STATE.md').read_text(encoding='utf-8')
    # Preserve migration and handoff notes written after earlier milestones.
    (PROJECT/'PROJECT_STATE.md').write_text(text+'\n## Latest automated milestone\n'+json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def command(args,log):
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('a',encoding='utf-8') as f:
        subprocess.run([sys.executable,'-u','-m','ocr.scale_experiment',*args],cwd=PROJECT,stdout=f,stderr=subprocess.STDOUT,check=True)
def config(name,cfg,root=ROOT):
    path=root/'configs'/f'{name}.json'
    if path.exists() and json.loads(path.read_text())!=cfg:raise RuntimeError('Refusing altered experiment config: '+name)
    save(path,cfg);return path
def evaluate(name,cfg,manifest,adapter=None,root=ROOT):
    out=root/'experiments'/name;cf=config(name,cfg,root=root)
    milestone('Validation: '+name,out,root=root)
    if not (out/'metrics.json').exists():
        args=['evaluate','--config',str(cf),'--manifest',str(manifest),'--output',str(out)]
        if adapter:args+=['--adapter',str(adapter)]
        command(args,out/'execution.log')
    return json.loads((out/'metrics.json').read_text())
def register(name,metrics,comparison=None,root=ROOT):
    p=root/'experiments.json';items=json.loads(p.read_text()) if p.exists() else []
    item={'name':name,'metrics':metrics,'comparison':comparison}
    items=[i for i in items if i['name']!=name]+[item];save(p,items)
def key(m):return (m['micro_cer'],-m['raw_exact_match'])
def snapshot():
    target=ROOT/'preserved-artifacts.json'
    if target.exists():
        for p,h in json.loads(target.read_text()).get('frozen_pilot',{}).items():
            if sha(p)!=h:raise RuntimeError('Immutable pilot changed: '+p)
        return
    provenance=json.loads((PROJECT/'reports/model_provenance.json').read_text())
    original={}
    for r in provenance['files']:
        p=Path('D:/OCR/models/indic-ocr')/r['file'];h=sha(p)
        if h!=r['sha256']:raise RuntimeError('Original snapshot hash mismatch: '+str(p))
        original[str(p)]=h
    frozen={str(p):sha(p) for p in PILOT.rglob('*') if p.is_file()}
    audit={str(p):sha(p) for p in Path('D:/OCR/research/manifests').glob('*.jsonl')}
    logs={str(p):sha(p) for p in PROJECT.parent.parent.joinpath('work').glob('*.log')}
    save(target,{'original_model':original,'frozen_pilot':frozen,'original_manifests':audit,'prior_log_hashes':logs,
                 'note':'Original files preserved; fingerprints are not human image/label verification.'})
def verify_frozen():
    p=json.loads((ROOT/'protocol.json').read_text())
    for s,h in p['pilot_manifest_hashes'].items():
        if sha(PILOT/f'{s}.jsonl')!=h:raise RuntimeError('Pilot manifest changed')
    for s,v in p['manifests'].items():
        if sha(ROOT/f'{s}.jsonl')!=v['sha256']:raise RuntimeError('Scale manifest changed: '+s)
    curation=json.loads((ROOT/'curation-protocol.json').read_text())
    for s,v in curation['manifests'].items():
        if sha(ROOT/f'{s}.jsonl')!=v['sha256']:raise RuntimeError('Curated manifest changed: '+s)

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    if (ROOT/'superseded-by-efficient-v3.json').exists():
        raise RuntimeError('Historical v2 pipeline retired by the capped plan. Use ocr.run_efficient; do not start the 80,083-example stage.')
    # Prevent accidentally running two pipelines. OS lock is released on crash.
    import msvcrt
    lock=(ROOT/'pipeline.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:raise RuntimeError('A scale pipeline is already running')
    if (ROOT/'final-summary.json').exists():print('Run already completed; no retraining performed.');return
    try:
        milestone('Snapshot and full word audit',note='Inspecting all supplied labeled word pairs; source labels are not newly human verified.')
        snapshot()
        deadline=time.time()+7200
        while not (DATA/'audit_summary.json').exists():
            if time.time()>deadline:raise RuntimeError('Full audit did not finish within two hours; inspect audit log')
            time.sleep(15)
        milestone('Freeze leakage-checked scale manifests');freeze();curate();verify_frozen()
        base={'seed':42,'prompt':'official','preprocessing':'official','rank':8,'targets':['q','v'],'lr':1e-5,'augmentation':False,'accumulation':4}
        # Forward/backward/save/resume smoke before any longer GPU study.
        smoke=ROOT/'smoke-resume-v2';smokecfg=config('smoke',base)
        if not (smoke/'smoke_passed.json').exists():
            milestone('GPU smoke and checkpoint resume',smoke)
            command(['smoke','--config',str(smokecfg),'--manifest',str(ROOT/'trial-train-curated.jsonl'),'--output',str(smoke)],smoke/'execution.log')
        peak=json.loads((smoke/'resumed/epoch-1/validation/metrics.json').read_text())['peak_allocated_vram_bytes']
        if peak>3.5*2**30:raise RuntimeError('Smoke exceeds memory budget; revise before expensive training')
        # Each pair differs by prompt OR preprocessing, never silently replacing the baseline.
        results=[]
        for variant,adapter in [('original',None),('pilot',PILOT/'trained/adapter')]:
            for prompt,prep in [('official','official'),('telugu_literal','official'),('telugu_literal','white_margin')]:
                cfg={**base,'prompt':prompt,'preprocessing':prep};name=f'curated-{variant}-{prompt}-{prep}'
                metrics=evaluate(name,cfg,ROOT/'trial-validation-curated.jsonl',adapter)
                register(name,metrics);results.append((metrics,cfg,variant,name))
        # Select input policy using original-model validation only, keeping model choice separate.
        policy=min([r for r in results if r[2]=='original'],key=lambda r:key(r[0]))[1]
        save(ROOT/'input-policy-selection.json',{'config':policy,'basis':'287 fixed eligible validation words on original model; exploratory, not independent test'})
        reference_name=next(r[3] for r in results if r[2]=='original' and r[1]==policy)
        reference_predictions=load(ROOT/'experiments'/reference_name/'predictions.jsonl')
        # Controlled single-variable trials against fixed clean-base configuration and identical data.
        trials=[('control',{}),('rank16',{'rank':16}),('qkvo',{'targets':['q','k','v','o']}),
                ('lr3e-5',{'lr':3e-5}),('mild-augmentation',{'augmentation':True})]
        trial_results=[]
        for name,delta in trials:
            cfg={**policy,**delta};out=ROOT/'trials'/name;cf=config('trial-'+name,cfg)
            milestone('Controlled training trial: '+name,out,note='1,000 training words; settings selected on validation only.')
            if not (out/'training_complete.json').exists():command(['train','--config',str(cf),'--manifest',str(ROOT/'trial-train-curated.jsonl'),'--validation',str(ROOT/'trial-validation-curated.jsonl'),'--output',str(out),'--epochs','1'],out/'execution.log')
            best=json.loads((out/'best.json').read_text());metrics=json.loads((out/f"epoch-{best['epoch']}/validation/metrics.json").read_text())
            ci=paired(reference_predictions,load(out/f"epoch-{best['epoch']}/validation/predictions.jsonl"))
            register('trial-'+name,metrics,ci);trial_results.append((metrics,cfg,name))
        winner=min(trial_results,key=lambda r:key(r[0]));fullcfg=winner[1];save(ROOT/'training-selection.json',{'config':fullcfg,'trial':winner[2],'basis':'NFC CER, then raw exact, on fixed 287-word eligible validation subset; small-study selection uncertainty remains'})
        # Full run starts from original checkpoint, not the overfit smoke or short trial adapter.
        full=ROOT/'full';cf=config('full',fullcfg)
        milestone('Full eligible word training',full,note='At most two epochs; validation after each; stop on non-improvement. No guaranteed 99% outcome.')
        verify_frozen()
        if not (full/'training_complete.json').exists():command(['train','--config',str(cf),'--manifest',str(ROOT/'train-curated.jsonl'),'--validation',str(ROOT/'validation-curated.jsonl'),'--output',str(full),'--epochs','2'],full/'execution.log')
        best=json.loads((full/'best.json').read_text())
        # Match original and pilot validation inputs/decoding to selected full-run policy.
        original_val=evaluate('full-validation-original',fullcfg,ROOT/'validation-curated.jsonl')
        pilot_val=evaluate('full-validation-pilot',fullcfg,ROOT/'validation-curated.jsonl',PILOT/'trained/adapter')
        full_val=json.loads((full/f"epoch-{best['epoch']}/validation/metrics.json").read_text())
        candidates=[(original_val,None,'original'),(pilot_val,str(PILOT/'trained/adapter'),'pilot'),(full_val,best['adapter'],'scale-v2')]
        selected=min(candidates,key=lambda r:key(r[0]))
        selection={'variant':selected[2],'adapter':selected[1],'config':fullcfg,'validation':selected[0],'basis':'Chosen exclusively on full frozen validation; final-test outcomes cannot change this choice.'}
        save(ROOT/'selection.json',selection);verify_frozen()
        milestone('Independent final testing',note='Model and policy locked. Original, pilot and selected model use identical sealed inputs and deterministic decoding.')
        finalmetrics={};finalpred={}
        for name,adapter in [('original',None),('pilot',PILOT/'trained/adapter'),('selected',selected[1])]:
            out=ROOT/'final'/name;milestone('Independent final test: '+name,out)
            if not (out/'metrics.json').exists():
                args=['evaluate','--config',str(cf),'--manifest',str(ROOT/'final-test.jsonl'),'--output',str(out)]
                if adapter:args+=['--adapter',str(adapter)]
                command(args,out/'execution.log')
            finalmetrics[name]=json.loads((out/'metrics.json').read_text());finalpred[name]=load(out/'predictions.jsonl')
        ci=paired(finalpred['original'],finalpred['selected']);verify_frozen()
        summary={'selected':selection,'final_metrics':finalmetrics,'paired_original_selected':ci,'scope':'isolated word crops only',
                 'limitations':['writer identity unknown','pretraining overlap unknown','human label verification incomplete','word corpus contains no true sentence context','page training terms unresolved','single corpus and laptop; no best-in-market evidence']}
        save(ROOT/'final-summary.json',summary)
        report=PROJECT.parent/'Telugu_OCR_Scale_Results.md'
        text='# Telugu OCR scale-up — completed measured study\n\nSelected on validation: '+selected[2]+'.\n\n'
        text+='| Final-test metric | Original | Pilot | Selected |\n|---|---:|---:|---:|\n'
        for field,label in [('micro_cer','NFC grapheme CER'),('raw_micro_cer','Raw grapheme CER'),('micro_wer','WER'),('raw_exact_match','Raw exact word match'),('script_contamination_rate','Script contamination'),('refusal_rate','Refusal rate'),('malformed_output_rate','Malformed output')]:
            text+='|'+label+'|'+'|'.join(f"{100*finalmetrics[n][field]:.2f}%" for n in ['original','pilot','selected'])+'|\n'
        text+=f"\nPaired 95% CER reduction interval: [{ci['cer_reduction_95'][0]*100:.2f}, {ci['cer_reduction_95'][1]*100:.2f}] percentage points. {ci['interpretation']}.\n\n"
        text+='\n'.join('- '+s for s in summary['limitations'])
        text+='\n\nNo 99% or market-leading claim is made. Raw predictions, manifests, configs, checkpoints and logs are retained in D:/OCR/runs/word-scale-v2.\n\nBuilt with IndicOCR from Bodhan AI / AI4Bharat. Word data: IIIT Hyderabad, Gongidi & Jawahar, IIIT-INDIC-HW-WORDS, ICDAR 2021, CC BY 4.0, https://ilocr.iiit.ac.in/dataset/23/.\n'
        report.write_text(text,encoding='utf-8')
        # Export a candidate artifact; never replace original or pilot adapter.
        if selected[1]:
            with zipfile.ZipFile(PROJECT.parent/'Telugu_OCR_Selected_Scale_Adapter.zip','w',zipfile.ZIP_DEFLATED) as z:
                for p in Path(selected[1]).glob('*'):
                    if p.is_file():z.write(p,'adapter/'+p.name)
                for p in [ROOT/'selection.json',ROOT/'protocol.json',ROOT/'final-summary.json',report,Path('D:/OCR/models/indic-ocr/Bodhan_AI_Open_Model_License.md')]:z.write(p,p.name)
        milestone('Completed: validation selection and independent final test',note=ci['interpretation'])
        save(ROOT/'status.json',{'status':'completed','stage':'Completed','selected_variant':selected[2],'report':str(report)})
    except Exception as error:
        save(ROOT/'failure.json',{'type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc()})
        save(ROOT/'status.json',{'status':'failed','stage':'Needs attention','error':str(error)})
        with (PROJECT/'WORK_LOG.md').open('a',encoding='utf-8') as f:f.write('\n- Scale pipeline failed: '+str(error)+'\n')
        raise
    finally:
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
if __name__=='__main__':main()
