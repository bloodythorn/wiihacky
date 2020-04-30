import discord as dis
import discord.ext.commands as dec


class Discord(dec.Cog):

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot

    @dec.command()
    @dec.is_owner()
    async def users(self, ctx: dec.Context, *, member: dis.Member) -> None:
        await ctx.send(member.display_name)

    @users.error
    async def users_error(self, ctx: dec.Context, error):
        await ctx.send('```' + str(error) + '```')

    async def angry_axe_action(self, ctx: dec.Context, msg: dis.Message):
        """ The Angry Axe.

        The Angry Axe function will take the context given and attempt to
        delete it if possible. It is meant to be the action of the
        Angry Axe listener.
        """
        await ctx.send(f'Implement Me{msg}')
