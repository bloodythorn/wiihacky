import discord.ext.commands as disextc

# TODO: Still unsure what this is going to do.
#   things like spam and antimalware.
#   The checks for role can be here or constants.
#   maybe move current checks here?
#   User registration.


class Security(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot


def setup(bot: disextc.Bot) -> None:
    """ Loads config cog. """
    bot.add_cog(Security(bot))
