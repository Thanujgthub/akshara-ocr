"""Short timing run using the unchanged full-manifest scheduler and training loop."""
import argparse,json,os,statistics,subprocess,threading,time
from pathlib import Path
from .scale_experiment import ScaleExperiment,read_manifest
from .research_io import save


class ProfileExperiment(ScaleExperiment):
    def __init__(self,*args,**kwargs):
        self.input_observations=[];self.image_seconds=0.
        super().__init__(*args,**kwargs)
    def image(self,row):
        start=time.perf_counter();result=super().image(row);self.image_seconds+=time.perf_counter()-start;return result
    def inputs(self,row,training=False):
        self.torch.cuda.synchronize();start=time.perf_counter();prior=self.image_seconds
        result=super().inputs(row,training);self.torch.cuda.synchronize()
        self.input_observations.append({'image_decode_preprocess_seconds':self.image_seconds-prior,'processor_and_transfer_seconds':time.perf_counter()-start-(self.image_seconds-prior)})
        return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--manifest',required=True);p.add_argument('--validation',required=True);p.add_argument('--output',required=True);p.add_argument('--updates',type=int,default=16);a=p.parse_args()
    out=Path(a.output)
    if out.exists() and any(out.iterdir()):raise RuntimeError('Benchmark requires a fresh output directory; never resume timings or promote benchmark weights')
    cfg=json.loads(Path(a.config).read_text());acc=cfg.get('accumulation',4)
    if a.updates<4:raise ValueError('Benchmark needs at least4 optimizer updates')
    os.environ['OCR_PROFILE_BATCHES']='1';os.environ.pop('OCR_RUNTIME_BUDGET_SECONDS',None);os.environ.pop('OCR_STOP_FILE',None)
    import torch,numpy as np
    torch.set_num_threads(4);np.random.seed(cfg['seed']);loaded=time.perf_counter();exp=ProfileExperiment(cfg);load_seconds=time.perf_counter()-loaded
    observations=[];stop=threading.Event()
    def sample():
        while not stop.is_set():
            r=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True)
            observations.append({'time':time.time(),'observation':r.stdout.strip(),'returncode':r.returncode});stop.wait(1)
    thread=threading.Thread(target=sample,daemon=True);thread.start()
    start=time.perf_counter()
    try:exp.train_scale(read_manifest(a.manifest),read_manifest(a.validation),out,1,stop_after_updates=a.updates)
    finally:stop.set();thread.join(timeout=3)
    total=time.perf_counter()-start
    rows=[json.loads(s) for s in (out/'training.jsonl').read_text().splitlines()] if (out/'training.jsonl').exists() else [json.loads(s) for s in (out/'training_log.jsonl').read_text().splitlines()]
    warmup=min(8,len(rows)//4);steady=rows[warmup:];seconds=[r['batch_seconds'] for r in steady]
    checkpoint_times=[json.loads(p.read_text())['checkpoint_write_seconds'] for p in out.glob('checkpoints/*/write-timing.json')]
    report={'examples':len(rows),'warmup_examples':warmup,'warmup_seconds':sum(r['batch_seconds'] for r in rows[:warmup]),'steady_examples_per_second':len(steady)/sum(seconds),'median_batch_seconds':statistics.median(seconds),'median_input_processing_transfer_seconds':statistics.median(r['input_processing_transfer_seconds'] for r in steady),'input_observations':exp.input_observations,'model_load_seconds':load_seconds,'wall_seconds_including_checkpoint':total,'checkpoint_write_seconds':checkpoint_times,'gpu_samples':observations,'peak_allocated_vram_bytes':torch.cuda.max_memory_allocated(),'losses':[r['loss'] for r in rows],'remaining_25000_word_training_hours_projection':25000/(len(steady)/sum(seconds))/3600,'projection_limitations':'Short64-example sample; excludes full validation, final testing, initialization, Drive sync and disconnects. Benchmark weights never selected or credited toward final training. Full25000-row scheduler retained. Synchronized timings add profiling overhead.','data_loader':'Direct sequential microbatch1 loop; DataLoader workers/pin_memory/persistent_workers not applicable.','precision':str(exp.dtype),'gpu':torch.cuda.get_device_name(0),'torch':torch.__version__,'cuda':torch.version.cuda,'config':cfg}
    save(out/'benchmark.json',report);print(json.dumps({k:v for k,v in report.items() if k not in {'input_observations','gpu_samples','losses'}},indent=2))

if __name__=='__main__':main()
