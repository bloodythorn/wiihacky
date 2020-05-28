import discord.ext.commands as disextc

from .feeds import Feeds
from .reddit import Reddit


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Reddit(bot))
    bot.add_cog(Feeds(bot))
