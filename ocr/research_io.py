"""Small atomic JSON writer independent of model and experiment imports."""
import json
import os
import time
import uuid
from pathlib import Path


def _transient_windows_lock(error):
    return os.name == 'nt' and getattr(error, 'winerror', None) in {5, 32, 33}


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    with tmp.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2))
        stream.flush()
        os.fsync(stream.fileno())
    # Windows readers/scanners can briefly deny replacement. Keep the existing
    # destination intact, retry only sharing/access errors, and retain the staged
    # bytes for diagnosis if the bounded retry fails. Never fall back to truncation.
    for attempt in range(40):
        try:
            os.replace(tmp, path)
            return
        except PermissionError as error:
            if not _transient_windows_lock(error) or attempt == 39:
                raise
            time.sleep(0.05)
