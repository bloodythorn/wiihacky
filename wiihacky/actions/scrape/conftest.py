"""
This is the test for actions.scrape.comment.

It will scrape ten comments. Fail condition is if it gives an exception.

All tests that use it need to be set to run from the project's 'run' directory
or the instance will not be able to find its configuration.
"""

import pytest


@pytest.fixture
def wh():
    """
    This function returns an instance of the bot.

    :return: WiiHacky() instance.
    """
    from wiihacky import WiiHacky
    wh = WiiHacky()
    return wh
