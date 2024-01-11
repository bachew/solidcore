from dev import ENVVAR_INCL_MANUAL_TESTS, logconf
from pathlib import Path
import os
import pytest


logconf.set_verbosity(1)


@pytest.fixture
def tmp_dir(tmpdir):
    yield Path(tmpdir)  # easier to work with Path objects


def manual_test(func):
    include = os.environ.get(ENVVAR_INCL_MANUAL_TESTS)

    if include:
        return func

    return pytest.mark.skip('manual test')(func)
