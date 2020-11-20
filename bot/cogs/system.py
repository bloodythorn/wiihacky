import discord
import discord.ext.commands as disextc
import logging as lg
import typing as typ

import bot.convert as converters

txt_log_channel_key = 'botwrangler:log'

__version__ = '0.0.2'
log = lg.getLogger(__name__)

# TODO: ping command -> client.latency
# TODO: bot info -> client.user, client.guilds, client.emojis,
#   private channels, voice clients?
# TODO: Bot.description : maybe after DB hookup?
# Set description, get description, clear description
# ^ Same thing for status, etc.
# TODO: Confirm Action for more destructive commands.
# TODO: Get Cog Listeners
# https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html#inspection
# TODO: When bot boots it should give a lot more info in the log


txt_system_on_ready = "on_ready system cog fired."
txt_cog_sub_err = 'Invalid system cog subcommand.'
log_key = 'log_channel'


class System(disextc.Cog):
    """
        Cog responsible for the Bot Operation.

        This bot carries all commands, listeners, etc, that tend to the bot
        itself.
    """

    def __init__(self, bot: disextc.Bot) -> None:
        super().__init__()
        self.bot = bot
        self._log_channel = None

    # Helpers

    async def set_log_channel(self, snowflake: int) -> bool:
        """ Setter for log channel id.
        """
        self._log_channel = snowflake
        try:
            await self.set_log_to_memory(snowflake)
        except Exception as e:
            log.error(f"Exception saving log channel: {e}")
            return False
        finally:
            return True

    async def get_log_channel(self) -> int:
        """ Getter for log channel id.
        """
        output = 0
        try:
            output = await self.get_log_from_memory()
        except Exception as e:
            log.error(f"Could not get log channel: {e}")
        self._log_channel = output
        return output

    async def clear_log_channel(self) -> None:
        """ Setter for log channel snowflake.
        """
        self._log_channel = None
        await self.clear_log_from_memory()

    # FIXME: If this has no log channel set any command that uses it will
    # not work.
    async def send_to_log(self, text: str) -> bool:
        """ Sends text to log.
        """
        if self._log_channel is None:
            self._log_channel = await self.get_log_from_memory()
        log_chan = self.bot.get_channel(self._log_channel)
        if log_chan is None:
            raise disextc.CommandError('Could not find log channel!')
        else:
            await log_chan.send(text)
        if self._log_channel is None:
            log.error(f'Failed to send to chan_log: {text}')

    async def set_log_to_memory(self, snowflake: int) -> bool:
        """ Writes the log channel sf to memory.
        """
        from bot.cogs.memory import redis_scope
        from bot.constants import redis_config_db
        async with redis_scope(redis_config_db) as redis:
            await redis.set(log_key, snowflake)

    async def get_log_from_memory(self) -> int:
        """ Reads the sf id from memory.
        """
        from bot.cogs.memory import redis_scope
        from bot.constants import redis_config_db
        async with redis_scope(redis_config_db) as redis:
            return await redis.get(log_key)

    async def clear_log_from_memory(self) -> bool:
        """ Clears the ID from memory.
        """
        from bot.cogs.memory import redis_scope
        from bot.constants import redis_config_db
        async with redis_scope(redis_config_db) as redis:
            return await redis.delete(log_key)

    async def boot_text(self) -> None:
        """ Prints boot up text to log channel and console log.
        """
        pass
        # TODO: Implement me.

    # Listeners

    # @disextc.Cog.listener(name='on_command_error')
    # async def command_error(self, ctx: disextc.Context, error):
    #     """ Error Handler.
    #     """
    #     log.error(f'{type(error)}:{error}')
    #     if isinstance(error, disextc.errors.MissingRequiredArgument):
    #         await ctx.send(f'Error : {error}')

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Start up checks.
        """
        await self.bot.wait_until_ready()
        log.debug(txt_system_on_ready)
        # TODO: Boot text should be sent to con and log
        #   But we also need a command that just gets the text
        await self.boot_text()

    # System Group

    @disextc.group(name='sys')
    @disextc.is_owner()
    async def system_group(self, ctx: disextc.Context) -> None:
        """ Grouping for system commands. """
        # TODO: Resolve this gracefully
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No system subcommand given.')

    @system_group.command(name='inf')
    @disextc.is_owner()
    async def application_info_command(self, ctx: disextc.Context) -> None:
        """ Bot's application info.

        This will retrieve the bot's application info from discord.

        :param ctx -> Invocation Context
        :return None
        """
        # TODO: Flesh this out.
        # This should mirror what is printed to the log channel upon boot.
        # Praw Version
        # discord.py verion
        # whether the bot is in debug mode
        pass

    # Cog Group Commands

    @system_group.group(name='cog')
    @disextc.is_owner()
    async def cogs_group(self, ctx: disextc.Context) -> None:
        """ Cog related commands. """
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @cogs_group.command(name='act')
    @disextc.is_owner()
    async def list_active_cogs_command(self, ctx: disextc.Context) -> None:
        """ Lists active cogs.

            Lists all cogs currently active in the bot.

            :param ctx -> Invocation Context
            :return None
        """
        await ctx.send('```' + repr(list(ctx.bot.cogs.keys())) + '```')

    @cogs_group.command(name='lst')
    @disextc.is_owner()
    async def list_all_cogs_command(self, ctx: disextc.Context) -> None:
        """ Lists all registered cogs.

            This will list all the cogs that are currently registered with the
            bot.
        """
        from __main__ import cog_names
        await ctx.send('```' + repr(list(cog_names)) + '```')

    @cogs_group.command(name='loa')
    @disextc.is_owner()
    async def load_cog_command(
        self,
        ctx: disextc.Context,
        name: converters.FuzzyCogName
    ) -> None:
        """ Loads given extension/cog. """
        from __main__ import cog_names, module_names, cog_pref
        if name not in cog_names:
            raise disextc.CommandError(
                f'{name} not found in installed cogs.')
        cog_to_module = dict(zip(cog_names, module_names))
        self.bot.load_extension(cog_pref + cog_to_module[str(name)])
        txt_cog_loaded = \
            f'{name} cog has been loaded by {ctx.message.author.name}'
        log.info(txt_cog_loaded)
        await ctx.send(txt_cog_loaded)

    @cogs_group.command(name='unl')
    @disextc.is_owner()
    async def unload_cog_command(
        self,
        ctx: disextc.Context,
        name: converters.FuzzyCogName
    ) -> None:
        """ Unloads given extension/cog. """
        if name not in ctx.bot.cogs.keys():
            raise disextc.CommandError(
                f'No loaded cog found with the name {name}.')
        from __main__ import cog_names, module_names, cog_pref
        cog_to_module = dict(zip(cog_names, module_names))
        self.bot.unload_extension(cog_pref + cog_to_module[str(name)])
        txt_cog_unloaded = f'{name} cog unloaded by {ctx.message.author.name}.'
        log.info(txt_cog_unloaded)
        await ctx.send(txt_cog_unloaded)

    @cogs_group.command(name='rel', aliases=('reboot',))
    @disextc.is_owner()
    async def reload_cog_command(
        self,
        ctx: disextc.Context,
        name: converters.FuzzyCogName
    ) -> None:
        """Reloads given cog."""
        if name not in ctx.bot.cogs.keys():
            raise disextc.CommandError(
                f"Could not find cog '{name}' in loaded cog list.")
        from __main__ import cog_names, module_names, cog_pref
        cog_to_module = dict(zip(cog_names, module_names))
        self.bot.reload_extension(cog_pref + cog_to_module[str(name)])
        txt_cog_reloaded = f'{name} cog reloaded by {ctx.message.author.name}.'
        log.info(txt_cog_reloaded)
        await ctx.send(txt_cog_reloaded)

    # Console group

    @system_group.group(name='con')
    @disextc.is_owner()
    async def console_group(self, ctx: disextc.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No subcommand given for con')
            # loggers = [lg.getLogger()]  # get the root logger
            # noinspection PyUnresolvedReferences
            # loggers = loggers + [
            #    lg.getLogger(name) for name in lg.root.manager.loggerDict]
            # for name in loggers:
            #    await ctx.send(f"Registered Logs: {name}")

    # TODO: Make this result persistent between reboots using redis.
    @console_group.command(name='lvl')
    @disextc.is_owner()
    async def set_get_log_level(
        self, ctx: disextc.Context,
        name: converters.FuzzyCogName,
        level: typ.Optional[converters.FuzzyLogLevelName]
    ) -> None:
        """ sets log level if given, gets log level if not."""
        log.debug(f'change log level fired: {name} | {level}')
        if name not in ctx.bot.cogs.keys():
            raise disextc.CommandError(
                f"Could not find cog '{name}' in loaded cog list.")
        from __main__ import cog_names, module_names, cog_pref
        cog_to_module = dict(zip(cog_names, module_names))
        module_name = cog_pref + cog_to_module[name]
        temp_log = lg.getLogger(module_name)
        if level is not None:
            temp_log.setLevel(str(level))
        await ctx.send(f'{temp_log}')

    # Log Group

    @system_group.group(name='log')
    @disextc.is_owner()
    async def log_group(self, ctx: disextc.Context) -> None:
        """ This is the group dealing with in-discord logging.
        """
        if ctx.invoked_subcommand is None:
            if self._log_channel is None:
                self._log_channel = await self.get_log_from_memory()
            if self._log_channel is None:
                await ctx.send(f'No log channel currently set.')
            else:
                await ctx.send(f'Log channel set to : {self._log_channel}')

    @log_group.command(name='snd')
    @disextc.is_owner()
    async def txt_to_log_command(self, ctx: disextc.Context, *, message: str):
        """Sends text to discord log."""
        await self.send_to_log(message)
        await ctx.send(f"Sent '{message}' to the log.")

    @log_group.command(name='set')
    @disextc.is_owner()
    async def set_log_channel_command(
        self,
        ctx: disextc.Context,
        chan: discord.TextChannel
    ) -> None:
        """ This command will set the logging channel to the given channel.
        """
        await self.set_log_channel(chan.id)
        txt_set_log_chan = 'Log set to {}.'
        await ctx.send(txt_set_log_chan.format('#' + chan.name))
        await self.send_to_log(txt_set_log_chan.format('this channel'))
        log.debug(txt_set_log_chan.format('#' + chan.name))

    @log_group.command(name='clr')
    @disextc.is_owner()
    async def clear_log_channel_command(
        self,
        ctx: disextc.Context
    ) -> None:
        """ This command clears the given channel to send logs to.
        """
        await self.clear_log_from_memory()
        self._log_channel = None
        await ctx.send(f'Log channel cleared.')


def setup(bot: disextc.Bot) -> None:
    """ Loads system cog. """
    bot.add_cog(System(bot))
