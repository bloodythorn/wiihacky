# If the configuration is not set to run from the project run directory,
# this test will not work.

import pytest


@pytest.fixture
def wh():
    from wiihacky import WiiHacky
    wh = WiiHacky()
    return wh
