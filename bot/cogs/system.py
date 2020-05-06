import discord as discord
import discord.ext.commands as disextc


# TODO: def command -> info
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

def run(self) -> None:
    """Start the bot daemon.

    This will start the bot daemon and run the underlying bot
    async loop. If it cannot connect to discord, it will execute the
    discord connection wizard until the operator can connect, or
    gives up.

    :return: None
    """
    txt_error_def_token = \
        """You still haven't changed the default discord token..."""
    txt_login_failure = "I couldn't log into discord... : {}"
    txt_login_giveup = [
        """Okay, gonna give up trying to login to discord.""",
        """But that means I'll have to shut it down..."""]
    txt_main_loop_term = 'The main loop has been terminated : {}'

    # TODO: Parse Arguments
    # Setup logging defaults

    # Add Cogs
    self._init_cogs()

    # Attempt to loin to discord
    while True:
        try:
            # Check to make sure we have a token
            import os
            txt_token_key = 'DISCORD_BOT_TOKEN'
            discord_token = os.environ[txt_token_key]
            if discord_token is None:
                log.critical(
                    f'Token not found under env key: {txt_token_key}')
                log.critical(
                    f'Please ensure token is set in your environment.')
                exit(-1)
            super().run(self.discord_token)
        except discord.errors.LoginFailure as e:
            log.error(txt_login_failure.format(e.args))
            exit(-1)
        except RuntimeError as e:
            log.info(txt_main_loop_term.format(e.args))
            exit(0)


default_log_category = 'bot'
default_log_channel = 'log'
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
        from constants import paginate, send_paginator
        self.paginate = paginate
        self.send_paginator = send_paginator

    @disextc.Cog.listener()
    async def on_ready(self):
        #TODO Ready message once booted up to log and owner?
        pass

    @disextc.command()
    async def clog(self, ctx: disextc.Context) -> None:
        """ Clear Log.

        If typed from a DMChannel, this will have the bot delete the last
        50 messages to you.

        :param ctx -> Context the command was called from
        :return None
        """
        # TODO: Make this work for the logging channel.
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

    @disextc.group()
    @disextc.is_owner()
    async def cog(self, ctx: disextc.Context) -> None:
        """ Cog related commands.

        :param ctx -> Invocation context
        :return None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @cog.command()
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

    @disextc.command()
    @disextc.is_owner()
    async def app_info(self, ctx: disextc.Context) -> None:
        """ Bot's application info.

        This will retrieve the bot's application info from discord.

        :param ctx -> Invocation Context
        :return None
        """
        await self.send_paginator(
            ctx, await self.paginate(repr(await self.bot.application_info())))

    @cog.command()
    @disextc.is_owner()
    async def list(self, ctx: disextc.Context) -> None:
        """ Lists all registered cogs.

        This will list all the cogs that are currently registered with the bot.


        """
        from constants import installed_cogs
        pag = disextc.Paginator()
        pag.add_line(repr(installed_cogs))
        for page in pag.pages:
            await ctx.send(page)

    @disextc.command()
    @disextc.is_owner()
    async def commands(self, ctx):
        await ctx.send([a.name for a in ctx.bot.commands])

    @disextc.command()
    @disextc.is_owner()
    async def info(self, ctx: disextc.Context) -> None:
        msg = await ctx.bot.application_info()
        await ctx.send(msg)

    @disextc.command()
    @disextc.is_owner()
    async def sys(self, ctx: disextc.Context) -> None:
        """This starts the cog menu."""
        # system = dii.Page('System Cog -> Things like rebooting the bot')
        await ctx.send(self.__doc__)

    @disextc.command()
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

    @disextc.command(name='wiz_log')
    @disextc.is_owner()
    async def wiz_setup_logging(self, ctx):
        """ Logging setup wizard.

        This function when invoked will cause the bot to open a DM with the
        invokee and display the main default bot menu.
        """
        await ctx.send('Not Implemented')


def setup(bot: disextc.Bot) -> None:
    """ Loads system cog. """
    bot.add_cog(System(bot))