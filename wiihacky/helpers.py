"""Helper functions."""

import time as tm
import const


def get_timestamp():
    """Obtain a timestamp in utc unix."""
    return const.UTC_STAMP, int(tm.time())


def get_version_stamp():
    """Obtain a stamp containing software version."""
    return const.VERSION_TEXT, const.__version__
