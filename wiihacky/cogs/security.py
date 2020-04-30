import discord.ext.commands as dec


class Security(dec.Cog):

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot
