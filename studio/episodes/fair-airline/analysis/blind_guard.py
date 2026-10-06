"""Deny Python file access to mixed raw inputs and network in gate processes.

The managed workspace resets directory permissions between tool calls; chmod
is not a persistent boundary here. This audit hook is a process-level safeguard
for these Python entry points, not a claim of kernel sandbox isolation.
"""
import os
from pathlib import Path
import sys
from common import RAW

RAW_RESOLVED = RAW.resolve()

def audit(event, args):
    if event in ('open', 'os.listdir', 'os.scandir'):
        p=args[0]
        if isinstance(p,(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(p)).resolve()
            if path==RAW_RESOLVED or RAW_RESOLVED in path.parents:
                raise PermissionError('Mixed raw inputs are denied to this outcome-blind process')
    if event=='socket.connect':
        raise PermissionError('Network access is denied to outcome-blind gate processes')
    if event=='subprocess.Popen':
        command=args[1]
        if not isinstance(command,(list,tuple)) or list(command[:2])!=['git','show']:
            raise PermissionError('Only read-only git show is permitted in this gate process')

def install():
    sys.addaudithook(audit)

def verify_denial():
    try:
        (RAW/'dictionary.html').open('rb')
    except PermissionError:
        return True
    raise AssertionError('Raw access denial failed')
