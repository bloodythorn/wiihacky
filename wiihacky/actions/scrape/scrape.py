"""Scraper Module.

    A collection of functions to scrape data-items from Reddit. And actions
    that use them.
"""

from pathlib import Path
import logging as lg
import time as tm
import yaml as yl

import actions.scrape.constants as const


def ex_occurred(log: lg.Logger, tp: str, e: Exception):
    """Will log exceptions."""
    log.error(const.TXT_ERR_EXCEPT.format(tp, e))


# TODO: clean up gen_filename

# Helper Functions

# noinspection PyProtectedMember
def fetch(fetchable):
    """This function will make sure the given praw item has been fetched.
    This does so by accessing restricted data members.
    """
    if str('_' + const.TXT_FETCHED) in fetchable.__dict__ \
            and not fetchable._fetched:
        fetchable._fetch()


def gen_timestamp():
    """Obtain a timestamp in utc unix."""
    return const.TXT_UTC_STAMP, int(tm.time())


def gen_version_stamp():
    """Obtain a stamp containing software version."""
    from wiihacky import constants as wconst
    return wconst.VERSION_TEXT, wconst.__version__


def prep_dict(dct: dict, tp: str):
    """This function will prep a dict with all required information for
    storage.
    """
    dct.update([(const.TXT_TYPE, tp), gen_timestamp(), gen_version_stamp()])
    return dct


def save_file(file: str, data):
    """Given a filename/path and encodable data, this function will write
        that file.
    """
    with open(file, 'w') as f:
        f.write(yl.safe_dump(data))
    return True


def strip_all(dct: dict):
    """This function combines all strip functions to make sure a dictionary is
        encodable.
    """
    return strip_empty_string(strip_none(strip_underscore(dct)))


def strip_empty_string(dct: dict):
    """Strips all data containing an empty string."""
    return {i: dct[i] for i in dct if dct[i] != ''}


def strip_none(dct: dict):
    """Strips all keys who's data type is None."""
    return {i: dct[i] for i in dct if dct[i] is not None}


def strip_underscore(dct: dict):
    """Remove's praw's underscore members from the given dict."""
    return {i: dct[i] for i in dct if i[0] != '_'}


def verify_dir(ls: str):
    """Given a directory name, this function will verify that it exists,
        and if not, create it."""
    p = Path(ls)
    if not p.exists():
        p.mkdir()
    return p.exists()
