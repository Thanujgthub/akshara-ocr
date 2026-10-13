"""Run the existing capped coordinator with periodic verified Drive snapshots."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
from .colab_storage import snapshot_run
from .research_io import save
from .portable_paths import run_lock


def main():
    p=argparse.ArgumentParser();p.add_argument('--durable',required=True);p.add_argument('--seconds',type=int,default=10800);p.add_argument('--sync-seconds',type=int,default=300);a=p.parse_args()
    run=Path(os.environ['OCR_RUN_ROOT']);run.mkdir(parents=True,exist_ok=True);durable=Path(a.durable)
    if a.seconds<60 or a.sync_seconds<30:raise ValueError('Use a sensible safe-stop budget and sync interval')
    stop=run/'STOP';os.environ['OCR_STOP_FILE']=str(stop)
    if stop.exists():raise RuntimeError('Previous safe-stop sentinel remains; verify snapshot and remove STOP explicitly before resuming')
    started=time.monotonic();next_sync=started+a.sync_seconds
    # Local OS lock supplements the private Drive single-owner lease/manual check.
    with run_lock(run/'colab-runner.lock'):
        with (run/'colab-pipeline.log').open('a',encoding='utf-8') as log:
            child=subprocess.Popen([sys.executable,'-u','-m','ocr.run_efficient'],stdout=log,stderr=subprocess.STDOUT)
            try:
                while child.poll() is None:
                    now=time.monotonic()
                    if now-started>=a.seconds and not stop.exists():stop.write_text('Safe stop requested by runtime budget.\n')
                    if now>=next_sync:
                        try:
                            latest=snapshot_run(run,durable);save(run/'drive-sync-status.json',{'snapshot':latest.name,'verified':True,'time':time.time()})
                        except Exception as e:
                            save(run/'drive-sync-status.json',{'verified':False,'error':str(e),'time':time.time()})
                        next_sync=time.monotonic()+a.sync_seconds
                    print(json.loads((run/'status.json').read_text()) if (run/'status.json').exists() else {'status':'starting'},flush=True)
                    time.sleep(15)
            except KeyboardInterrupt:
                stop.write_text('User requested safe stop.\n');print('Waiting for an optimizer/prediction boundary and snapshot; keep this runtime open.',flush=True)
                child.wait()  # Does not terminate the active GPU job.
        latest=snapshot_run(run,durable)
        print('Verified durable snapshot:',latest,'pipeline exit:',child.returncode,flush=True)
        if child.returncode:raise SystemExit(child.returncode)

if __name__=='__main__':main()
