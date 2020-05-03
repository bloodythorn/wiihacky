import discord.ext.commands as disext
# import praw as prw


class Reddit(disext.Cog):

    def __init__(self, bot: disext.Bot):
        super().__init__()
        self.bot = bot


# self.reddit = pr.Reddit(
#    user_agent=self.config.data['reddit']['user_agent'],
#    client_id=self.config.data['reddit']['client_id'],
#    client_secret=self.config.data['reddit']['client_secret'],
#    username=self.config.data['reddit']['username'],
#    password=self.config.data['reddit']['password'])
