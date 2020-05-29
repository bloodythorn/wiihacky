import discord
import discord.ext.commands as disextc
import discord.ext.tasks as disextt
import logging as lg
import praw
import typing as typ

import cogs.reddit.utils as utils


from datetime import timedelta

# TODO: Top Posts for Today
# TODO: This needs a lot of doccu attention.
# !fee sub add wiihacks-comment wiihacks 711058635215601746 comments
# !fee sub add wiihacks-new wiihacks 711058353660362782 new
# !fee mul add bloodythorn-gaming-new bloodythorn gaming 715415648095961090 new
feed_config_group = 'feeds'
log = lg.getLogger(__name__)


# Feed Modes

class FeedMode:
    def __init__(self, mode_name: str):
        self._mode_name = mode_name
        self._cache = None

    @staticmethod
    def verify_mode(name: str):
        return name in ['new', 'comments']

    @property
    def name(self):
        return self._mode_name

    def to_dict(self):
        output = vars(self)
        return output

    async def get_new_posts(self,
                            feed_source: typ.Union[
                                praw.reddit.Subreddit,
                                praw.reddit.models.Multireddit]):
        new_list = None
        if self._mode_name == 'new':
            new_list = list(feed_source.new(limit=10))
        elif self._mode_name == 'comments':
            new_list = list(feed_source.comments(limit=10))
        new_list = new_list
        if self._cache is None:  # Un-initialized
            self._cache = new_list
            return set()
        else:
            old_list = self._cache
            self._cache = new_list
            diff = []
            old_ids = [a.id for a in old_list]
            for post in new_list:
                if post.id not in old_ids:
                    diff.append(post)
            return set(diff)

    async def execute(self,
                      bot: disextc.Bot,
                      channel: discord.TextChannel,
                      feed_source: typ.Union[
                        praw.reddit.Subreddit,
                        praw.reddit.models.Multireddit]) -> None:
        new_posts = await self.get_new_posts(feed_source)
        for post in new_posts:
            if isinstance(post, praw.reddit.Comment):
                await utils.display_comment(
                    bot, channel, post,
                    clear=False, stop=False, eject=False)
            if isinstance(post, praw.reddit.Submission):
                await utils.display_submission(
                    bot, channel, post,
                    clear=False, stop=False, eject=False)


class PeriodMode(FeedMode):
    def __init__(self, mode_name: str, period: timedelta):
        super().__init__(mode_name)
        self._delta = period
        self._last_run = None

    @staticmethod
    def verify_mode(name: str):
        return name in ['hot', 'rising']


class TimeFrameMode(PeriodMode):
    def __init__(self, mode_name, period: timedelta, tf: str):
        super().__init__(mode_name, period)
        self._time_frame = tf

    @staticmethod
    def verify_mode(name: str):
        return name in ['controversial', 'top']

    @staticmethod
    def verify_time_depth(tf: str):
        """Can be one of: all, day, hour, month, week, year (default: all)."""
        return tf in ['all', 'day', 'hour', 'month', 'week', 'year']


# Feed Types


class Feed:
    """
    Base class for a reddit feed.

    Parameters
    -----------
    name: :class:`str`
        The name of the feed.
    channel_id: :class:`int`
        Snowflake ID of the channel to broadcast

    """
    def __init__(self, name: str, channel_id: int):
        self._name = name
        self._channel_id = channel_id
        self._mode = None
    # TODO: from_dict

    @property
    def name(self) -> str:
        return self._name

    @property
    def channel_id(self) -> int:
        return self._channel_id

    def to_dict(self):
        output = vars(self)
        output['mode'] = self._mode.to_dict()
        return output


class SubredditFeed(Feed):
    """
    A reddit feed centered around a Subreddit.

    Parameters
    -----------
    subreddit:
    mode:
    """
    def __init__(self,
                 name: str,
                 channel_id: int,
                 subreddit: str,
                 mode: str):
        super().__init__(name, channel_id)
        self._subreddit = subreddit
        self._mode = get_mode(mode)(mode)

    @property
    def subreddit(self):
        return self._subreddit

    @property
    def mode(self):
        return self._mode

    async def execute(self, bot: disextc.Bot, reddit: praw.Reddit):
        subreddit = reddit.subreddit(self._subreddit)
        channel = bot.get_channel(self._channel_id)
        await self._mode.execute(bot, channel, subreddit)


class MultiredditFeed(Feed):
    """
    A reddit feed centered around a user's Multireddit

    Parameters
    ___________
    user:
    multi:
    mode:
    """
    def __init__(self,
                 name: str,
                 channel_id: int,
                 user: str,
                 multi: str,
                 mode: str):
        super().__init__(name, channel_id)
        self._user = user
        self._multi = multi
        self._mode: FeedMode = get_mode(mode)(mode)

    @property
    def multireddit(self):
        return self._user, self._multi

    @property
    def mode(self):
        return self._mode

    async def execute(self, bot: disextc.Bot, reddit: praw.Reddit):
        multireddit = reddit.multireddit(redditor=self._user, name=self._multi)
        channel = bot.get_channel(self._channel_id)
        await self._mode.execute(bot, channel, multireddit)


def get_mode(
        modestr: str
        ) -> typ.Union[type(FeedMode),
                       type(PeriodMode),
                       type(TimeFrameMode)]:
    """Given a mode string, this will return the corresponding mode class. """
    if TimeFrameMode.verify_mode(modestr):
        return TimeFrameMode
    elif PeriodMode.verify_mode(modestr):
        return PeriodMode
    elif FeedMode.verify_mode(modestr):
        return FeedMode
    else:
        raise Exception(f'Unknown mode name: {modestr}')


