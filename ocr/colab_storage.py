"""Private archive staging and versioned, verified runtime snapshots; no cloud API."""
import argparse,json,os,shutil,time,uuid,zipfile
from pathlib import Path,PurePosixPath
from .checkpoint_io import sha,recovery_folder,durable_copy_checkpoint
from .research_io import save


def safe_extract(archive,destination):
    destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            name=PurePosixPath(member.filename)
            target=(destination/member.filename).resolve()
            if '\\' in member.filename or name.is_absolute() or '..' in name.parts or ':' in member.filename or not target.is_relative_to(destination) or (member.external_attr>>16)&0o170000==0o120000:
                raise RuntimeError('Unsafe archive member: '+member.filename)
            if target.exists() and not member.is_dir():raise RuntimeError('Refusing to overwrite staged file: '+str(target))
        z.extractall(destination)


def stage_inputs(inbox,local):
    inbox=Path(inbox);local=Path(local);index=json.loads((inbox/'transfer-index.json').read_text())
    marker=local/'input-verification.json'
    if marker.exists():
        if json.loads(marker.read_text())['index_sha256']!=sha(inbox/'transfer-index.json'):raise RuntimeError('Different input bundle at existing local stage')
        verify_inputs(local);return
    if local.exists() and any(local.iterdir()):raise RuntimeError('Incomplete local stage: inspect it or select an empty staging directory; nothing was deleted')
    required=sum(a['uncompressed_bytes'] for a in index['archives'])
    if shutil.disk_usage(local.parent).free<required+12*2**30:raise RuntimeError('Insufficient local disk for inputs plus12GiB working reserve')
    for item in index['archives']:
        p=inbox/item['file']
        if sha(p)!=item['sha256']:raise RuntimeError('Archive transfer hash mismatch: '+p.name)
        safe_extract(p,local)
    verify_inputs(local)
    save(marker,{'index_sha256':sha(inbox/'transfer-index.json'),'verified_utc':time.time()})


def verify_inputs(local):
    local=Path(local);root=local/'inputs';protocol=json.loads((root/'protocol/protocol.json').read_text())
    from PIL import Image
    sets={};groups={};pixels={};documents={}
    for split,expected in protocol['manifests'].items():
        path=root/'protocol'/(split+'.jsonl')
        if sha(path)!=expected['sha256']:raise RuntimeError('Frozen manifest differs: '+split)
        rows=[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines()]
        if len(rows)!=expected['count']:raise RuntimeError('Frozen count differs')
        sets[split]=set();groups[split]=set();pixels[split]=set();documents[split]=set()
        for row in rows:
            p=(root/'data'/row['local_relative_path']).resolve()
            if not p.is_relative_to((root/'data').resolve()) or sha(p)!=row['original_sha256']:raise RuntimeError('Image path/hash mismatch')
            with Image.open(p) as im:im.verify()
            sets[split].add(row['original_sha256']);pixels[split].add(row['pixel_sha256']);groups[split].add(row['leakage_group']);documents[split].add(row['group_id'])
        if len(sets[split])!=len(rows) or len(pixels[split])!=len(rows):raise RuntimeError('Duplicate frozen image identity')
    names=list(sets)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if any(d[a]&d[b] for d in [sets,pixels,groups,documents]):raise RuntimeError('Cross-split leakage identity overlap')
    provenance=json.loads((local/'project/reports/model_provenance.json').read_text())
    for item in provenance['files']:
        if sha(root/'model'/item['file'])!=item['sha256']:raise RuntimeError('Original model/processor differs')
    pilot=json.loads((root/'pilot-checksums.json').read_text())
    for rel,h in pilot.items():
        if sha(root/'pilot'/rel)!=h:raise RuntimeError('Pilot adapter differs')
    return {k:v['count'] for k,v in protocol['manifests'].items()}


