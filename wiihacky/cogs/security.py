import discord.ext.commands as disext


class Security(disext.Cog):

    def __init__(self, bot: disext.Bot):
        super().__init__()
        self.bot = bot
