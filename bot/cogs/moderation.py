import discord.ext.commands as disextc


class Moderation(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super(Moderation, self).__init__(bot)
        self.bot = bot


def setup(bot: disextc.Bot) -> None:
    """ Loads moderation cog. """
    bot.add_cog(Moderation(bot))
