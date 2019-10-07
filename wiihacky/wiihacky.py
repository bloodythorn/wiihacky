"""WiiHacky Module."""

import logging as lg
import os
from time import sleep
import praw as pr
import yaml as yl

import const
import scraper

lg.basicConfig(
    level=lg.INFO,
    format=const.LOG_FORMAT_STRING)


class WiiHacky(pr.Reddit):
    """WiiHacky's direct interface."""

    def __init__(self):
        """Initialize Wiihacky."""
        # store configuration
        self.config = self.load_config()

        # init logger
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.info(wiihacky.const.WH_INIT_LOGGER_SUCC)

        # init reddit instance
        pr.Reddit.__init__(
            self,
            user_agent=self.config['auth']['user_agent'],
            client_id=self.config['auth']['client_id'],
            client_secret=self.config['auth']['client_secret'],
            username=self.config['auth']['username'],
            password=self.config['auth']['password'])
        self.log.info(wiihacky.const.WH_INIT_REDDIT_SUCC)
        self.log.info(wiihacky.const.WH_INIT_LOGGED_IN, self.user.me())

        # init scraper
        self.scraper = scrap.Scraper()
        self.log.info(wiihacky.const.WH_INIT_SCRAPER)

    @staticmethod
    def load_config():
        """Get Configuration.

        This function will retrieve the configuration dict from yaml file.

        Returns
        -------
        A dictionary containing all configuration options.

        """
        file_np = "{}/{}".format(os.getcwd(), const.FILE_DEFAULT_CONFIG)
        with open(file_np, 'r') as config_file:
            return yl.safe_load(config_file)

    def run(self):
        """Run bot.

        The bot will perform scheduled tasks and eventually respond to
        CLI-like commands until told to exit.
        """
        self.log.info(wiihacky.const.WH_RUN_START_BOT)
        # interactive (hopefully) loop
        try:
            while True:
                sleep(0.5)
        except KeyboardInterrupt:
            self.log.info(wiihacky.const.WH_RUN_INTERUPT)
