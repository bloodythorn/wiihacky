#!/usr/bin/env python3

import logging as lg
import os
import praw as pr
from time import sleep
import yaml as yl

FORMAT_STRING = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
lg.basicConfig(level=lg.INFO, format=FORMAT_STRING)

CONFIG_NAME = 'config.yml'


def getConfig():
    file_np = "{}/{}".format(os.getcwd(), CONFIG_NAME)
    with open(file_np, 'r') as config_file:
        return yl.load(config_file)


class WiiHacky(pr.Reddit):

    def __init__(self, config):
        # store configuration
        self._config = config
        # init logger
        self._log = lg.getLogger(self.__class__.__name__)
        self._log.info("successfully initialized logger.")
        # init reddit instance
        pr.Reddit.__init__(
            self,
            user_agent=self._config['auth']['user_agent'],
            client_id=self._config['auth']['client_id'],
            client_secret=self._config['auth']['client_secret'],
            username=self._config['auth']['username'],
            password=self._config['auth']['password'])
        self._log.info("successfully initialized reddit instance.")
        self._log.info("logged in as {}".format(self.user.me()))

    def run(self):
        self._log.info("starting bot. press ctrl-c to exit.")
        # interactive (hopefully) loop
        try:
            while True:
                sleep(0.5)
        except KeyboardInterrupt:
            self._log.info("ctrl-c interupt detected.")


if __name__ == "__main__":
    wh = WiiHacky(getConfig())
    wh.run()
