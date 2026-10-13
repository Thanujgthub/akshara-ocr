"""Filesystem relocation only; frozen labels and training configuration stay unchanged."""
import json,os
from pathlib import Path
from contextlib import contextmanager


def resolve_path(value):
    text=str(value).replace('\\','/')
    mapping=json.loads(os.environ.get('OCR_PATH_MAP','{}'))
    for old,new in sorted(mapping.items(),key=lambda kv:-len(kv[0])):
        old=old.replace('\\','/').rstrip('/')
        if text.casefold()==old.casefold() or text.casefold().startswith(old.casefold()+'/'):
            return Path(new)/text[len(old):].lstrip('/')
    return Path(value)


@contextmanager
def run_lock(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as f:
        if f.tell()==0:f.write(b'0');f.flush()
        f.seek(0)
        try:
            if os.name=='nt':
                import msvcrt;msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl;fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as e:raise RuntimeError('Another process owns this run; do not launch a duplicate') from e
        try:yield
        finally:
            if os.name=='nt':
                import msvcrt;f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:
                import fcntl;fcntl.flock(f.fileno(),fcntl.LOCK_UN)
