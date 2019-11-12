import os
import yaml as yl

import const

def gen_filename(scrape: dict):
    """When given a properly processed dict, it returns an appropriate
        filename.
    """
    tp = scrape[const.SCRAPE_TYPE]
    st = scrape[const.UTC_STAMP]

    # Inbox and User have the same format.
    if tp == const.TYPE_INBOX or tp == const.TYPE_USER:
        return const.FILE_FORMAT_ONE.format(tp, st)

    if tp == const.TYPE_COMMENT or tp == const.TYPE_MESSAGE or \
        tp == const.TYPE_SUBMISSION:
        ident = scrape[const.KEY_ID]
        return const.FILE_FORMAT_TWO.format(tp, ident, st)

    if tp == const.TYPE_REDDITOR or tp == const.TYPE_SUBREDDIT:
        nm = scrape[const.KEY_NAME]
        return const.FILE_FORMAT_TWO.format(tp, nm, st)

    if tp == const.TYPE_MULTIREDDIT:
        ow = scrape[const.KEY_OWNER]
        nm = scrape[const.KEY_NAME]
        return const.FILE_FORMAT_THREE.format(tp, ow, nm, st)


def load_config():
    """Get Configuration.

    This function will retrieve the configuration dict from yaml file.

    Returns
    -------
    A dictionary containing all configuration options.

    """
    file_np = const.LOAD_CONFIG.format(os.getcwd(), const.FILE_DEFAULT_CONFIG)
    with open(file_np, 'r') as config_file:
        return yl.safe_load(config_file)
