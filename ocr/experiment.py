"""Actual IndicBlockOCR LoRA experiment. Requires local authorized original weights.

Uses the shipped processor/chat template, TEXT_PROMPT and crop-area clamp.
Word adaptation is reported as word adaptation, never as measured page quality.
"""
import argparse, hashlib, json, os, random, sys, time
from pathlib import Path

def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def read_manifest(path,limit=0):
    rows=[json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]
    random.Random(42).shuffle(rows)
    return rows[:limit] if limit else rows

class Experiment:
    def __init__(self,repo,data_root,device='cuda',adapter=None):
        import torch
        from transformers import AutoModelForImageTextToText,AutoProcessor
        self.torch=torch;self.repo=Path(repo);self.data_root=Path(data_root)
        sys.path.insert(0,str(self.repo))
        from idp_contract import TEXT_PROMPT
        from idp_crops import area_clamp
        self.prompt=TEXT_PROMPT;self.area_clamp=area_clamp
        ckpt=str(self.repo/'weights/ocr')
        if not (Path(ckpt)/'model-00001-of-00001.safetensors').is_file():
            raise FileNotFoundError('Actual IndicOCR recognizer weight file is missing; no substitute model will be loaded')
        self.processor=AutoProcessor.from_pretrained(ckpt,local_files_only=True)
        self.processor.tokenizer.padding_side='left'
        precision=os.environ.get('OCR_PRECISION')
        if precision not in {None,'bf16','fp32'}:raise ValueError('Only existing BF16 or explicit FP32 precision is supported; FP16/GradScaler is not silently enabled')
        if precision=='bf16' and device!='cpu' and not torch.cuda.is_bf16_supported():raise RuntimeError('This GPU cannot run the frozen BF16 precision contract')
        self.dtype=(torch.bfloat16 if precision=='bf16' else torch.float32) if precision else (torch.bfloat16 if device=='cpu' or torch.cuda.is_bf16_supported() else torch.float32)
        from ocr.stream_load import load_model
        self.model=load_model(ckpt,device,self.dtype)
        self.model.eval();self.adapter=adapter
        if adapter:
            from peft import PeftModel
            self.model=PeftModel.from_pretrained(self.model,adapter)
        self.eos=self.processor.tokenizer.eos_token_id;self.pad=self.processor.tokenizer.pad_token_id
        self.contract={'model_class':type(self.model).__name__,'processor_class':type(self.processor).__name__,
            'tokenizer_class':type(self.processor.tokenizer).__name__,'eos_token_id':self.eos,'pad_token_id':self.pad,
            'prompt':self.prompt,'dtype':str(self.dtype),'attention':'sdpa','model_id':'bodhan-ai/indic-ocr',
            'revision':'cd50d301d0e17e8ecb32fc49c8ccbd7914dcfc25','granularity':'word',
            'crop_preprocessing':'official area_clamp defaults; same processor for training and inference'}

    def image(self,row):
        from PIL import Image,ImageOps
        with Image.open(self.data_root/row['local_relative_path']) as im:
            return self.area_clamp(ImageOps.exif_transpose(im).convert('RGB'))

    def prompt_text(self):
        return self.processor.apply_chat_template([{'role':'user','content':[{'type':'image'},{'type':'text','text':self.prompt}]}],add_generation_prompt=True,tokenize=False)

    def inputs(self,row,training=False):
        image=self.image(row);text=self.prompt_text()
        prefix=self.processor(text=[text],images=[image],padding=True,return_tensors='pt')
        if not training:return prefix.to(self.model.device)
        # Retain only the token boundary, releasing the duplicate CPU image tensors
        # before processing the supervised sequence with the same shipped processor.
        prefix_ids=prefix['input_ids']
        n=prefix_ids.shape[-1]
        del prefix
        # Match the exact inference prefix and append verbatim assistant content plus real EOS.
        target=row['transcription_raw']+self.processor.tokenizer.eos_token
        full=self.processor(text=[text+target],images=[image],padding=True,return_tensors='pt')
        if not self.torch.equal(prefix_ids,full['input_ids'][:,:n]):
            raise RuntimeError('Prompt token boundary differs between inference and training')
        labels=full['input_ids'].clone();labels[:,:n]=-100;labels[full['attention_mask']==0]=-100
        special_ids=[self.model.config.image_token_id,self.model.config.video_token_id]
        for token in special_ids:labels[full['input_ids']==token]=-100
        if not (labels!=-100).any():raise RuntimeError('No target labels remain')
        if full['input_ids'].shape[-1]>1024:raise ValueError('Word sample exceeds verified 1024-token cap')
        full['labels']=labels
        return full.to(self.model.device)

    def generate(self,row,max_tokens=64):
        torch=self.torch;self.model.eval();inputs=self.inputs(row)
        with torch.inference_mode():
            result=self.model.generate(**inputs,max_new_tokens=max_tokens,do_sample=False,use_cache=True,eos_token_id=self.eos,pad_token_id=self.pad)
        tokens=result[:,inputs['input_ids'].shape[-1]:]
        raw=self.processor.batch_decode(tokens,skip_special_tokens=True)[0]
        return raw.strip(),{'generated_tokens':tokens.shape[-1],'truncated':tokens.shape[-1]>=max_tokens and int(tokens[0,-1])!=self.eos}

    def add_lora(self):
        from peft import LoraConfig,get_peft_model
        torch=self.torch
        # Discover actual full-attention projections; leave vision, embeddings and output head immutable.
        names=[name for name,module in self.model.named_modules() if isinstance(module,torch.nn.Linear) and '.language_model.' in name and name.endswith(('.self_attn.q_proj','.self_attn.v_proj'))]
        if not names:raise RuntimeError('Expected recognizer attention Linear modules were not found')
        self.model=get_peft_model(self.model,LoraConfig(r=8,lora_alpha=16,lora_dropout=0.05,target_modules=names,bias='none',task_type='CAUSAL_LM'))
        self.model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        self.model.enable_input_require_grads();self.model.config.use_cache=False
        self.contract['lora_modules']=names
        self.contract['trainable_parameters']=sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        self.contract['total_parameters']=sum(p.numel() for p in self.model.parameters())

    def training_loss(self,batch):
        # Causal cross-entropy only needs positions immediately before target tokens.
        # Avoid allocating a 262k-vocabulary logit vector for every image/prompt token.
        labels=batch.pop('labels')
        positions=(labels[0]!=-100).nonzero(as_tuple=True)[0]
        outputs=self.model(**batch,use_cache=False,logits_to_keep=positions-1)
        return self.torch.nn.functional.cross_entropy(outputs.logits[0].float(),labels[0,positions])

    def probe(self,rows,out,steps=16):
        torch=self.torch;out=Path(out);out.mkdir(parents=True,exist_ok=True)
        baseline,_=self.generate(rows[0]);save(out/'baseline_example.json',{'prediction':baseline,'reference':rows[0]['transcription_raw'],'example_id':rows[0]['example_id']});self.add_lora();save(out/'contract.json',self.contract)
        optimizer=torch.optim.AdamW((p for p in self.model.parameters() if p.requires_grad),lr=1e-4)
        before={n:p.detach().cpu().clone() for n,p in self.model.named_parameters() if p.requires_grad}
        losses=[];gradients=[];start=time.time()
        for step in range(steps):
            self.model.train();optimizer.zero_grad(set_to_none=True)
            batch=self.inputs(rows[step%min(4,len(rows))],True)
            loss=self.training_loss(batch)
            if not torch.isfinite(loss):raise RuntimeError('Nonfinite loss')
            loss.backward();norm=torch.nn.utils.clip_grad_norm_([p for p in self.model.parameters() if p.requires_grad],1.0)
            if not torch.isfinite(norm):raise RuntimeError('Nonfinite gradient norm')
            optimizer.step();losses.append(float(loss.detach()));gradients.append(float(norm))
            print(json.dumps({'probe_step':step+1,'loss':losses[-1],'grad_norm':gradients[-1]}),flush=True)
        changed=any(not torch.equal(before[n],p.detach().cpu()) for n,p in self.model.named_parameters() if p.requires_grad)
        if not changed:raise RuntimeError('No adapter weight changed')
        self.model.save_pretrained(out/'adapter');prediction,_=self.generate(rows[0])
        self.model.load_adapter(out/'adapter',adapter_name='reload_check',is_trainable=False)
        self.model.set_adapter('reload_check')
        reloaded,_=self.generate(rows[0])
        if reloaded!=prediction:raise RuntimeError('Saved adapter generation differs after reload')
        # Save optimizer state for the smoke run separately; never treat smoke weights as final training.
        torch.save(optimizer.state_dict(),out/'optimizer.pt')
        report={'status':'forward_backward_update_passed','losses':losses,'gradient_norms':gradients,'adapter_weights_changed':changed,
            'baseline_prediction':baseline,'after_probe_prediction':prediction,'example_id':rows[0]['example_id'],
            'elapsed_seconds':time.time()-start,'peak_vram_bytes':torch.cuda.max_memory_allocated() if torch.cuda.is_available() else None,
            'tiny_overfit_proven':prediction==rows[0]['transcription_raw'],'save_reload_verified':True}
        save(out/'probe.json',report)
        return report

    def evaluate(self,rows,out,max_tokens=64):
        from ocr.metrics import corpus
        out=Path(out);out.mkdir(parents=True,exist_ok=True);predictions=[];start=time.time()
        with (out/'predictions.jsonl').open('w',encoding='utf-8') as f:
            for i,row in enumerate(rows):
                began=time.time();text,meta=self.generate(row,max_tokens)
                record={'example_id':row['example_id'],'reference':row['transcription_raw'],'prediction':text,
                    'source_dataset':row['source_dataset'],'granularity':row['granularity'],'latency_seconds':time.time()-began,**meta}
                f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush();predictions.append(record)
                if i%10==0:print(json.dumps({'evaluated':i+1,'total':len(rows),'elapsed_seconds':time.time()-start}),flush=True)
        report=corpus(predictions);report['elapsed_seconds']=time.time()-start
        report['truncated_count']=sum(r['truncated'] for r in predictions);report['contract']=self.contract
        save(out/'metrics.json',report);return report

    def train(self,rows,validation,out,epochs=1,lr=1e-5):
        torch=self.torch;out=Path(out);out.mkdir(parents=True,exist_ok=True);self.add_lora()
        save(out/'contract.json',self.contract)
        optimizer=torch.optim.AdamW((p for p in self.model.parameters() if p.requires_grad),lr=lr)
        torch.manual_seed(42);random.seed(42);accumulation=4;log=[];start=time.time()
        for epoch in range(epochs):
            shuffled=list(rows);random.Random(42+epoch).shuffle(shuffled);optimizer.zero_grad(set_to_none=True)
            for i,row in enumerate(shuffled):
                self.model.train();batch=self.inputs(row,True);loss=self.training_loss(batch)
                if not torch.isfinite(loss):raise RuntimeError('Nonfinite training loss')
                (loss/accumulation).backward()
                if (i+1)%accumulation==0 or i+1==len(shuffled):
                    norm=torch.nn.utils.clip_grad_norm_([p for p in self.model.parameters() if p.requires_grad],1.0)
                    if not torch.isfinite(norm):raise RuntimeError('Nonfinite training gradients')
                    optimizer.step();optimizer.zero_grad(set_to_none=True)
                record={'epoch':epoch+1,'example':i+1,'loss':float(loss.detach()),'elapsed_seconds':time.time()-start};log.append(record)
                if i%10==0:print(json.dumps(record),flush=True);save(out/'training_progress.json',record)
                if (i+1)%100==0:self.model.save_pretrained(out/'latest');torch.save({'optimizer':optimizer.state_dict(),'epoch':epoch,'example':i+1},out/'optimizer.pt')
            self.model.save_pretrained(out/f'epoch-{epoch+1}')
        self.model.save_pretrained(out/'adapter');self.processor.save_pretrained(out/'processor')
        save(out/'training.json',{'examples':len(rows),'epochs':epochs,'learning_rate':lr,'gradient_accumulation':accumulation,'seed':42,'elapsed_seconds':time.time()-start,'losses':log,'contract':self.contract})
        if validation:self.evaluate(validation,out/'validation')

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['probe','evaluate','train']);p.add_argument('--repo',default='D:/OCR/models/indic-ocr');p.add_argument('--data-root',default='D:/OCR/research');p.add_argument('--manifest',required=True);p.add_argument('--validation');p.add_argument('--output',required=True);p.add_argument('--adapter');p.add_argument('--limit',type=int,default=0);p.add_argument('--steps',type=int,default=16);p.add_argument('--epochs',type=int,default=1);p.add_argument('--device',default='cuda');a=p.parse_args()
    try:
        import torch,transformers,peft
        torch.set_num_threads(4);torch.manual_seed(42)
        save(Path(a.output)/'environment.json',{'torch':torch.__version__,'transformers':transformers.__version__,'peft':peft.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,'argv':sys.argv})
        exp=Experiment(a.repo,a.data_root,a.device,a.adapter);rows=read_manifest(a.manifest,a.limit)
        if not rows:raise ValueError('Empty manifest')
        if a.mode=='probe':exp.probe(rows,a.output,a.steps)
        elif a.mode=='evaluate':exp.evaluate(rows,a.output)
        else:exp.train(rows,read_manifest(a.validation,500) if a.validation else [],a.output,a.epochs)
    except Exception as error:
        import traceback
        save(Path(a.output)/'failure.json',{'error':str(error),'type':type(error).__name__,'traceback':traceback.format_exc()})
        raise
if __name__=='__main__':main()



