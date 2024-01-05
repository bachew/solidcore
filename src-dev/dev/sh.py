from collections.abc import Sequence
from contextlib import contextmanager
from typing import Any
import os
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
    log.info(f'run: {cmdline}', cmd=cmd, run_kwargs=orig_kwargs)
    return subprocess.run(cmd, **kwargs)


@contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    log = structlog.get_logger()

    log.info(f'chdir: {str(new_dir)}', cwd=str(new_dir))
    os.chdir(new_dir)

    try:
        yield
    finally:
        log.info(f'chdir: {str(old_dir)}', cwd=str(old_dir))
        os.chdir(old_dir)


def get_env_var(name: str) -> str:
    value = os.environ.get(name)

    if not value:
        raise ValueError(f'Environment variable {name!r} is not set')

    return value
