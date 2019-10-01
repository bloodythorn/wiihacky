#!/usr/bin/env python3
"""WiiHacky main module."""

import logging as lg
import os
from time import sleep
import praw as pr
import yaml as yl

FORMAT_STRING = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
lg.basicConfig(level=lg.INFO, format=FORMAT_STRING)

CONFIG_NAME = 'config.yml'


def get_file_name(msg_dict):
    """Return a file name."""
    pass


def save_message(msg_dict):
    """Save message to hd."""
    pass


def message_to_dict(msg):
    """Convert message to dict()."""
    output = {}
    output['id'] = msg.id
    output['author'] = msg.author.id
    output['dest'] = msg.dest.id
    output['subject'] = msg.subject
    output['subreddit'] = msg.subreddit
    output['created_utc'] = msg.created_utc
    output['was_comment'] = msg.was_comment
    output['body'] = msg.body
    return output


class WiiHacky(pr.Reddit):
    """WiiHacky's direct interface."""

    def __init__(self):
        # store configuration
        self._config = self.load_config()
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
        self._log.info("logged in as %s", self.user.me())

    @staticmethod
    def load_config():
        """Get Configuration.

        This function will retrieve the configuration dict from yaml file.

        Returns
        -------
        A dictionary containing all configuration options.
        """
        file_np = "{}/{}".format(os.getcwd(), CONFIG_NAME)
        with open(file_np, 'r') as config_file:
            return yl.load(config_file)

    def run(self):
        """Run bot.

        The bot will perform scheduled tasks and eventually respond to
        CLI-like commands until told to exit.
        """
        self._log.info("starting bot. press ctrl-c to exit.")
        # interactive (hopefully) loop
        try:
            while True:
                sleep(0.5)
        except KeyboardInterrupt:
            self._log.info("ctrl-c interupt detected.")


if __name__ == "__main__":
    # TODO load a different config.
    WH = WiiHacky()
    WH.run()
