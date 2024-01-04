from dev import logconf
from pathlib import Path
import pytest


logconf.set_verbosity(1)


@pytest.fixture
def tmp_dir(tmpdir):
    yield Path(tmpdir)  # easier to work with Path objects
