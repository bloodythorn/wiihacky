#!/usr/bin/env python3

import logging as lg
import os
import praw as pr
import sys
import yaml as yl

log = lg.getLogger(__name__)
FORMAT_STRING = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
lg.basicConfig(level=lg.INFO, format=FORMAT_STRING)


class WiiHackey:

    def __init__(self):
        CONFIG_NAME = 'config.yml'
        file_np = "{}/{}".format(os.getcwd(), CONFIG_NAME)
        with open(file_np, 'r') as config_file:
            self._config = yl.load(config_file)


if __name__ == "__main__":
    log.info("Starting...")
    wh = WiiHackey()
    wh._reddit_login = pr.Reddit(
        user_agent=wh._config['auth']['user_agent'],
        client_id=wh._config['auth']['client_id'],
        client_secret=wh._config['auth']['client_secret'],
        username=wh._config['auth']['username'],
        password=wh._config['auth']['password'])
    log.info("{}".format(wh._reddit_login))
    sys.exit(0)
