"""Versioned, resumable experiments on the exact original IndicOCR checkpoint."""
import argparse,hashlib,json,math,os,random,time,sys,unicodedata
from pathlib import Path
from collections import defaultdict
from ocr.experiment import Experiment,read_manifest
from ocr.research_policy import TELUGU_PROMPT,quality,flags,augment,length_bin,crop_review_reasons,image_token_budget,uniform_visible_input
from ocr.metrics import corpus,compare
from ocr.research_io import save

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

class ScaleExperiment(Experiment):
    def adapter_digest(self):
        from peft import get_peft_model_state_dict
        h=hashlib.sha256()
        for name,value in sorted(get_peft_model_state_dict(self.model).items()):
            value=value.detach().cpu().contiguous()
            h.update(name.encode());h.update(str(value.dtype).encode());h.update(str(tuple(value.shape)).encode())
            h.update(value.view(self.torch.uint8).numpy().tobytes())
        return h.hexdigest()
    def __init__(self,cfg,adapter=None):
        import torch
        self.cfg=cfg;self.augmenting=False;self.aug_rng=random.Random(cfg['seed'])
        torch.manual_seed(cfg['seed']);random.seed(cfg['seed'])
        if torch.cuda.is_available():torch.cuda.manual_seed_all(cfg['seed'])
        super().__init__('D:/OCR/models/indic-ocr','D:/OCR/research-v2','cuda',adapter)
        if cfg.get('prompt')=='telugu_literal':self.prompt=TELUGU_PROMPT
        self.contract.update({'prompt':self.prompt,'research_config':cfg,'preprocessing':cfg.get('preprocessing','official'),
            'raw_output_policy':'exact decoded content preserved; no strip, spelling repair, numeral replacement or cleanup'})
    def image(self,row):
        from PIL import Image,ImageOps
        with Image.open(self.data_root/row['local_relative_path']) as im:image=ImageOps.exif_transpose(im).convert('RGB')
        if self.cfg.get('preprocessing')=='white_margin':image=ImageOps.expand(image,border=4,fill='white')
        if self.augmenting and self.cfg.get('augmentation'):
            candidate=augment(image,self.aug_rng)
            # Even a mild rotation can expand a very long word greatly. Keep the
            # unchanged source when augmentation would exceed the smoke-tested cap.
            if image_token_budget(candidate.width,candidate.height)<=800:image=candidate
        return self.area_clamp(image)
    def inputs(self,row,training=False):
        self.augmenting=training
        try:return super().inputs(row,training)
        finally:self.augmenting=False
    def add_lora(self):
        if self.adapter:raise RuntimeError('Use hashed initial_adapter configuration for follow-up training; --adapter is an inference initialization, not exact training resume')
        from peft import LoraConfig,get_peft_model
        suffixes=tuple('.self_attn.'+x+'_proj' for x in self.cfg.get('targets',['q','v']))
        names=[n for n,m in self.model.named_modules() if isinstance(m,self.torch.nn.Linear) and '.language_model.' in n and n.endswith(suffixes)]
        if not names:raise RuntimeError('No exact expected LoRA modules')
        rank=self.cfg.get('rank',8)
        self.model=get_peft_model(self.model,LoraConfig(r=rank,lora_alpha=rank*2,lora_dropout=.05,target_modules=names,bias='none',task_type='CAUSAL_LM'))
        initial=self.cfg.get('initial_adapter')
        if initial:
            initial=Path(initial);saved=json.loads((initial/'adapter_config.json').read_text(encoding='utf-8'))
            if saved['r']!=rank or saved['lora_alpha']!=rank*2 or set(saved['target_modules'])!=set(names):
                raise RuntimeError('Follow-up adapter contract differs from requested LoRA structure')
            expected=self.cfg.get('initial_adapter_sha256')
            if not expected or sha(initial/'adapter_model.safetensors')!=expected:raise RuntimeError('Initial adapter hash mismatch')
            from peft import set_peft_model_state_dict,get_peft_model_state_dict
            from safetensors.torch import load_file
            weights=load_file(str(initial/'adapter_model.safetensors'));expected_weights=get_peft_model_state_dict(self.model)
            if set(weights)!=set(expected_weights) or any(weights[k].shape!=expected_weights[k].shape for k in weights):
                raise RuntimeError('Initial adapter tensor names/shapes differ')
            loaded=set_peft_model_state_dict(self.model,weights)
            if loaded.unexpected_keys or any('lora_' in k for k in loaded.missing_keys):raise RuntimeError('Incomplete initial adapter tensors')
            self.contract['adapter_initialization']={'path':str(initial),'sha256':expected,'strategy':'Existing adapter tensor initialization; new optimizer/scheduler. Not exact historical optimizer resume.'}
        self.model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        self.model.enable_input_require_grads();self.model.config.use_cache=False
        self.contract.update({'lora_modules':names,'trainable_parameters':sum(p.numel() for p in self.model.parameters() if p.requires_grad)})
    def generate(self,row,max_tokens=64):
        torch=self.torch;self.model.eval()
        if uniform_visible_input(self.image(row)):
            return '',{'generated_tokens':0,'truncated':False,'latency_seconds':0.,'generated_token_ids':[],'abstention':'uniform_pixels'}
        try:inputs=self.inputs(row)
        except ValueError as e:
            return '',{'generated_tokens':0,'truncated':False,'latency_seconds':0.,'generated_token_ids':[],'abstention':'invalid_processor_input','abstention_detail':str(e)}
        if inputs['input_ids'].shape[-1]>1024:
            return '',{'generated_tokens':0,'truncated':False,'latency_seconds':0.,'generated_token_ids':[],'abstention':'resource_token_budget'}
        torch.cuda.synchronize();start=time.perf_counter()
        with torch.inference_mode():out=self.model.generate(**inputs,max_new_tokens=max_tokens,do_sample=False,num_beams=1,use_cache=True,eos_token_id=self.eos,pad_token_id=self.pad)
        torch.cuda.synchronize();tokens=out[:,inputs['input_ids'].shape[-1]:]
        raw=self.processor.batch_decode(tokens,skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
        return raw,{'generated_tokens':tokens.shape[-1],'truncated':tokens.shape[-1]>=max_tokens and int(tokens[0,-1])!=self.eos,
                    'latency_seconds':time.perf_counter()-start,'generated_token_ids':tokens[0].tolist()}
    def evaluate(self,rows,out,max_tokens=64):
        out=Path(out);out.mkdir(parents=True,exist_ok=True);predictions=[];self.torch.cuda.reset_peak_memory_stats();started=time.time()
        save(out/'contract.json',self.contract)
        # Resume completed prediction records only when this exact input/config contract matches.
        signature=hashlib.sha256(json.dumps({'ids':[r['example_id'] for r in rows],'config':self.cfg,'adapter':self.adapter,'max_tokens':max_tokens},sort_keys=True).encode()).hexdigest()
        if (out/'evaluation_contract.json').exists():
            if json.loads((out/'evaluation_contract.json').read_text())['signature']!=signature:raise RuntimeError('Evaluation resume contract mismatch')
            if (out/'predictions.jsonl').exists():
                rawlines=(out/'predictions.jsonl').read_text(encoding='utf-8').splitlines()
                for line in rawlines:
                    try:predictions.append(json.loads(line))
                    except ValueError:break
                if [r['example_id'] for r in predictions]!=[r['example_id'] for r in rows[:len(predictions)]]:raise RuntimeError('Evaluation ordering mismatch')
                (out/'predictions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in predictions),encoding='utf-8')
        else:save(out/'evaluation_contract.json',{'signature':signature})
        resumed_predictions=len(predictions)
        with (out/'predictions.jsonl').open('a',encoding='utf-8') as f:
            for i,row in enumerate(rows[len(predictions):],start=len(predictions)):
                raw,meta=self.generate(row,max_tokens);q=quality(self.image(row))
                record={'example_id':row['example_id'],'reference':row['transcription_raw'],'prediction':raw,
                    'source_dataset':row['source_dataset'],'granularity':'word','group_id':row['leakage_group'],
                    'source_document_id':row['group_id'],
                    'length_bin':length_bin(row['transcription_raw']),'image_quality':q,'label_status':row['label_status'],'crop_review_reasons':crop_review_reasons(row),
                    'reference_token_ids':self.processor.tokenizer.encode(row['transcription_raw'],add_special_tokens=False),
                    **meta,**flags(raw,meta['truncated'],q)}
                f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush();predictions.append(record)
                if (i+1)%20==0:save(out/'progress.json',{'evaluated':i+1,'total':len(rows),'elapsed_seconds':time.time()-started})
        report=corpus(predictions);report.pop('per_example',None)
        lat=sorted(r['latency_seconds'] for r in predictions)
        report.update({'elapsed_seconds_this_process':time.time()-started,'latency_median_seconds':lat[len(lat)//2],
            'latency_p95_seconds':lat[min(len(lat)-1,math.ceil(.95*len(lat))-1)],
            'peak_allocated_vram_bytes':self.torch.cuda.max_memory_allocated(),'peak_reserved_vram_bytes':self.torch.cuda.max_memory_reserved(),
            'truncated_count':sum(r['truncated'] for r in predictions),
            'script_contamination_rate':sum(r['script_contamination'] for r in predictions)/len(predictions),
            'refusal_rate':sum(r['refusal'] for r in predictions)/len(predictions),
            'malformed_output_rate':sum(r['malformed_output'] for r in predictions)/len(predictions)})
        report['abstention_rate']=sum(bool(r.get('abstention')) for r in predictions)/len(predictions)
        report['resource_abstention_rate']=sum(r.get('abstention')=='resource_token_budget' for r in predictions)/len(predictions)
        report['repetition_candidate_rate']=sum(bool(r.get('repeat_candidate')) for r in predictions)/len(predictions)
        report['resumed_predictions_count']=resumed_predictions
        report['generated_predictions_this_process']=len(predictions)-resumed_predictions
        report['peak_vram_scope']='entire_evaluation' if not resumed_predictions else 'remaining_examples_in_this_process_only'
        report['cost']={'provider':'local laptop','cloud_charges_incurred':0,'energy_cost_measured':False,'evaluation_wall_seconds_this_process':time.time()-started}
        groups=defaultdict(list)
        for r in predictions:
            for key in ['length:'+r['length_bin'],'source:'+r['source_dataset'],'document:'+r.get('source_document_id','unknown'),
                        'numerals:'+('present' if any(unicodedata.category(c)=='Nd' for c in r['reference']) else 'absent'),
                        'quality:'+('low_contrast' if r['image_quality']['low_contrast'] else 'other'),
                        'script:'+('mixed' if flags(r['reference'])['script_contamination'] else 'Telugu'),
                        'crop_quality:'+('review' if r['crop_review_reasons'] else 'eligible'),
                        *['error:'+x for x in r['uncertainty_flags']]]:groups[key].append(r)
        report['subgroups']={k:{kk:vv for kk,vv in corpus(v).items() if kk in ['examples','micro_cer','micro_wer','raw_exact_match']} for k,v in groups.items()}
        save(out/'metrics.json',report)
        # All selection experiments can be compared with the fixed official-prompt
        # baseline on these same validation IDs. Trials also get matched-policy CIs
        # in run_scale; these intervals never inspect the sealed final test.
        reference=Path('D:/OCR/runs/word-scale-v2/experiments/curated-original-official-official/predictions.jsonl')
        if reference.exists() and 'final' not in out.parts:
            from ocr.scale_analysis import load,paired
            baseline=load(reference)
            if [r['example_id'] for r in baseline]==[r['example_id'] for r in predictions]:
                save(out/'paired_official_baseline.json',paired(baseline,predictions))
        queue=sorted([{**r,**compare(r['reference'],r['prediction'])} for r in predictions if r['reference']!=r['prediction']],key=lambda r:r['grapheme_edits'],reverse=True)
        (out/'error-queue.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in queue),encoding='utf-8')
        return report
    def train_scale(self,rows,validation,out,epochs,stop_after_updates=None):
        cap=self.cfg.get('maximum_training_examples',25000)
        if not 0<cap<=25000 or not 0<len(rows)<=cap:raise ValueError('Training examples exceed the active25000 cap or are empty')
        if not 0<epochs<=self.cfg.get('maximum_epochs',1):raise ValueError('Validate the initial epoch before scheduling additional training')
        if self.cfg.get('microbatch_size',1)!=1:raise ValueError('Verified microbatch size is1')
        out=Path(out);out.mkdir(parents=True,exist_ok=True);torch=self.torch
        signature=hashlib.sha256(json.dumps({'cfg':self.cfg,'ids':[r['example_id'] for r in rows],'validation':[r['example_id'] for r in validation],'epochs':epochs},sort_keys=True).encode()).hexdigest()
        self.add_lora();save(out/'contract.json',self.contract)
        initialization_file=out/'adapter-initialization.json'
        if not initialization_file.exists():save(initialization_file,{'tensor_digest':self.adapter_digest(),'strategy':self.contract.get('adapter_initialization','new LoRA from original base')})
        params=[p for p in self.model.parameters() if p.requires_grad]
        optimizer=torch.optim.AdamW(params,lr=self.cfg['lr']);acc=self.cfg.get('accumulation',4)
        steps_per_epoch=math.ceil(len(rows)/acc);total_steps=steps_per_epoch*epochs;warmup=max(1,round(total_steps*.05))
        scheduler=torch.optim.lr_scheduler.LambdaLR(optimizer,lambda step:(step+1)/warmup if step<warmup else max(0.,(total_steps-step)/max(1,total_steps-warmup)))
        start_epoch=start_index=updates=0;elapsed_prior=0.;best=None;start=time.time();torch.cuda.reset_peak_memory_stats()
        if (out/'resume.json').exists():
            resume=json.loads((out/'resume.json').read_text());folder=out/resume['checkpoint']
            state=torch.load(folder/'state.pt',map_location='cpu',weights_only=False)
            if state['signature']!=signature:raise RuntimeError('Training resume manifest/config mismatch')
            from peft import set_peft_model_state_dict
            from safetensors.torch import load_file
            set_peft_model_state_dict(self.model,load_file(str(folder/'adapter/adapter_model.safetensors')))
            optimizer.load_state_dict(state['optimizer']);scheduler.load_state_dict(state['scheduler'])
            torch.set_rng_state(state['torch_rng']);torch.cuda.set_rng_state_all(state['cuda_rng']);random.setstate(state['python_rng']);self.aug_rng.setstate(state['augment_rng'])
            start_epoch=state['epoch'];start_index=state['next_index'];updates=state['updates'];elapsed_prior=state['elapsed'];best=state['best']
        def checkpoint(epoch,next_index):
            folder=out/f'checkpoints/step-{updates:07d}'
            folder.mkdir(parents=True,exist_ok=True);self.model.save_pretrained(folder/'adapter')
            state={'signature':signature,'optimizer':optimizer.state_dict(),'scheduler':scheduler.state_dict(),
                'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),'python_rng':random.getstate(),'augment_rng':self.aug_rng.getstate(),
                'epoch':epoch,'next_index':next_index,'updates':updates,'elapsed':elapsed_prior+time.time()-start,'best':best}
            torch.save(state,folder/'state.tmp');os.replace(folder/'state.tmp',folder/'state.pt')
            save(out/'resume.json',{'checkpoint':str(folder.relative_to(out)),'signature':signature})
        with (out/'training.jsonl').open('a',encoding='utf-8') as log:
            for epoch in range(start_epoch,epochs):
                shuffled=list(rows);random.Random(self.cfg['seed']+epoch).shuffle(shuffled)
                begin=start_index if epoch==start_epoch else 0
                if begin%acc and begin!=len(shuffled):raise RuntimeError('Resume is not at an optimizer boundary')
                optimizer.zero_grad(set_to_none=True)
                for i in range(begin,len(shuffled)):
                    self.model.train();loss=self.training_loss(self.inputs(shuffled[i],True))
                    if not torch.isfinite(loss):raise RuntimeError('Nonfinite loss')
                    window_size=min(acc,len(shuffled)-(i//acc)*acc)
                    (loss/window_size).backward()
                    boundary=(i+1)%acc==0 or i+1==len(shuffled)
                    if boundary:
                        norm=torch.nn.utils.clip_grad_norm_(params,1.)
                        if not torch.isfinite(norm):raise RuntimeError('Nonfinite gradient')
                        optimizer.step();scheduler.step();optimizer.zero_grad(set_to_none=True);updates+=1
                    record={'epoch':epoch+1,'example':i+1,'examples_per_epoch':len(shuffled),'optimizer_updates':updates,'loss':float(loss.detach()),
                            'lr':scheduler.get_last_lr()[0],'elapsed_seconds':elapsed_prior+time.time()-start,'peak_allocated_vram_bytes':torch.cuda.max_memory_allocated()}
                    log.write(json.dumps(record)+'\n');log.flush()
                    if (i+1)%20==0 or i+1==len(shuffled):save(out/'training_progress.json',record)
                    if boundary and updates%125==0:checkpoint(epoch,i+1)
                    if boundary and stop_after_updates and updates>=stop_after_updates:
                        checkpoint(epoch,i+1);return
                self.model.save_pretrained(out/f'epoch-{epoch+1}/adapter');self.processor.save_pretrained(out/'processor')
                result=self.evaluate(validation,out/f'epoch-{epoch+1}/validation')
                previous=best
                if best is None or (result['micro_cer'],-result['raw_exact_match'])<(best['cer'],-best['exact']):
                    best={'epoch':epoch+1,'cer':result['micro_cer'],'exact':result['raw_exact_match'],'adapter':str(out/f'epoch-{epoch+1}/adapter')}
                    save(out/'best.json',best)
                checkpoint(epoch+1,0)
                if previous and best==previous:break
        progress=json.loads((out/'training_progress.json').read_text()) if (out/'training_progress.json').exists() else {}
        changed=self.adapter_digest()!=json.loads(initialization_file.read_text(encoding='utf-8'))['tensor_digest']
        if not changed:raise RuntimeError('Adapter tensors did not change from initialization')
        save(out/'training_complete.json',{'config':self.cfg,'best':best,'elapsed_seconds':elapsed_prior+time.time()-start,'optimizer_updates':updates,'manifest_examples':len(rows),'signature':signature,'adapter_weights_changed_from_initial':changed,'peak_training_allocated_vram_bytes':progress.get('peak_allocated_vram_bytes'),'cloud_charges_incurred':0,'energy_cost_measured':False})

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['evaluate','train','smoke']);p.add_argument('--config',required=True);p.add_argument('--manifest',required=True);p.add_argument('--validation');p.add_argument('--output',required=True);p.add_argument('--adapter');p.add_argument('--epochs',type=int,default=1);p.add_argument('--limit',type=int,default=0);a=p.parse_args()
    out=Path(a.output)
    try:
        import torch,transformers,peft,regex,PIL
        torch.set_num_threads(4);cfg=json.loads(Path(a.config).read_text());started=time.time()
        exp=ScaleExperiment(cfg,a.adapter)
        save(out/'environment.json',{'python':sys.version,'torch':torch.__version__,'transformers':transformers.__version__,'peft':peft.__version__,'regex':regex.__version__,'pillow':PIL.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'argv':sys.argv,'load_seconds':time.time()-started})
        rows=read_manifest(a.manifest,a.limit)
        if a.mode=='evaluate':exp.evaluate(rows,out)
        elif a.mode=='smoke':
            exp.train_scale(rows[:8],rows[:2],out/'resumed',1,stop_after_updates=1)
            if exp.adapter_digest()==json.loads((out/'resumed/adapter-initialization.json').read_text())['tensor_digest']:raise RuntimeError('Smoke optimizer update did not change adapter tensors')
            del exp;import gc;gc.collect();torch.cuda.empty_cache()
            exp=ScaleExperiment(cfg);exp.train_scale(rows[:8],rows[:2],out/'resumed',1)
            del exp;gc.collect();torch.cuda.empty_cache()
            exp=ScaleExperiment(cfg);exp.train_scale(rows[:8],rows[:2],out/'uninterrupted',1)
            from safetensors.torch import load_file
            x=load_file(str(out/'resumed/epoch-1/adapter/adapter_model.safetensors'));y=load_file(str(out/'uninterrupted/epoch-1/adapter/adapter_model.safetensors'))
            identical=all(torch.equal(x[k],y[k]) for k in x)
            if not identical:raise RuntimeError('Mid-epoch resume differs from uninterrupted adapter weights')
            expected=[r['prediction'] for r in [json.loads(s) for s in (out/'resumed/epoch-1/validation/predictions.jsonl').read_text(encoding='utf-8').splitlines()]]
            del exp;gc.collect();torch.cuda.empty_cache()
            exp=ScaleExperiment(cfg,str(out/'resumed/epoch-1/adapter'))
            reloaded=[exp.generate(row)[0] for row in rows[:2]]
            if reloaded!=expected:raise RuntimeError('Final adapter reload inference differs from saved smoke predictions')
            save(out/'smoke_passed.json',{'forward_backward':True,'finite_loss_and_gradients':True,'adapter_weights_changed':True,'final_adapter_reload_inference_matches':True,'mid_epoch_resume_exact_adapter_weights':True,'optimizer_rng_scheduler_resume':True})
        else:exp.train_scale(rows,read_manifest(a.validation),out,a.epochs)
    except Exception as e:
        import traceback
        save(out/'failure.json',{'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()});raise
if __name__=='__main__':main()
