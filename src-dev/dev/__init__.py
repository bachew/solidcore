from attrs import define, field
from dev import sh
from os import path as osp
from pathlib import Path
import os


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
