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
#   Create a place for a log
#   create a place for bot commands

# TODO: def command -> info
# TODO: Collective logger -> This might be a discord cog thing
# TODO: on_ready, on_connect, on_disconnect, on_resumed, on_typing,
#   on_message, on_message_delete, on_message_edit, on_reaction_add,
#   on_reaction_remove, on_reaction_clear, on_reaction_clear_emoji,
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

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

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

        # Grab the owner
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = appinfo.owner

        # Check Config

        # Check Channels

    # Cog Group Commands

    @disextc.group(name='cog', hidden=True)
    @disextc.is_owner()
    async def cogs_group(self, ctx: disextc.Context) -> None:
        """ Cog related commands.

        :param ctx -> Invocation context
        :return None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @cogs_group.command(hidden=True)
    @disextc.is_owner()
    async def active(self, ctx: disextc.Context) -> None:
        """ Lists active cogs.

        Lists all cogs currently active in the bot.

        :param ctx -> Invocation Context
        :return None
        """
        pag = disextc.Paginator()
        pag.add_line(repr(tuple(ctx.bot.cogs.keys())))
        for page in pag.pages:
            await ctx.send(page)

    @cogs_group.command(hidden=True)
    @disextc.is_owner()
    async def list(self, ctx: disextc.Context) -> None:
        """ Lists all registered cogs.

        This will list all the cogs that are currently registered with the bot.


        """
        from __main__ import installed_cogs
        pag = disextc.Paginator()
        pag.add_line(repr(installed_cogs))
        for page in pag.pages:
            await ctx.send(page)

    # Uncategorized

    @disextc.command(hidden=True)
    async def clog(self, ctx: disextc.Context) -> None:
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

    @disextc.command(hidden=True)
    @disextc.is_owner()
    async def app_info(self, ctx: disextc.Context) -> None:
        """ Bot's application info.

        This will retrieve the bot's application info from discord.

        :param ctx -> Invocation Context
        :return None
        """
        await send_paginator(
            ctx, await paginate(repr(await self.bot.application_info())))

    @disextc.command(hidden=True)
    @disextc.is_owner()
    async def commands(self, ctx):
        await ctx.send([a.name for a in ctx.bot.commands])

    @disextc.command(hidden=True)
    @disextc.is_owner()
    async def info(self, ctx: disextc.Context) -> None:
        msg = await ctx.bot.application_info()
        await ctx.send(msg)

    @disextc.command(hidden=True)
    @disextc.is_owner()
    async def sys(self, ctx: disextc.Context) -> None:
        """This starts the cog menu."""
        # system = dii.Page('System Cog -> Things like rebooting the bot')
        await ctx.send(self.__doc__)

    @disextc.command(hidden=True)
    @disextc.is_owner()
    async def shutdown(self, ctx: disextc.Context):
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


def setup(bot: disextc.Bot) -> None:
    """ Loads system cog. """
    bot.add_cog(System(bot))