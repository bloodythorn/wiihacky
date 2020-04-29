import discord.ext.commands as dec
import logging as lg
import os
import random as rd
import yaml as yl

# TODO: These should be in personality.
# TODO: or maybe default config for personality

default_config = {'discord': {'token': 'put_your_bot_token_here'}}


class Config(dec.Cog):
    """ Configuration handler for the bot.

    This class will initialize and dole out any configuration option needed
    by a cog or the main module. However remember that this file should only
    contain secure things like tokens and db creds.

    Anything that is 'memory' should be stored in persistent memory cog.
    """

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        level_default = lg.DEBUG

        # Prep Log
        # TODO: move default
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.setLevel(level_default)
        self.file_name = None
        self.data = None

    # TODO: Async Versions of these functions.
    @staticmethod
    def _load_config(file_name) -> dict:
        """ Get Configuration from disk.

        This function will retrieve the configuration dict from yaml file.

        :return None
        """
        file_np = os.getcwd() + '/' + file_name
        with open(file_np, 'r') as config_file:
            return yl.safe_load(config_file)

    @staticmethod
    def _save_config(file_name: str, data: dict):
        """ Commit Configuration to disk.
        """
        file_np = os.getcwd() + '/' + file_name
        with open(file_np, 'w') as config_file:
            config_file.write(yl.safe_dump(data))

    def wiz_create_config(self) -> bool:
        """ A wizard for config creation.

        This function when run will save a blank dict into configured file_name.

        :return: bool with results
        """
        # TODO: Also if there are any config 'defaults' they might want to be
        #   put here.
        # TODO: text constants probably need a unified local.
        txt_query = 'Would you like to create a config.yml file? '
        txt_save_fail = 'Could not save file: {}'
        txt_save_created = 'Save file {} created.'
        txt_save_sarcasm = [
            """Shutting it down. The user doesn't want a config...""",
            """Not really sure why not...""",
            """But I can't really run without one...."""]
        txt_wiz_start = """***-> Starting config wizard..."""

        self.log.info(txt_wiz_start)
        txt = None
        from .persona import \
            txt_positive, txt_negative, txt_ambiguous_answer
        while not txt or \
                (txt.lower() not in txt_positive and
                 txt.lower() not in txt_negative):
            # Make sure the log buffer is clean.
            from time import sleep
            sleep(0.5)
            # Get user response.
            txt = input(txt_query)

            if txt.lower() in txt_positive:
                try:
                    self._save_config(self.file_name, default_config)
                except Exception as e:
                    self.log.critical(txt_save_fail.format(e.args))
                    return False
                self.log.info(txt_save_created.format(self.file_name))
            elif txt.lower() in txt_negative:
                for retort in txt_save_sarcasm:
                    self.log.critical(retort)
                return False
            else:
                self.log.warning(rd.choice(txt_ambiguous_answer))

        return True

    def load(self):
        """ Wrapper for _load_config.
        """
        self.data = self._load_config(self.file_name)

    def save(self):
        """ Wrapper for _save_config.
        """
        self._save_config(self.file_name, self.data)
