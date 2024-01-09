from collections.abc import Sequence
from contextlib import contextmanager
from typing import Any
import os
import shlex
import shutil
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

    try:
        return subprocess.run(cmd, **kwargs)
    except FileNotFoundError:
        raise FileNotFoundError(f'program not found: {cmd[0]}')


@contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    log = structlog.get_logger()

    log.info(f'chdir: {str(new_dir)}', dir=str(new_dir))
    os.chdir(new_dir)

    try:
        yield
    finally:
        log.info(f'chdir: {str(old_dir)}', dir=str(old_dir))
        os.chdir(old_dir)


def remove(path_or_paths, *, ignore_not_found=True):
    if isinstance(path_or_paths, list):
        paths = path_or_paths
    else:
        paths = [path_or_paths]

    log = structlog.get_logger()

    for path in paths:
        log.info(f'removing {str(path)!r}', path=str(path))
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            if not ignore_not_found:
                raise
        except NotADirectoryError:
            os.remove(path)


def get_env_var(name: str) -> str:
    value = os.environ.get(name)

    if not value:
        raise ValueError(f'Environment variable {name!r} is not set')

    return value
