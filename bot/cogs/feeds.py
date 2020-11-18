import discord.ext.commands as disextc


class Feeds(disextc.Cog):
    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Feeds(bot))
