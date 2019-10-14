"""Helper functions."""

import time as tm
import const


def get_timestamp():
    """Obtain a timestamp in utc unix."""
    return const.SCRAPE_UTC_STAMP, int(tm.time())


def get_stamped_dict(output):
    if not output:
        output = {}
    st_name, st_time = get_timestamp()
    output[st_name] = st_time
    return output
