import discord.ext.commands as disextc


class Security(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot


def setup(bot: disextc.Bot) -> None:
    """ Loads config cog. """
    bot.add_cog(Security(bot))