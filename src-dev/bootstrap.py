from os import path as osp
from os import environ as env
from pathlib import Path
from textwrap import dedent
from venv import EnvBuilder
import pickle
import platform
import runpy
import subprocess
import sys
import os


class Venv:
    __slots__ = (
        'base_dir',
        'venv_dir',
        'bin_dir',
        'python',
        'pip_config',
        'pip_installs',
        'pyproject_mtime')

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.venv_dir = base_dir / 'venv'
        self.bin_dir = self._get_bin_dir()
        self.python = self.bin_dir / 'python'

        # See https://pip.pypa.io/en/stable/topics/configuration/
        self.pip_config = dedent('''\
            ''')

        # Dev requirements
        self.pip_installs = [
            ['-U', 'pip'],
            ['-U', 'setuptools', 'wheel'],
            'attrs',
            'build',
            'click',
            'flake8',
            'mypy',
            'pytest',
            'structlog',
            'twine',
        ]

        self.pyproject_mtime = 0
        pyproject_toml = base_dir / 'pyproject.toml'

        if pyproject_toml.exists():
            self.pip_installs.append(['-e', base_dir])
            self.pyproject_mtime = os.stat(pyproject_toml).st_mtime

    def _get_bin_dir(self):
        plat = platform.system()

        if plat == 'Windows':
            return self.venv_dir / 'Scripts'

        return self.venv_dir / 'bin'

    def __str__(self):
        return f'Virtual environment {str(self.venv_dir)!r}'

    def is_active(self):
        if not self.venv_dir.exists():
            return False

        return Path(sys.executable).is_relative_to(self.venv_dir)

    @property
    def spec(self):
        return {k: getattr(self, k) for k in self.__slots__}

    @property
    def updated_spec_file(self):
        return self.venv_dir / 'updated-spec.pickle'

    def is_up_to_date(self):
        try:
            updated_spec = pickle.loads(self.updated_spec_file.read_bytes())
        except FileNotFoundError:
            return False

        return self.spec == updated_spec

    def update(self):
        venv_dir = self.venv_dir
        builder = EnvBuilder(clear=venv_dir.exists(), with_pip=True)
        builder.create(venv_dir)
        pip_conf_file = venv_dir / 'pip.conf'
        pip_conf_file.write_text(self.pip_config)
        pip_prog = [self.python, '-m', 'pip']

        for args in self.pip_installs:
            if isinstance(args, str):
                args = [args]

            run([*pip_prog, 'install', *args])

        self.updated_spec_file.write_bytes(pickle.dumps(self.spec))


def main():
    base_dir = Path(__file__).resolve().parents[1]
    env_file = base_dir / 'env.py'

    if env_file.is_file():
        runpy.run_path(env_file)

    venv = Venv(base_dir)

    if not venv.is_up_to_date():
        if venv.is_active():
            panic(f'{venv} is oudated, please exit and try again')

        print(f'{venv} is outdated, updating...')
        venv.update()
        print(f'{venv} updated')

    env['PATH'] = osp.pathsep.join([
        str(base_dir / 'bin'),
        str(venv.bin_dir),
        env.get('PATH') or ''])
    env['PYTHONPATH'] = osp.pathsep.join([
        str(base_dir / 'src-dev'),
        str(base_dir / 'src'),
        # Add other source directories here
        env.get('PYTHONPATH') or '',
    ])
    env['PYTHONUNBUFFERED'] = '1'
    env['PYTHONUTF8'] = '1'

    args = sys.argv[1:]
    res = run([venv.python, '-m', 'dev', *args], check=False, print_cmd=False)
    raise SystemExit(res.returncode)


def panic(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def run(cmd, *, print_cmd=True, **kwargs):
    kwargs.setdefault('check', True)
    cmd = [str(arg) for arg in cmd if cmd is not None]

    if print_cmd:
        cmdline = subprocess.list2cmdline(cmd)
        print(f'bootstrap.run: {cmdline}')

    return subprocess.run(cmd, **kwargs)


main()