def snapshot_run(run,durable):
    """Append-only snapshots. Latest pointer commits only after all copied hashes pass."""
    run=Path(run);durable=Path(durable);durable.mkdir(parents=True,exist_ok=True)
    staging=durable/('.partial-'+uuid.uuid4().hex);staging.mkdir();hashes={}
    # Capture each recovery pointer after verification. Checkpoints are immutable.
    recovery={}
    for pointer in run.rglob('resume.json'):
        if 'checkpoints' in pointer.relative_to(run).parts:continue
        folder=recovery_folder(pointer.parent);record=json.loads(pointer.read_text())
        checkpoint_relative=record['checkpoint'].replace('\\','/')
        if (pointer.parent/checkpoint_relative).resolve()!=folder.resolve():raise RuntimeError('Checkpoint advanced while snapshotting; retry snapshot')
        record['checkpoint']=checkpoint_relative
        destination=staging/pointer.parent.relative_to(run)/checkpoint_relative
        durable_copy_checkpoint(folder,destination)
        recovery[pointer.relative_to(run).as_posix()]=json.dumps(record,ensure_ascii=False,indent=2).encode()
    for p in sorted(run.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(run);key=rel.as_posix()
        if key in {'snapshot-checksums.json','snapshot-metadata.json'}:continue
        if 'checkpoints' in rel.parts or p.name.endswith(('.tmp','.lock')) or any(part.startswith('.') for part in rel.parts):continue
        if p.name=='resume.json':data=recovery.get(key)
        else:
            try:data=p.read_bytes()
            except FileNotFoundError:continue
        if data is None:continue
        if p.suffix=='.jsonl' and data and not data.endswith(b'\n'):data=data[:data.rfind(b'\n')+1]
        if p.suffix=='.json':json.loads(data)  # Never commit partial JSON.
        target=staging/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    save(staging/'snapshot-metadata.json',{'created_ns':time.time_ns(),'source_run':str(run.resolve())})
    for p in staging.rglob('*'):
        if p.is_file():hashes[p.relative_to(staging).as_posix()]=sha(p)
    save(staging/'snapshot-checksums.json',hashes)
    verify_snapshot(staging)
    for best in staging.rglob('best.json'):
        record=json.loads(best.read_text());original=Path(record['adapter'])
        relative=original.relative_to(run.resolve())
        if not (staging/relative/'adapter_model.safetensors').is_file():raise RuntimeError('Epoch export advanced during snapshot; retry snapshot')
    final=durable/('snapshot-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:8])
    os.replace(staging,final);save(durable/'latest-snapshot.json',{'directory':final.name,'index_sha256':sha(final/'snapshot-checksums.json')})
    return final


def verify_snapshot(folder):
    folder=Path(folder)
    for rel,h in json.loads((folder/'snapshot-checksums.json').read_text()).items():
        p=(folder/rel).resolve()
        if not p.is_relative_to(folder.resolve()) or sha(p)!=h:raise RuntimeError('Snapshot corruption: '+rel)


def restore_run(durable,run):
    durable=Path(durable);run=Path(run)
    if run.exists() and any(run.iterdir()):raise RuntimeError('Restore requires an empty runtime run directory')
    def order(folder):
        try:return int(json.loads((folder/'snapshot-metadata.json').read_text())['created_ns'])
        except (OSError,ValueError,KeyError,TypeError):return folder.stat().st_mtime_ns
    candidates=sorted(durable.glob('snapshot-*'),key=order,reverse=True)
    pointer_index=None;pointed=None
    try:
        pointer=json.loads((durable/'latest-snapshot.json').read_text())
        pointed=(durable/pointer['directory']).resolve()
        if not pointed.is_relative_to(durable.resolve()) or pointed.parent!=durable.resolve():raise ValueError('Snapshot pointer escapes durable directory')
        pointer_index=pointer['index_sha256']
        if sha(pointed/'snapshot-checksums.json')==pointer_index:
            candidates=[pointed]+[p for p in candidates if p.resolve()!=pointed]
    except (OSError,ValueError,KeyError,TypeError):pointed=None
    for folder in candidates:
        try:verify_snapshot(folder)
        except (OSError,ValueError,RuntimeError):continue
        shutil.copytree(folder,run,dirs_exist_ok=True,ignore=shutil.ignore_patterns('snapshot-checksums.json','snapshot-metadata.json'))
        save(run/'restore-source.json',{'snapshot':folder.name,'index_sha256':sha(folder/'snapshot-checksums.json')})
        return folder
    raise RuntimeError('No intact durable snapshot; do not reset training silently')


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['stage','verify','snapshot','restore']);p.add_argument('source');p.add_argument('destination',nargs='?');a=p.parse_args()
    result={'stage':stage_inputs,'verify':verify_inputs,'snapshot':snapshot_run,'restore':restore_run}[a.mode](a.source,*([a.destination] if a.destination else []))
    print(result)

if __name__=='__main__':main()
