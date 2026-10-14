"""Versioned atomic checkpoints; compatible adapter/state.pt/resume.json layout."""
import hashlib,json,os,shutil,time,uuid
from pathlib import Path
from .research_io import save


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        # Hash unchanged bytes with bounded buffers even under Windows commit pressure.
        for b in iter(lambda:f.read(256*1024),b''):h.update(b)
    return h.hexdigest()


def file_hashes(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='checksums.json'}


def verify_checkpoint(folder,allow_legacy=False):
    folder=Path(folder);index=folder/'checksums.json'
    if not index.exists():
        if allow_legacy and (folder/'state.pt').is_file() and (folder/'adapter/adapter_model.safetensors').is_file():return {'legacy_without_checksums':True}
        raise RuntimeError('Checkpoint has no completed integrity index: '+str(folder))
    hashes=json.loads(index.read_text(encoding='utf-8'))
    if 'state.pt' not in hashes or 'adapter/adapter_model.safetensors' not in hashes:raise RuntimeError('Incomplete checkpoint index')
    for rel,expected in hashes.items():
        p=(folder/rel).resolve()
        if not p.is_relative_to(folder.resolve()) or not p.is_file() or sha(p)!=expected:raise RuntimeError('Checkpoint integrity failure: '+rel)
    return hashes


def save_checkpoint(out,updates,model,state,torch):
    out=Path(out);base=out/'checkpoints';base.mkdir(parents=True,exist_ok=True)
    tag=f'step-{updates:07d}';final=base/tag
    if final.exists():final=base/(tag+'-'+uuid.uuid4().hex[:12])
    staging=base/('.incomplete-'+uuid.uuid4().hex);staging.mkdir()
    started=time.perf_counter()
    model.save_pretrained(staging/'adapter')
    torch.save(state,staging/'state.pt')
    save(staging/'recovery.json',{k:state.get(k) for k in ['signature','updates','epoch','next_index','precision','dataset_fingerprint']})
    save(staging/'checksums.json',file_hashes(staging));verify_checkpoint(staging)
    os.replace(staging,final)
    pointer={'checkpoint':final.relative_to(out).as_posix(),'signature':state['signature'],'checkpoint_index_sha256':sha(final/'checksums.json')}
    save(out/'resume.json',pointer)
    save(final/'write-timing.json',{'checkpoint_write_seconds':time.perf_counter()-started})
    # Timing is outside the recovery index; it is not required to restore state.
    return final


def recovery_folder(out,expected_signature=None):
    out=Path(out);pointer_path=out/'resume.json'
    try:pointer=json.loads(pointer_path.read_text(encoding='utf-8'))
    except (OSError,ValueError):
        if expected_signature is None:raise RuntimeError('Missing/corrupt pointer: supply the expected training signature to recover safely')
        pointer={'signature':expected_signature,'checkpoint':'missing'}
    if expected_signature and pointer['signature']!=expected_signature:raise RuntimeError('Recovery configuration signature differs')
    folder=(out/pointer['checkpoint'].replace('\\','/')).resolve()
    if not folder.is_relative_to(out.resolve()):raise RuntimeError('Recovery pointer escapes run')
    valid=[];failure=None
    try:
        verify_checkpoint(folder,allow_legacy='checkpoint_index_sha256' not in pointer)
        if pointer.get('checkpoint_index_sha256') and sha(folder/'checksums.json')!=pointer['checkpoint_index_sha256']:raise RuntimeError('Recovery index differs from atomic pointer')
        if not (folder/'recovery.json').exists() or pointer.get('pin_checkpoint'):return folder
    except Exception as e:failure=str(e)
    for candidate in (out/'checkpoints').glob('step-*'):
        try:
            verify_checkpoint(candidate)
            metadata=json.loads((candidate/'recovery.json').read_text(encoding='utf-8'))
            if metadata['signature']==pointer['signature']:valid.append((metadata['updates'],candidate.stat().st_mtime,candidate))
        except (OSError,ValueError,RuntimeError):continue
    if not valid:raise RuntimeError('No verified recovery checkpoint remains: '+str(failure))
    chosen=max(valid,key=lambda item:item[:2])[2]
    if chosen.resolve()!=folder or failure:
        backup=out/('resume-before-recovery-'+uuid.uuid4().hex+'.json')
        if pointer_path.exists():shutil.copy2(pointer_path,backup)
        save(pointer_path,{'checkpoint':chosen.relative_to(out).as_posix(),'signature':pointer['signature'],'checkpoint_index_sha256':sha(chosen/'checksums.json')})
    return chosen


def durable_copy_checkpoint(source,destination):
    source=Path(source);destination=Path(destination);verify_checkpoint(source)
    if destination.exists():
        verify_checkpoint(destination)
        if sha(source/'checksums.json')!=sha(destination/'checksums.json'):raise RuntimeError('Refusing to replace a different durable checkpoint')
        return
    destination.parent.mkdir(parents=True,exist_ok=True)
    temp=destination.parent/('.partial-'+uuid.uuid4().hex)
    shutil.copytree(source,temp);verify_checkpoint(temp);os.replace(temp,destination)


def sync_recovery(out,durable):
    out=Path(out);durable=Path(durable);pointer=out/'resume.json'
    if not pointer.exists():return False
    folder=recovery_folder(out);before=pointer.read_bytes();record=json.loads(before)
    durable_copy_checkpoint(folder,durable/record['checkpoint'].replace('\\','/'))
    if pointer.read_bytes()!=before:return False  # Retry the newer pointer next time.
    save(durable/'resume.json',record);return True


def save_adapter_export(model,destination):
    """Commit an inference export once; never replace an earlier epoch adapter."""
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    staging=destination.parent/('.adapter-'+uuid.uuid4().hex)
    model.save_pretrained(staging);hashes=file_hashes(staging)
    save(staging/'checksums.json',hashes)
    if destination.exists():
        old=json.loads((destination/'checksums.json').read_text(encoding='utf-8'))
        if old!=hashes or any(sha(destination/k)!=v for k,v in old.items()):raise RuntimeError('Refusing to replace a different epoch adapter export')
        shutil.rmtree(staging);return destination
    os.replace(staging,destination);return destination
