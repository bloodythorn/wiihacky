import aiofiles
import discord.ext.commands as disextc
import logging as lg
import os
import random as rd
import yaml as yl

config_default_file_name = 'config.yml'
# TODO: Since the DB has went on line and creds are now stored in env, this
#   is essentially unused. I changed it to async but it still needs to be
#   tested.


class Config(disextc.Cog):
    """ Configuration handler for the bot.

    This is a yml file representation. Each configuration stored should be
    under its own key:

    discord:
        exampledata1
        exampledata2
    reddit:
        exampledata

    Between the database and env vars for credentials, this should only be
    used for things that would be beneficial to change at runtime.

    This file should most optimally be 'read' before used, and 'saved' after
    being altered. The defaults should be stored in each cog that utilizes
    them.

    Anything that is 'memory' should be stored in persistent memory cog.

    Attributes:
    -------------------------------------------

        bot -> The bot that was initialized with the cog.
        data -> a dictionary representation of the config file

    """

    def __init__(self, bot: disextc.Bot, **attrs):
        super().__init__()
        self.file_name = attrs.pop('file_name', config_default_file_name)
        self.bot = bot
        self.data = None

    # TODO: Async Versions of these functions.

    async def load_config(self):
        file_np = os.getcwd() + '/' + self.file_name
        with aiofiles.open(file_np, 'r')as f:
            self.data = yl.safe_load(f)

    async def save_config(self):
        file_np = os.getcwd() + '/' + self.file_name
        with aiofiles.open(file_np, 'w') as f:
            f.write(yl.safe_dump(self.data))


def setup(bot: disextc.Bot) -> None:
    """ Loads config cog. """
    bot.add_cog(Config(bot))
