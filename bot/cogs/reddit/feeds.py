import asyncio
import discord
import discord.ext.commands as disextc
import discord.ext.tasks as disextt
import logging as lg
import praw
import typing as typ

import cogs.reddit.utils as utils

from collections import deque
from datetime import timedelta

# TODO: Top Posts for Today
# TODO: This needs a lot of doccu attention.
# TODO: Debug logging in commands
# TODO: So far new and comments are all that's implemented in FeedModes
# TODO: Feed Commands should be put in documentation
# FIXME: For some reason every so often, 10hr old posts will re-post.
# !fee sub add wiihacks-comments wiihacks 711058635215601746 comments
# !fee sub add wiihacks-new wiihacks 711058353660362782 new

config_group_reddit = 'reddit'
config_group_feeds = 'feeds'
log = lg.getLogger(__name__)


# Feed Modes

class FeedMode:

    """ The base class for a feed mode.

    Since the base feed mode doesn't require any extra information the only
    thing stored is the mode_name.
    """

    def __init__(self, mode_name: str) -> None:
        """ Init Class """
        self._mode_name = mode_name
        self._cache = deque()

    @staticmethod
    def verify_mode(name: str) -> bool:
        """ Verify Mode Name

        This will return true if the string given matches one of the two feed
        mode types for this class.
        """
        return name in ['new', 'comments']

    @property
    def name(self) -> str:
        """ Getter for self._name """
        return self._mode_name

    def to_dict(self) -> dict:
        """ Output class to dict()."""
        output = dict()
        output['mode_name'] = self._mode_name
        return output

    async def get_new_posts(
            self,
            feed_source: typ.Union[
                praw.reddit.Subreddit,
                praw.reddit.models.Multireddit]):
        """ Get new posts.

        Return a list of 'new' posts, timewise from the last time the command
        was checked. For the first time it returns an empty set.
        """
        # get recent feed
        # log.debug(f'get_new_posts fired : {self._cache}')
        new_list = None
        if self._mode_name == 'new':
            new_list = list(feed_source.new(limit=10))
        elif self._mode_name == 'comments':
            new_list = list(feed_source.comments(limit=10))
        # log.debug(f'fetched: {new_list}')

        # Filter out ones we already have.
        new_list = [a for a in new_list if a not in self._cache]
        # log.debug(f'trimmed to {new_list} due to {self._cache}')

        # Un-initialized
        if len(self._cache) == 0:
            # log.debug(f'Initialized cache: {len(self._cache)}')
            return_data = []
        else:
            return_data = new_list

        # log.debug(f'Adding to cache...')
        self._cache.extend(new_list)

        # drain excess
        cache_limit = 20
        while len(self._cache) >= cache_limit:
            # log.debug(f'Draining excess: {len(self._cache)} > {cache_limit}')
            self._cache.popleft()

        # Send out new
        return return_data

    async def execute(self,
                      bot: disextc.Bot,
                      channel: discord.TextChannel,
                      feed_source: typ.Union[
                        praw.reddit.Subreddit,
                        praw.reddit.models.Multireddit]) -> None:
        """ Execute mode.

        Each time this is run, it will determine if there is anything to do and
        if so, do it.
        """
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


# TODO: Finish
class PeriodMode(FeedMode):
    def __init__(self, mode_name: str, period: timedelta):
        super().__init__(mode_name)
        self._delta = period
        self._last_run = None

    @staticmethod
    def verify_mode(name: str):
        return name in ['hot', 'rising']


