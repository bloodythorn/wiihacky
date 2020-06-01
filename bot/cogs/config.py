import aiofiles
import aioredis
import discord
import discord.ext.commands as disextc
import logging as lg
import os
import yaml as yl

import decorators

# TODO: This currently won't be used, config file is saved to redis.
config_default_file_name = 'config.yml'
# TODO: Since the DB has went on line and creds are now stored in env, this
#   is essentially unused. I changed it to async but it still needs to be
#   tested.
# TODO: Change the config load into a retry-system.

log = lg.getLogger(__name__)


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
        # TODO: Should we use this sort of init on other cogs/classes?
        self.file_name = attrs.pop('file_name', config_default_file_name)
        self.bot = bot
        self.data = {}

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Initialize the config cog. """
        # NOTE: This needs to be done immediately to ensure that other cogs
        # won't have to wait long on it.
        await self.load_config()

        await self.bot.wait_until_ready()
        txt_config_on_ready = "on_ready config cog fired."
        log.debug(txt_config_on_ready)

        # FIXME: So far the load config is it, and it happens before ready to
        #   ensure that anything relies on it can get it after the ready.
        # Grab the owner
        # appinfo: discord.AppInfo = await self.bot.application_info()
        # owner: discord.User = appinfo.owner

    # Helpers

    async def load_config(self):
        """ Loads config from Redis."""
        memory = self.bot.get_cog('Memory')
        if memory is None:
            raise RuntimeError('Could not get memory cog to save config.')
        from cogs.memory import redis_db_config
        pool = await memory.get_redis_pool(redis_db_config)
        self.data = yl.safe_load(await pool.get('config'))
        result = await pool.set('config', yl.safe_dump(self.data))
        pool.close()
        await pool.wait_closed()
        log.debug(f'Results: {result}')

    async def save_config(self):
        """ Saves config to Redis."""
        memory = self.bot.get_cog('Memory')
        if memory is None:
            raise RuntimeError('Could not get memory cog to save config.')
        from cogs.memory import redis_db_config
        pool = await memory.get_redis_pool(redis_db_config)
        result = await pool.set('config', yl.safe_dump(self.data))
        pool.close()
        await pool.wait_closed()
        log.debug(f'Results: {result}')

    # Config Command Group

    @disextc.group(name='con', hidden=True)
    @disextc.is_owner()
    async def config_group(self, ctx: disextc.Context):
        """Group for config cog commands."""
        # TODO: more Gracefully
        if ctx.invoked_subcommand is None:
            await ctx.send('No config subcommand given.')

    @config_group.command(name='show', hidden=True)
    @disextc.is_owner()
    async def show_config_command(self, ctx: disextc.Context):
        """Dumps current config into ctx. """
        await ctx.send('```' + repr(self.data) + '```')


def setup(bot: disextc.Bot) -> None:
    """ Loads config cog. """
    bot.add_cog(Config(bot))
