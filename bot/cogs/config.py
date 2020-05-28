import aiofiles
import discord
import discord.ext.commands as disextc
import logging as lg
import os
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
        # TODO: Should we use this sort of init on other cogs/classes?
        self.file_name = attrs.pop('file_name', config_default_file_name)
        self.bot = bot
        self.data = {}

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Initialize the config cog. """
        await self.bot.wait_until_ready()

        txt_config_on_ready = "on_ready config cog fired."
        lg.getLogger().debug(txt_config_on_ready)

        # Grab the owner
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = appinfo.owner
        # TODO: Check for a config in the cwd.
        #   No config? Create one
        #   Config? Load it.

    # Helpers

    async def load_config(self):
        file_np = os.getcwd() + '/' + self.file_name
        with aiofiles.open(file_np, 'r')as f:
            self.data = yl.safe_load(f)

    async def save_config(self):
        file_np = os.getcwd() + '/' + self.file_name
        with aiofiles.open(file_np, 'w') as f:
            f.write(yl.safe_dump(self.data))

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
