from os import path as osp
from os import environ as env
from pathlib import Path
from venv import EnvBuilder
import pickle
import runpy
import subprocess
import sys


class Venv:
    __slots__ = (
        'venv_dir',
        'version',
        'pip_install_com_opts',
        'pip_installs')

    def __init__(self, venv_dir):
        self.venv_dir = venv_dir
        self.version = 1  # increase if pip_installs haven't changed but venv needs to be updated
        self.pip_install_com_opts = [
            # Insert common pip install options here, e.g. --index-url
        ]

        # Dev requirements
        self.pip_installs = [
            ['-U', 'pip'],
            ['-U', 'setuptools', 'wheel'],
            'attrs',
            'click',
            'structlog',
            'mypy',
            'pytest',
        ]

    def __str__(self):
        return f'virtual environment {str(self.venv_dir)!r}'

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
        pip = venv_dir / 'bin' / 'pip'
        common_opts = self.pip_install_com_opts

        for args in self.pip_installs:
            if isinstance(args, str):
                args = [args]

            run([pip, 'install', *common_opts, *args])

        self.updated_spec_file.write_bytes(pickle.dumps(self.spec))


def main():
    base_dir = Path(__file__).resolve().parents[1]
    env_file = base_dir / 'env.py'

    if env_file.is_file():
        runpy.run_path(env_file)

    venv_dir = base_dir / 'venv'
    venv = Venv(venv_dir)

    if (base_dir / 'pyproject.toml').exists():
        venv.pip_installs.append(['-e', base_dir])

    if not venv.is_up_to_date():
        if venv.is_active():
            panic(f'please exit outdated {venv}')

        print(f'{venv} is outdated, updating...')
        venv.update()
        print(f'{venv} updated')

    env['PATH'] = osp.pathsep.join([
        str(base_dir / 'bin'),
        str(venv_dir / 'bin'),
        env.get('PATH') or ''])
    env['PYTHONPATH'] = osp.pathsep.join([
        str(base_dir / 'src-dev'),
        str(base_dir / 'src'),
        # Add other source directories here
        env.get('PYTHONPATH') or '',
    ])
    env['PYTHONUTF8'] = '1'

    python = venv_dir / 'bin' / 'python'
    args = sys.argv[1:]
    res = run([python, '-m', 'dev', *args], check=False, print_cmd=False)
    raise SystemExit(res.returncode)


def panic(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def run(cmd, print_cmd=True, **kwargs):
    kwargs.setdefault('check', True)
    cmd = [str(arg) for arg in cmd if cmd is not None]

    if print_cmd:
        cmdline = subprocess.list2cmdline(cmd)
        print(f'bootstrap.run: {cmdline}')

    return subprocess.run(cmd, **kwargs)


main()
