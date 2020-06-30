import decorators
import discord
import discord.ext.commands as disextc
import logging as lg
import os
import praw
import typing as typ

import constants
import cogs.reddit.utils as utils
from converters import BooleanFuzzyConverter as FuzzyBool

# TODO: Upvote/downvote query.
# TODO: watch for upvote/down vote, tally per user, use as money.
# todo: strip &#x200B;
# todo: persistence
# TODO: Submission/Comment search
# TODO: Search by timestamp
# https://www.reddit.com/r/redditdev/comments/5gfvik/praw_getting_all_submissions_for_the_past_two/
# https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html?highlight=submissions#praw.models.Subreddit.submissions
# TODO: subreddit population party popper at population increments.

reddit_config_group = 'reddit'

log = lg.getLogger(__name__)


# praw uses tons of protected members we need access to.
# noinspection PyProtectedMember
class Reddit(disextc.Cog):
    """ Reddit Connection.

    This cog handles the connection and commands and procesess related to
    reddit.

    To be able to log into to reddit, it needs these env keys set:
    REDDIT_USER_AGENT
    REDDIT_CLIENT_ID
    REDDIT_CLIENT_SECRET
    REDDIT_USERNAME
    REDDIT_PASSWORD

    If they are not set or it cannot connect, Reddit functionality will be
    disabled.
    """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

    @property
    async def reddit(self) -> typ.Optional[praw.reddit.Reddit]:
        if not await utils.reddit_credential_check():
            return None
        return praw.Reddit(
            user_agent=os.environ['REDDIT_USER_AGENT'],
            client_id=os.environ['REDDIT_CLIENT_ID'],
            client_secret=os.environ['REDDIT_CLIENT_SECRET'],
            username=os.environ['REDDIT_USERNAME'],
            password=os.environ['REDDIT_PASSWORD'])

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Test Reddit Cog credentials and config. """
        await self.bot.wait_until_ready()
        log.debug('on_ready reddit init fired.')
        await self.reddit_init()

    # Helpers

    async def reddit_init(self) -> None:
        """ Init and attach Reddit API. """
        txt_no_creds = \
            'Reddit credentials not setup, Reddit functions disabled.'
        txt_login_failed = \
            'Unable to log into reddit. Reboot to try again.'
        txt_logged_in = 'Logged into reddit as {}.'

        # Fetch Owner
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = appinfo.owner

        # This fires if the bot can't find the credentials in env.
        if not await utils.reddit_credential_check():
            log.info(txt_no_creds)
            pag_msg = await constants.paginate(txt_no_creds)
            if owner is not None:
                await constants.send_paginator(owner, pag_msg)
            return

        # This is if the bot does find the creds.
        reddit: praw.reddit.Reddit = await self.reddit
        if reddit:
            # Success!
            log.info(txt_logged_in.format(reddit.user.me().name))
        else:
            log.info(txt_login_failed)
            pag_msg = await constants.paginate(txt_login_failed)
            await constants.send_paginator(owner, pag_msg)
        return

    # Reddit Group Commands

    @disextc.group(name='red', hidden=True)
    @decorators.with_roles(constants.moderator_and_up)
    async def reddit_group(self, ctx: disextc.Context):
        """ Grouping for the reddit cog commands. """
        if ctx.invoked_subcommand is None:
            await ctx.send('No subcommand given.')

    @reddit_group.command(name='id', hidden=True)
    @disextc.is_owner()
    async def get_profile_command(self, ctx: disextc.Context, redditor: str):
        """ This retrieves a redditor's profile. """
        result: praw.reddit.models.Redditor = \
            (await self.reddit).redditor(redditor)
        if result is None:
            await ctx.send(f'Could not find redditor: {redditor}')
        else:
            import yaml as yl
            result._fetch()
            temp = vars(result)
            temp['_reddit'] = None
            # TODO: Paginate this display.
            await constants.send_paginator(
                ctx, await constants.paginate(
                    f'{yl.safe_dump(temp)}'))

    @reddit_group.command(name='sub', hidden=True)
    @disextc.is_owner()
    async def get_submission_command(self, ctx: disextc.Context, sub_id: str):
        """ Retrieve Submission. """
        # TODO:
        #   gj4d4z -> Picture Post
        #   eu4iwf -> Self Post
        #   gjmvt8 -> Video Post
        submission: praw.reddit.Submission = \
            (await self.reddit).submission(id=sub_id)
        await utils.display_submission(self.bot, ctx, submission)

    @reddit_group.command(name='com', hidden=True)
    @disextc.is_owner()
    async def get_comment_command(self, ctx: disextc.Context, com_id: str):
        """ Retrieve Comment."""
        comment: praw.reddit.Comment = (await self.reddit).comment(com_id)
        await utils.display_comment(self.bot, ctx, comment)

    # Inbox Group Commands

    @reddit_group.group(name='inb', hidden=True)
    @disextc.is_owner()
    async def inbox_group(self, ctx: disextc.Context, count: int = 10):
        if ctx.invoked_subcommand is None:
            # TODO: I need a paginator that lists reddit items.
            await ctx.send(
                f'```Inbox->All: ' +
                f'{list((await self.reddit).inbox.all(limit=count))}```')

    @inbox_group.command(name='unread', hidden=True)
    @disextc.is_owner()
    async def unread_inbox_command(self, ctx: disextc.Context):
        """List only unread items in inbox."""
        await ctx.send(
            f'```Inbox->New: {list((await self.reddit).inbox.unread())}```')

    # Moderator Group Commands

    @reddit_group.group(name='mod', hidden=True)
    @decorators.with_roles(constants.moderator_and_up)
    async def moderator_group(self, ctx: disextc.Context):
        """Grouping for moderator commands."""
        # TODO: Handle error more gracefully
        if ctx.invoked_subcommand is None:
            await ctx.send(f'reddit moderator subcommand not given')

    # TODO: Decorator for console log output
    # Todo: properly paginate (page control for key?)
    @moderator_group.command(name='stats', hidden=True)
    @decorators.with_roles(constants.moderator_and_up)
    async def moderator_statistics(
            self,
            ctx: disextc.Context,
            count: int = 500,
            display_key: FuzzyBool = True,
            compact: FuzzyBool = False,
            limit_to_mods: FuzzyBool = True,
            limit_actions: FuzzyBool = True):
        """ Retrieve the stats for mod actions. """
        # Protection
        if count > 5000:
            raise disextc.CommandError('Cannot parse more than 5000 entries.')

        # TODO: Configurable? v Magic String
        reddit = await self.reddit
        wh = reddit.subreddit('WiiHacks')
        from cogs.discord import ModStatsDisplay
        test = ModStatsDisplay(
            subreddit=wh,
            count=count,
            display_key=bool(display_key),
            compact=bool(compact),
            limit_to_mods=bool(limit_to_mods),
            limit_actions=bool(limit_actions),
            restrict_to_user=ctx.message.author)

        async with ctx.typing():
            await test.run(ctx)


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Reddit(bot))
