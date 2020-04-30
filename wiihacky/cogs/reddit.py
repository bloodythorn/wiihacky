import discord.ext.commands as dec
import praw as pr


class Reddit(dec.Cog):

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot


# self.reddit = pr.Reddit(
#    user_agent=self.config.data['reddit']['user_agent'],
#    client_id=self.config.data['reddit']['client_id'],
#    client_secret=self.config.data['reddit']['client_secret'],
#    username=self.config.data['reddit']['username'],
#    password=self.config.data['reddit']['password'])
