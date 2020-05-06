import discord.ext.commands as disextc
# import discord.ext.tasks as disextt
# import praw as prw
import typing as typ


class Reddit(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self.reddit = None
        self.is_configured = False

    # Processes

    async def reddit_processes(self, ctx: disextc.Context) -> None:
        """ Reddit's Automated Processes. """
        # We only want the Connection Check reminder to happen once.
        if not self.config_check() and not self.is_configured:
            pass # Ask if they want to do the wizard
        # TODO : Reddit Connection Wizard
        # TODO : Comment Scroll Setup and Continue
        # TODO : Submission Scroll ^
        pass

    # Helpers

    async def config_check(self) -> bool:
        """ Check Reddit config for bot. """
        return False

    async def reddit_init(self) -> bool:
        """ Init and attach Reddit API. """
        return False

    # Commands

    async def reddit_toggle_process(
            self, ctx: disextc.Context, on: typ.Optional[bool]) -> None:
        """ Toggle Process Status. """
        pass

    # Wizards

    async def wiz_reddit_setup(self):
        """ Setup Reddit connection. """
        pass


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Reddit(bot))

# self.reddit = pr.Reddit(
#    user_agent=self.config.data['reddit']['user_agent'],
#    client_id=self.config.data['reddit']['client_id'],
#    client_secret=self.config.data['reddit']['client_secret'],
#    username=self.config.data['reddit']['username'],
#    password=self.config.data['reddit']['password'])
