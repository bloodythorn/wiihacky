import discord.ext.commands as dec


class Memory(dec.Cog):
    """ Bot Memory

    This module handles DB connections. Currently only mysql is supported.
    """

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot

        # we need to start off by doing a check on DB creds to see if they are
        # available, and work.
        # so the second we are online, we need to check to make sure the db is
        # 100%, or we message the owner with the wiz command.

    @dec.command()
    @dec.is_owner()
    async def sql(self, ctx: dec.Context, *, arg: str) -> None:
        await ctx.send(f'{ctx.guild}:{ctx.channel}:{ctx.author} -> {arg}')

    @dec.command(name='wiz_db')
    @dec.is_owner()
    async def wiz_db_setup(self, ctx: dec.Context) -> None:
        """ DB Setup Wizard.

        This will walk you through setting up your DB connection.

        :return:
        """
        await ctx.send('Implement me')
