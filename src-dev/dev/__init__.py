from attrs import define, field
from dev import sh
from os import path as osp
from pathlib import Path
from glob import glob
import os
import sys


ENVVAR_INCL_MANUAL_TESTS = 'DEV_INCLUDE_MANUAL_TESTS'


@define
class Development:
    base_dir: Path = field()
    source_dirs: list[Path] = field()

    @base_dir.default
    def create_base_dir(self):
        return Path(__file__).parents[2]

    @source_dirs.default
    def create_source_dirs(self):
        paths_str = os.environ.get('PYTHONPATH') or ''
        raw_paths = paths_str.split(osp.pathsep)
        paths = [Path(p) for p in raw_paths if p]
        base_dir = self.base_dir
        source_dirs = [p for p in paths if p.is_relative_to(base_dir)]
        # To add new source directory, please update src-dev/bootstrap.py
        return source_dirs

    def lint(self):
        for source_dir in self.source_dirs:
            sh.run(['flake8'], cwd=str(source_dir))

        for source_dir in self.source_dirs:
            sh.run(['mypy', '.'], cwd=str(source_dir))

    def test(self, pytest_args=None, *, manual=False):
        if pytest_args is None:
            pytest_args = []
        else:
            pytest_args = list(pytest_args)

        if manual:
            os.environ[ENVVAR_INCL_MANUAL_TESTS] = '1'
            pytest_args += ['--capture', 'no']
        else:
            os.environ.pop(ENVVAR_INCL_MANUAL_TESTS, None)

        with sh.chdir(self.base_dir):
            sh.run(['pytest', *pytest_args])

    def build(self):
        with sh.chdir(self.base_dir):
            sh.remove(['build', 'dist'])
            sh.remove(list(glob('**/*.egg-info')))
            sh.run([sys.executable, '-m', 'build', '--wheel'])

    def upload(self):
        with sh.chdir(self.base_dir):
            dist_files = list(Path().glob('dist/*'))
            sh.run(['twine', 'check', *dist_files])

            for required_var in ['TWINE_USERNAME', 'TWINE_PASSWORD']:
                sh.env_var(required_var)

            sh.run(['twine', 'upload', '--verbose', '--non-interactive', *dist_files])
