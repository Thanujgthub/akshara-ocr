"""Read-only Windows commit-capacity gate before loading an OCR GPU model.

No GPU imports, process termination, pagefile changes or training launch. The
reserve is an operational margin, not a guarantee against later memory pressure.
"""
import argparse
import ctypes
import datetime
import json
import math
import os
from pathlib import Path

from .research_io import save

GIB = 1024 ** 3


def snapshot():
    if os.name != 'nt':
        raise RuntimeError('Windows memory inspection requires actual Windows; no estimated fallback')

    class PerformanceInformation(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in (
                'CommitTotal', 'CommitLimit', 'CommitPeak', 'PhysicalTotal',
                'PhysicalAvailable', 'SystemCache', 'KernelTotal', 'KernelPaged',
                'KernelNonpaged', 'PageSize')
        ] + [(name, ctypes.c_ulong) for name in ('HandleCount', 'ProcessCount', 'ThreadCount')]

    info = PerformanceInformation()
    info.cb = ctypes.sizeof(info)
    library = ctypes.WinDLL('psapi', use_last_error=True)
    function = library.GetPerformanceInfo
    function.argtypes = [ctypes.POINTER(PerformanceInformation), ctypes.c_ulong]
    function.restype = ctypes.c_int
    if not function(ctypes.byref(info), info.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    if not info.PageSize or info.CommitTotal > info.CommitLimit:
        raise RuntimeError('Windows returned invalid commit-capacity measurements')
    return {
        'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'commit_total_bytes': info.CommitTotal * info.PageSize,
        'commit_limit_bytes': info.CommitLimit * info.PageSize,
        'commit_headroom_bytes': (info.CommitLimit - info.CommitTotal) * info.PageSize,
        'available_ram_bytes': info.PhysicalAvailable * info.PageSize,
        'source': 'Native Windows GetPerformanceInfo; pagefile configuration is not runtime capacity.',
    }


def assess(measured, model_private_gib=6., reserve_gib=3.):
    if not all(math.isfinite(x) and x > 0 for x in (model_private_gib, reserve_gib)):
        raise ValueError('Declare finite positive model allowance and reserve')
    total, limit = measured['commit_total_bytes'], measured['commit_limit_bytes']
    headroom = measured['commit_headroom_bytes']
    if not 0 <= total <= limit or headroom != limit - total:
        raise ValueError('Inconsistent commit-capacity measurement')
    required = math.ceil((model_private_gib + reserve_gib) * GIB)
    return {
        'passed': headroom >= required,
        'measurement': measured,
        'required_commit_headroom_bytes': required,
        'model_private_allowance_gib': model_private_gib,
        'reserve_gib': reserve_gib,
        'policy_basis': 'Recent trainer used about6GB private memory at Windows-confirmed exhaustion. Default6GiB allowance plus3GiB operational reserve before model loading.',
        'scope': 'Pre-load Windows capacity check only. Free physical RAM cannot replace commit headroom. Not native BF16, smoke, benchmark, runtime stability or accuracy evidence. Later memory demand can change.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-private-gib', type=float, default=6.)
    parser.add_argument('--reserve-gib', type=float, default=3.)
    parser.add_argument('--output')
    args = parser.parse_args()
    output = Path(args.output) if args.output else None
    if output is not None and output.exists():
        raise FileExistsError('Use a fresh memory report path; preserve prior evidence')
    report = assess(snapshot(), args.model_private_gib, args.reserve_gib)
    if output is not None:
        save(output, report)
    print(json.dumps(report, indent=2))
    if not report['passed']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
