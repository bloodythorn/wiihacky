import discord as discord
import discord.ext.commands as disext

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


default_log_category = 'bot'
default_log_channel = 'log'
txt_cog_sub_err = 'Invalid cog command.'
# TODO: Bot.description : maybe after DB hookup?
# TODO: Confirm Action for more destructive commands.
# TODO: Get Cog Listeners
# https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html#inspection


class System(disext.Cog):
    """``` Bot Cog responsible for the Bot Operation.

    This bot carries all commands, listeners, etc, that tend to the bot itself.
```"""

    def __init__(self, bot: disext.Bot):
        super().__init__()
        self.bot = bot
        from wiihacky import paginate, send_paginator
        self.paginate = paginate
        self.send_paginator = send_paginator

    @disext.Cog.listener()
    async def on_ready(self):
        #TODO Ready message once booted up to log and owner?
        pass

    @disext.command()
    async def clog(self, ctx: disext.Context) -> None:
        """ Clear Log.

        If typed from a DMChannel, this will have the bot delete the last
        50 messages to you.

        :param ctx -> Context the command was called from
        :return None
        """
        # TODO: Make this work for the logging channel.
        txt_dmonly = """I can only clear a DM, dingbat."""
        pages = disext.Paginator()
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

    @disext.group()
    @disext.is_owner()
    async def cog(self, ctx: disext.Context) -> None:
        """ Cog related commands.

        :param ctx -> Invocation context
        :return None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @cog.command()
    @disext.is_owner()
    async def active(self, ctx: disext.Context) -> None:
        """ Lists active cogs.

        Lists all cogs currently active in the bot.

        :param ctx -> Invocation Context
        :return None
        """
        pag = disext.Paginator()
        pag.add_line(repr(tuple(ctx.bot.cogs.keys())))
        for page in pag.pages:
            await ctx.send(page)

    @cog.command()
    @disext.is_owner()
    async def list(self, ctx: disext.Context) -> None:
        """ Lists all registered cogs.

        This will list all the cogs that are currently registered with the bot.


        """
        from wiihacky import txt_cogs_list
        pag = disext.Paginator()
        pag.add_line(repr(txt_cogs_list))
        for page in pag.pages:
            await ctx.send(page)

    @disext.command()
    @disext.is_owner()
    async def commands(self, ctx):
        await ctx.send([a.name for a in ctx.bot.commands])

    @disext.command()
    @disext.is_owner()
    async def info(self, ctx: disext.Context) -> None:
        msg = await ctx.bot.application_info()
        await ctx.send(msg)

    @disext.command()
    @disext.is_owner()
    async def sys(self, ctx: disext.Context) -> None:
        """This starts the cog menu."""
        # system = dii.Page('System Cog -> Things like rebooting the bot')
        await ctx.send(self.__doc__)

    @disext.command()
    @disext.is_owner()
    async def shutdown(self, ctx: disext.Context):
        # TODO: Confirmation
        pag = disext.Paginator()
        pag.add_line('Daisy, Daisy, give me your answer, do,')
        pag.add_line("""I'm half crazy all for the love of you ...""")
        for page in pag.pages:
            await ctx.send(page)
        await ctx.bot.close()

    # def command -> info

    @disext.is_owner()
    @disext.command(name='wiz_log')
    async def wiz_setup_logging(self, ctx):
        """ Logging setup wizard.

        This function when invoked will cause the bot to open a DM with the
        invokee and display the main default bot menu.
        """
        await ctx.send('Not Implemented')

# async def test1(ctx: dec.Context, *args):
#    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
