from collections.abc import Sequence
from typing import Any
import shlex
import structlog
import subprocess
import sys


def run(cmd: Sequence[Any], **kwargs: Any) -> subprocess.CompletedProcess:
    orig_kwargs = dict(kwargs)
    kwargs.setdefault('check', True)
    kwargs.setdefault('encoding', sys.stdout.encoding)
    cmd = [str(arg) for arg in cmd if arg is not None]
    cmdline = shlex.join(cmd)
    log = structlog.get_logger()
    log.info(f'running: {cmdline}', cmd=cmd, run_kwargs=orig_kwargs)
    return subprocess.run(cmd, **kwargs)
