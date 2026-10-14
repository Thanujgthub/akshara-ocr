"""Temporary Windows idle-sleep request scoped to one verified study controller.

Does not change the power plan or request display/away mode. Manual sleep and
lid actions remain under Windows/user control. No model or training state loads.
"""
import argparse
import ctypes
import os
import time
from datetime import datetime, timezone
from pathlib import Path
import psutil
from .research_io import save

CONTINUOUS=0x80000000
SYSTEM_REQUIRED=0x00000001


def owner_matches(owner, created):
    try:
        return owner.is_running() and owner.create_time()==created and 'ocr.colab_runner' in owner.cmdline()
    except psutil.NoSuchProcess:
        return False


def hold_request(owner, created, set_state, wait, record):
    if not owner_matches(owner, created):
        raise RuntimeError('Verified study controller is no longer live; no power request made')
    if not set_state(CONTINUOUS|SYSTEM_REQUIRED):
        raise RuntimeError('Windows rejected the temporary idle-sleep request')
    try:
        record('active')
        while owner_matches(owner, created):
            wait(30)
    finally:
        released=bool(set_state(CONTINUOUS))
        record('released' if released else 'release-call-failed')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pid',type=int,required=True)
    parser.add_argument('--created',type=float,required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if os.name!='nt':raise RuntimeError('Windows-only helper; no other platform power settings changed')
    out=Path(args.output)
    if out.exists():raise FileExistsError('Use a fresh evidence directory')
    owner=psutil.Process(args.pid)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    function=kernel.SetThreadExecutionState
    function.argtypes=[ctypes.c_uint32];function.restype=ctypes.c_uint32
    def record(status):
        save(out/'status.json',{'status':status,'updated_utc':datetime.now(timezone.utc).isoformat(),
             'helper_pid':os.getpid(),'owner_pid':args.pid,'owner_created':args.created,
             'request_flags':CONTINUOUS|SYSTEM_REQUIRED,'scope':'Idle system-sleep request only; controller identity checked every30seconds.',
             'manual_sleep_and_lid_actions_can_pause':True,'power_plan_changed':False,'display_request':False,
             'documentation':'https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate'})
    hold_request(owner,args.created,function,time.sleep,record)


if __name__=='__main__':main()