# TODO: Finish
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
    feed_name: :class:`str`
        The name of the feed.
    channel_id: :class:`int`
        Snowflake ID of the channel to broadcast

    """
    def __init__(self, feed_name: str, channel_id: int):
        self._feed_name = feed_name
        self._channel_id = channel_id
        self._mode = None

    # TODO: from_dict should give either subreddit or reddit feed?

    @property
    def feed_name(self) -> str:
        return self._feed_name

    @property
    def channel_id(self) -> int:
        return self._channel_id

    def to_dict(self):
        output = dict()
        output['feed_name'] = self._feed_name
        output['channel_id'] = self._channel_id
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
                 feed_name: str,
                 channel_id: int,
                 subreddit: str,
                 mode: str):
        super().__init__(feed_name, channel_id)
        self._subreddit = subreddit
        self._mode = get_mode(mode)(mode)

    @property
    def subreddit(self):
        return self._subreddit

    @property
    def mode(self):
        return self._mode

    @classmethod
    def from_dict(cls, obj: dict):
        if all([
            'feed_name' in obj,
            'channel_id' in obj,
            'subreddit' in obj,
            'mode' in obj,
            'mode_name' in obj['mode']
        ]):
            return cls(
                feed_name=obj['feed_name'],
                channel_id=obj['channel_id'],
                subreddit=obj['subreddit'],
                mode=obj['mode']['mode_name']
            )
        else:
            raise RuntimeError('Unable to parse SubredditFeed from dict:'
                               f'{obj}')

    def to_dict(self):
        output = super().to_dict()
        output['subreddit'] = self._subreddit
        return output

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
                 feed_name: str,
                 channel_id: int,
                 user: str,
                 multi: str,
                 mode: str):
        super().__init__(feed_name, channel_id)
        self._user = user
        self._multi = multi
        self._mode: FeedMode = get_mode(mode)(mode)

    @property
    def multireddit(self):
        return self._user, self._multi

    @property
    def mode(self):
        return self._mode

    @classmethod
    def from_dict(cls, obj: dict):
        if all([
            'feed_name' in obj,
            'channel_id' in obj,
            'user' in obj,
            'multi' in obj,
            'mode' in obj,
            'mode_name' in obj['mode']
        ]):
            return cls(
                feed_name=obj['feed_name'],
                channel_id=obj['channel_id'],
                user=obj['user'],
                multi=obj['multi'],
                mode=obj['mode']['mode_name']
            )
        else:
            raise RuntimeError('Unable to parse Multireddit Feed from dict:'
                               f' {obj}')

    def to_dict(self):
        output = super().to_dict()
        output['user'] = self._user
        output['multi'] = self._multi
        return output

    async def execute(self, bot: disextc.Bot, reddit: praw.Reddit):
        multireddit = reddit.multireddit(redditor=self._user, name=self._multi)
        channel = bot.get_channel(self._channel_id)
        await self._mode.execute(bot, channel, multireddit)


# Utilities

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


def feed_from_dict(
        obj: dict
) -> typ.Optional[typ.Union[SubredditFeed, MultiredditFeed]]:
    """Convert from Dictionary

    Given a dictionary this function will attempt to return a parsed object.
    """
    log.debug(f'from_dict fired: {obj}')
    if 'subreddit' in obj:
        return SubredditFeed.from_dict(obj)
    return None


class Feeds(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self.feeds = {}
        self._feeds_loaded = False
        self.feed_processing_loop.start()

    def cog_unload(self):
        self.feed_processing_loop.cancel()

    # Events

    # TODO: listeners for on_member_join, on_member_remove

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Prep the Cog on load. """
        await self.bot.wait_until_ready()
        # FIXME: Right now this will just go on forever, every 5 seconds...
        #   Might want to put a max-retry, or incrementing timer for retry.
        while not self._feeds_loaded:
            await asyncio.sleep(5)
            self._feeds_loaded = await self.load_feeds()

    # Processes

    @disextt.loop(seconds=5.0)
    async def feed_processing_loop(self) -> None:
        """This processes all configured feeds."""
        await self.bot.wait_until_ready()
        try:
            reddit = await self.bot.get_cog('Reddit').reddit
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

    async def load_feeds(self) -> bool:
        """Loads or saves feeds to/from config file. """

        # Get Config Cog
        config = self.bot.get_cog('Config')
        if config is None:
            log.error('Could not load config cog to load feed config')
            return False

        # Check for reddit group
        if config_group_reddit not in config.data:
            log.error('Reddit not configured.')
            return False

        # Check for feeds group in reddit group
        if config_group_feeds not in config.data[config_group_reddit]:
            log.error('Feeds not configured in Reddit.')
            return False

        # Grab the feed group and put them in.
        feed_group = config.data[config_group_reddit][config_group_feeds]
        for feed_data in feed_group.values():
            await self.add_feed(feed_from_dict(feed_data))
        log.debug('Feeds Loaded.')
        return True

    async def save_feeds(self) -> None:
        """Loads or saves feeds to/from config file. """
        # Get Config Cog
        config = self.bot.get_cog('Config')
        if config is None:
            log.error('Could not load config cog to save feed config')
            raise RuntimeError('Could not load config cog to save feed config')
        # Check for reddit group
        if config_group_reddit not in config.data:
            config.data[config_group_reddit] = {}
        if config_group_feeds not in config.data[config_group_reddit]:
            config.data[config_group_reddit][config_group_feeds] = {}

        if self.feeds is None:
            self.feeds = {}
        for feed in self.feeds.values():
            log.debug(f'Saving: {feed.feed_name}')
            config.data[config_group_reddit][config_group_feeds][feed.feed_name] = feed.to_dict()
            await config.save_config()
        log.debug('Feeds saved.')

    async def add_feed(self, feed: Feed) -> None:
        # TODO: Docu and log
        if feed.feed_name in self.feeds:
            raise KeyError('Entry already exists')
        self.feeds[feed.feed_name] = feed

    async def remove_feed(self, name: str) -> None:
        # TODO: Docu and log
        if name not in self.feeds:
            raise KeyError('Entry not in dict.')
        self.feeds[name] = None

    @feed_group.command(name='save', hidden=True)
    @disextc.is_owner()
    async def save_feeds_command(self, ctx: disextc.Context):
        """Saves feeds for persistence."""
        await self.save_feeds()
        log.info('Feeds saved.')
        await ctx.send('Feeds saved.')

    @feed_group.command(name='load', hidden=True)
    @disextc.is_owner()
    async def load_feeds_command(self, ctx: disextc.Context):
        """Loads feeds from memory."""
        await self.load_feeds()
        log.debug('Feeds loaded.')
        await ctx.send('Feeds loaded.')

    @feed_group.command(name='rem', hidden=True)
    @disextc.is_owner()
    async def remove_feed_command(
            self, ctx: disextc.Context, feed_name: str) -> None:
        # TODO: Log and docu
        if feed_name in self.feeds:
            self.feeds.pop(feed_name)
            await ctx.send(f'Removed feed: {feed_name}')
        else:
            await ctx.send(f'Could not find feed: {feed_name}')

    @feed_group.group(name='sub', hidden=True)
    @disextc.is_owner()
    async def subreddit_feed_group(self, ctx: disextc.Context) -> None:
        # TODO: reformat this.
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
        # FIXME: This currently only handles one type of mode.
        feed = SubredditFeed(
            feed_name=feed_name,
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

        await self.add_feed(feed)

        await ctx.send(f'```Created feed {repr(feed)} {channel} {sub}```')
        # TODO: Send to discord log

    @feed_group.group(name='mul', hidden=True)
    @disextc.is_owner()
    async def multireddit_feed_group(self, ctx: disextc.Context) -> None:
        # TODO: Reformat this
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
        # FIXME: This currently only handles one type of feed
        feed = MultiredditFeed(
            feed_name=feed_name,
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

        await self.add_feed(feed)

        await ctx.send(f'```Created feed {repr(feed)} {channel} {multi}```')


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Feeds(bot))