class Feeds(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self.feeds = {}
        self.feed_processing_loop.start()

    @disextc.Cog.listener()
    async def on_ready(self):
        await self.load_feeds()
    # Processes

    @disextt.loop(seconds=5.0)
    async def feed_processing_loop(self) -> None:
        """This processes all configured feeds."""
        await self.bot.wait_until_ready()
        try:
            reddit = await self.bot.get_cog('Reddit').reddit
            if self.feeds is not None:
                for feed in self.feeds.values():
                    await feed.execute(self.bot, reddit)
        except Exception as e:
            lg.getLogger(__name__).debug(
                f'Exception During Reddit Access: {e.args}')

    # Feed Group Commands

    @disextc.group(name='fee', hidden=True)
    @disextc.is_owner()
    async def feed_group(self, ctx: disextc.Context) -> None:
        """Grouping for reddit feed related commands. """
        if ctx.invoked_subcommand is None:
            await ctx.send('```' + repr(self.feeds) + '```')

    async def load_feeds(self) -> None:
        """Loads or saves feeds to/from config file. """
        # Get Config Cog
        config = self.bot.get_cog('Config')
        if config is None:
            log.error('Could not load config cog to load feed config')
            return
        if 'reddit' not in config.data:
            log.error('Reddit not configured.')
            self.feeds = {}
            return
        if 'feeds' not in config.data['reddit']:
            log.error('Feeds not configured in Reddit.')
            self.feeds = {}
            return

    async def save_feeds(self) -> None:
        """Loads or saves feeds to/from config file. """
        # Get Config Cog
        config = self.bot.get_cog('Config')
        if config is None:
            log.error('Could not load config cog to save feed config')
            return
        if 'reddit' not in config.data:
            # TODO: FIXME
            # config.data.update(reddit_config_defaults)
            pass
        log.debug('save feeds not implemented.')

    async def add_feed(self, feed: Feed) -> None:
        if feed.name in self.feeds:
            raise KeyError('Entry already exists')
        self.feeds[feed.name] = feed
        await self.save_feeds()

    async def remove_feed(self, name: str) -> None:
        if name not in self.feeds:
            raise KeyError('Entry not in dict.')
        self.feeds[name] = None
        await self.save_feeds()

    @feed_group.command(name='rem', hidden=True)
    @disextc.is_owner()
    async def remove_feed_command(
            self, ctx: disextc.Context, feed_name: str) -> None:
        if feed_name in self.feeds:
            self.feeds.pop(feed_name)
            await ctx.send(f'Removed feed: {feed_name}')
        else:
            await ctx.send(f'Could not find feed: {feed_name}')

    @feed_group.group(name='sub', hidden=True)
    @disextc.is_owner()
    async def subreddit_feed_group(self, ctx: disextc.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(
                '```' +
                repr([a for a in self.feeds if a is SubredditFeed]) +
                '```')

    @subreddit_feed_group.command(name='add', hidden=True)
    @disextc.is_owner()
    async def add_subreddit_feed_command(
            self,
            ctx: disextc.Context,
            feed_name: str,
            subreddit_name: str,
            channel_id: int,
            feed_type: str,
    ) -> None:
        feed = SubredditFeed(
            name=feed_name,
            subreddit=subreddit_name,
            channel_id=channel_id,
            mode=feed_type)
        channel = self.bot.get_channel(channel_id)
        reddit = await self.bot.get_cog('Reddit').reddit
        sub = reddit.subreddit(subreddit_name)

        if not FeedMode.verify_mode(feed_type):
            raise Exception(f'Unknown feed type: {feed_type}')

        if channel is None:
            raise Exception('Argument channel_id not found.')
        try:
            sub._fetch()
        except Exception as e:
            raise Exception(f'Argument subreddit_name not found {e}.')

        self.feeds[feed.name] = feed

        await ctx.send(f'```Created feed {repr(feed)} {channel} {sub}```')

    @feed_group.group(name='mul', hidden=True)
    @disextc.is_owner()
    async def multireddit_feed_group(self, ctx: disextc.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(
                '```' +
                repr([a for a in self.feeds if a is MultiredditFeed]) +
                '```')

    @multireddit_feed_group.command(name='add', hidden=True)
    @disextc.is_owner()
    async def add_multi_feed_command(
            self,
            ctx: disextc.Context,
            feed_name: str,
            user_name: str,
            multi_name: str,
            channel_id: int,
            feed_type: str
    ) -> None:
        feed = MultiredditFeed(
            name=feed_name,
            user=user_name,
            multi=multi_name,
            channel_id=channel_id,
            mode=feed_type)
        channel = self.bot.get_channel(channel_id)
        reddit: praw.reddit.Reddit = await self.bot.get_cog('Reddit').reddit
        multi = reddit.multireddit(redditor=user_name, name=multi_name)

        if not FeedMode.verify_mode(feed_type):
            raise Exception(f'Unknown feed type: {feed_type}')

        if channel is None:
            raise Exception('Argument channel_id not found.')
        try:
            multi._fetch()
        except Exception as e:
            raise Exception(f'Argument subreddit_name not found {e}.')

        self.feeds[feed.name] = feed

        await ctx.send(f'```Created feed {repr(feed)} {channel} {multi}```')
