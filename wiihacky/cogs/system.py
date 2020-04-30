# import discord as dis
import discord.ext.commands as dec
import discord_interactive as dii
import logging as lg

default_log_category = 'bot'
default_log_channel = 'log'


# TODO: Bot.description : maybe after DB hookup?


class System(dec.Cog):
    """``` Bot Cog responsible for the Bot Operation.

    This bot carries all commands, listeners, etc, that tend to the bot itself.
```"""

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot

    @dec.command()
    @dec.is_owner()
    async def sys(self, ctx: dec.Context):
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
