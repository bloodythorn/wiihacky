import discord as discord
import discord.ext.commands as disextc
import logging as lg

from constants import paginate, send_paginator

system_defaults = {
    'bot_category': 'bot',
    'log_channel': 'log',
    'commands_channel': 'commands',
}

# TODO:
#   create a place for bot commands

# TODO:
#   on_message_delete, on_message_edit, on_reaction_clear,
#   on_reaction_clear_emoji,
#   on_private_channel_delete, on_private_channel_create,
#   on_private_channel_update, on_private_channel_pins_update,
#   on_guild_channel_delete, on_guild_channel_create,
#   on_guild_channel_update, on_guild_channel_pins_update
#   on_guild_integrations_update, on_webhooks_update
#   on_member_join, on_member_remove, on_member_update
#   on_user_update, on_guild_join, on_guild_remove, on_guild_update,
#   on_guild_role_create, on_guild_role_delete, on_guild_role_update
#   on_guild_emojis_update, on_guild_available, on_guild_unavailable
#   on_voice_state_update, on_member_ban, on_member_unban,
#   on_invite_create, on_invite_delete, on_group_join, on_group_remove
#   on_relationship_add, on_relationship_update,

txt_cog_sub_err = 'Invalid cog command.'
# TODO: Bot.description : maybe after DB hookup?
# TODO: Confirm Action for more destructive commands.
# TODO: Get Cog Listeners
# https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html#inspection


class System(disextc.Cog):
    """ Cog responsible for the Bot Operation.

    This bot carries all commands, listeners, etc, that tend to the bot itself.
    """

    def __init__(self, bot: disextc.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.log_channel = None

    # Helpers

    async def init_log(self) -> None:
        """This discovers the ID of the log channel."""
        # TODO: There should be an option for saving/loading this to/from
        #  the config.
        # Fetch Owner (WE shouldn't have to worry about waiting for the bot)
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner = appinfo.owner

        # See if we can find the designated log channel
        log_chan: discord.TextChannel = discord.utils.find(
            lambda m: m.name == system_defaults['log_channel'],
            self.bot.get_all_channels())
        # No?
        if log_chan is None:
            await owner.send(
                'No logging channel configured for {}->{}'.format(
                    system_defaults['bot_category'],
                    system_defaults['log_channel']))
            return
        # Not in the right category?
        elif log_chan.category.name != system_defaults['bot_category']:
            await owner.send('Log channel found but not in category {}'.format(
                        system_defaults['bot_category']))
            return

        # This is it!
        self.log_channel = log_chan.id
        log_chan = self.bot.get_channel(self.log_channel)

        # This shouldn't happen
        if log_chan is None:
            await owner.send("Unknown error finding logging channel.")

        # TODO: More information in the bootup? Cog Statuses?
        boot_txt = """Discord.py Version: {} Praw Version: {}"""
        import praw
        await log_chan.send(boot_txt.format(
            discord.__version__, praw.__version__))
        await log_chan.send('Log channel initialized, bot has booted.')

    async def send_to_log(self, message: str):
        """Sends a messaged to the designated, connected log channel. """
        # It's not setup...
        if self.log_channel is None:
            return
        log_chan = self.bot.get_channel(self.log_channel)
        await log_chan.send(message)

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Start up checks.

        Checks that the bot needs at the start will fire here. If there are
        any issues, the owner will be notified and told how to correct them.
        """
        txt_system_on_ready = "on_ready system cog fired."
        lg.getLogger().debug(txt_system_on_ready)
        await self.bot.wait_until_ready()

        # TODO: Check Config
        # TODO: Check Channels

        if self.log_channel is None:
            await self.init_log()

    # System Group

    @disextc.group(name='sys', hidden=True)
    @disextc.is_owner()
    async def system_group(self, ctx: disextc.Context):
        """ Grouping for system commands. """
        # TODO: Resolve this gracefully
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No system subcommand given.')

    @system_group.command(name='cdm', hidden=True)
    @disextc.is_owner()
    async def clear_direct_messages_command(
            self, ctx: disextc.Context) -> None:
        # TODO: This needs a better place. Clear the bot's DMs to you is all it
        #   really does and should be transitioned accordingly.
        """ Clear Log.

        If typed from a DMChannel, this will have the bot delete the last
        50 messages to you.

        :param ctx -> Context the command was called from
        :return None
        """
        txt_dmonly = """I can only clear a DM, dingbat."""
        pages = disextc.Paginator()
        pages.add_line(txt_dmonly)
        count = 0
        if isinstance(ctx.channel, discord.DMChannel):
            async for message in ctx.channel.history(limit=200):
                if message.author == self.bot.user:
                    count += 1
                    if count > 50:
                        return
                    await message.delete()
        else:
            for page in pages.pages:
                await ctx.send(page)

    @system_group.command(name='sysinfo', hidden=True)
    @disextc.is_owner()
    async def application_info_command(self, ctx: disextc.Context) -> None:
        """ Bot's application info.

        This will retrieve the bot's application info from discord.

        :param ctx -> Invocation Context
        :return None
        """
        await send_paginator(
            ctx, await paginate(repr(await self.bot.application_info())))

    @system_group.command(name='commands', hidden=True)
    @disextc.is_owner()
    async def list_commands_command(self, ctx):
        await ctx.send([a.name for a in ctx.bot.commands])

    @system_group.command(name='log', hidden=True)
    @disextc.is_owner()
    async def log_command(self, ctx: disextc.Context, *, message: str):
        """Sends text to discord log."""
        await self.send_to_log(message)

    @system_group.command(hidden=True)
    @disextc.is_owner()
    async def shutdown_command(self, ctx: disextc.Context):
        # TODO: Confirmation
        # TODO: Use this to create a relogon ->
        #   as I tink the only way you can change the bot activity is at
        #   login
        pag = disextc.Paginator()
        pag.add_line('Daisy, Daisy, give me your answer, do,')
        pag.add_line("""I'm half crazy all for the love of you ...""")
        for page in pag.pages:
            await ctx.send(page)
        await ctx.bot.close()

    # Cog Group Commands

    @system_group.group(name='cog', hidden=True)
    @disextc.is_owner()
    async def cogs_group(self, ctx: disextc.Context) -> None:
        """ Cog related commands.

        :param ctx -> Invocation context
        :return None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @cogs_group.command(name='act', hidden=True)
    @disextc.is_owner()
    async def active_command(self, ctx: disextc.Context) -> None:
        """ Lists active cogs.

        Lists all cogs currently active in the bot.

        :param ctx -> Invocation Context
        :return None
        """
        pag = disextc.Paginator()
        pag.add_line(repr(tuple(ctx.bot.cogs.keys())))
        for page in pag.pages:
            await ctx.send(page)

    @cogs_group.command(name='list', hidden=True)
    @disextc.is_owner()
    async def list_command(self, ctx: disextc.Context) -> None:
        """ Lists all registered cogs.

        This will list all the cogs that are currently registered with the bot.
        """
        from __main__ import installed_cogs
        pag = disextc.Paginator()
        pag.add_line(repr(installed_cogs))
        for page in pag.pages:
            await ctx.send(page)


def setup(bot: disextc.Bot) -> None:
    """ Loads system cog. """
    bot.add_cog(System(bot))