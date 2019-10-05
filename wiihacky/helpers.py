"""Helper functions."""

import time as tm
import wiihacky.const as const


def get_timestamp():
    """Obtain a timestamp in utc unix."""
    return (const.SCRAPE_UTC_STAMP, int(tm.time()))
