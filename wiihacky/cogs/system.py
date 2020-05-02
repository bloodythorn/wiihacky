import discord as dis
import discord.ext.commands as dec
# import discord_interactive as dii

default_log_category = 'bot'
default_log_channel = 'log'
# TODO: Bot.description : maybe after DB hookup?
# TODO: Confirm Action for more destructive commands.


class System(dec.Cog):
    """``` Bot Cog responsible for the Bot Operation.

    This bot carries all commands, listeners, etc, that tend to the bot itself.
```"""

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot
    # TODO: moderator functions
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

    @dec.command()
    async def clog(self, ctx: dec.Context):
        """ Clear Log.

        If typed from a DMChannel, this will have the bot delete the last
        200 messages to you.
        """
        txt_dmonly = """```I can only clear a DM, dingbat.```"""
        if isinstance(ctx.channel, dis.DMChannel):
            async for message in ctx.channel.history(limit=200):
                if message.author == self.bot.user:
                    await message.delete()
        else:
            await ctx.send(txt_dmonly)
            # TODO: Make this work for the logging channel.

    @dec.command()
    @dec.is_owner()
    async def emojis(self, ctx):
        await ctx.send(ctx.bot.emojis)

    @dec.command()
    @dec.is_owner()
    async def cogs(self, ctx):
        await ctx.send(ctx.bot.cogs)

    @dec.command()
    @dec.is_owner()
    async def commands(self, ctx):
        await ctx.send([a.name for a in ctx.bot.commands])

    @dec.command()
    @dec.is_owner()
    async def info(self, ctx: dec.Context) -> None:
        msg = await ctx.bot.application_info()
        await ctx.send(msg)

    @dec.command()
    @dec.is_owner()
    async def sys(self, ctx: dec.Context) -> None:
        """This starts the cog menu."""
        # system = dii.Page('System Cog -> Things like rebooting the bot')
        await ctx.send(self.__doc__)

    @dec.command()
    @dec.is_owner()
    async def shutdown(self, ctx: dec.Context):
        await ctx.send('Not Implemented')

    # def command -> info

    @dec.is_owner()
    @dec.command(name='wiz_log')
    async def wiz_setup_logging(self, ctx):
        """ Logging setup wizard.

        This function when invoked will cause the bot to open a DM with the
        invokee and display the main default bot menu.
        """
        await ctx.send('Not Implemented')

# async def test1(ctx: dec.Context, *args):
#    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
