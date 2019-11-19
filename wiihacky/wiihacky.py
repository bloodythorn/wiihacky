"""WiiHacky Module."""

import actions
import constants


def load_config():
    """Get Configuration.

    This function will retrieve the configuration dict from yaml file.

    Returns
    -------
    A dictionary containing all configuration options.

    """
    import os
    file_np = os.getcwd() + '/' + constants.FILE_DEFAULT_CONFIG
    with open(file_np, 'r') as config_file:
        import yaml as yl
        return yl.safe_load(config_file)


class WiiHacky:
    """WiiHacky's direct interface."""

    def __init__(self):
        """Initialize WiiHacky."""
        # init logger
        import logging as lg
        lg.basicConfig(
            level=lg.INFO, format=constants.LOG_FORMAT_STRING)
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.info(constants.TXT_LOGGER_SUCC)

        # store configuration
        self.config = load_config()

        # init reddit instance
        import praw as pr
        self.reddit = pr.Reddit(
            user_agent=self.config['auth']['user_agent'],
            client_id=self.config['auth']['client_id'],
            client_secret=self.config['auth']['client_secret'],
            username=self.config['auth']['username'],
            password=self.config['auth']['password'])
        self.log.info(constants.TXT_REDDIT_SUCC)
        self.log.info(constants.TXT_LOGGED_IN, self.reddit.user.me())

    def run(self):
        """Run bot.

        The bot will perform scheduled tasks and eventually respond to
        CLI-like commands until told to exit.
        """
        self.log.info(constants.TXT_START_BOT)
        # interactive (hopefully) loop
        try:
            while True:
                from time import sleep
                sleep(0.5)
        except KeyboardInterrupt:
            self.log.info(constants.TXT_INTERRUPT)
