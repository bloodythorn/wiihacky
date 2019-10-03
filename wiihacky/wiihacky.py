#!/usr/bin/env python3

"""WiiHacky main module."""

# import datetime as dt
import logging as lg
import os
from time import sleep
import praw as pr
import yaml as yl

from . import const

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
        self.log.info(const.TXT_INIT_LOGGER_SUCC)

        # init reddit instance
        pr.Reddit.__init__(
            self,
            user_agent=self.config['auth']['user_agent'],
            client_id=self.config['auth']['client_id'],
            client_secret=self.config['auth']['client_secret'],
            username=self.config['auth']['username'],
            password=self.config['auth']['password'])
        self.log.info(const.TXT_INIT_REDDIT_SUCC)
        self.log.info(const.TXT_INIT_LOGGED_IN, self.user.me())

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

    def cache_object(self, obj):
        """Cache object."""
        if isinstance(obj, (list, tuple)):
            for item in obj:
                self.cache_object(item)
            return
        self.log.info(CO_OBJC)
        self.log.error(CO_UNSP, type(obj))

    def run(self):
        """Run bot.

        The bot will perform scheduled tasks and eventually respond to
        CLI-like commands until told to exit.
        """
        self.log.info(RU_STRT)
        # interactive (hopefully) loop
        try:
            while True:
                sleep(0.5)
        except KeyboardInterrupt:
            self.log.info(RU_INTR)

    def scrape_user(self):
        """Scrape user.

        This function will scrape the user and update the user record.

        Return
        ------
        This will return a dictionary with all user data.

        """
        # Log
        info = self.log.info

        info(SC_USER)
        user = self.user
        blck = list(user.blocked())
        frnd = list(user.friends())
        mods = list(user.moderator_subreddits())
        mult = list(user.multireddits())
        subs = list(user.subreddits())
        output = {
            'id': user.me().id,
            'blocked': [a.id for a in blck],
            'friends': [a.id for a in frnd],
            'karma': user.karma(),
            'moderating': [a.id for a in mods],
            'multireddits': [a.name for a in mult],
            'preferences': dict(self.user.preferences()),
            'subscriptions': [a.id for a in subs]}
        self.cache_object([blck, frnd, mods, mult, subs])
        info(SC_COMP)
        return output

    def scrape_inbox(self):
        """Scrape inbox.

        This function will scrape the inbox and make sure it is up to date.

        Return
        ------
        This will return a dictionary with all inbox data.

        """
        # Log
        info = self.log.info
        info(const.TXT_SCRP_INBOX)
        info(const.TXT_SCRP_COMPLETE)
