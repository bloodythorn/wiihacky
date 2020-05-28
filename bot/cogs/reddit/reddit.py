import cogs.reddit.utils as utils
import constants
import discord
import discord.ext.commands as disextc
import logging as lg
import os
import praw
import typing as typ

# TODO: Upvote/downvote query.
# TODO: watch for upvote/down vote, tally per user, use as money.
# todo: strip &#x200B;
# todo: persistence

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
    @disextc.is_owner()
    async def reddit_group(self, ctx: disextc.Context):
        """ Grouping for the reddit cog commands. """
        if ctx.invoked_subcommand is None:
            await ctx.send('No subcommand given.')

    @reddit_group.command(name='inbox', hidden=True)
    @disextc.is_owner()
    async def inbox_command(self, ctx: disextc.Context):
        # TODO: Turn this into a group with inbox functions.
        await ctx.send(
            f'```Inbox->All: {list(await self.reddit.inbox.all())}```')

    @reddit_group.command(name='id', hidden=True)
    @disextc.is_owner()
    async def get_profile_command(self, ctx: disextc.Context, redditor: str):
        """ This retrieves a redditor's profile. """
        result: praw.reddit.models.Redditor = \
            await self.reddit.redditor(redditor)
        if result is None:
            await ctx.send(f'Could not find redditor: {redditor}')
        else:
            await constants.send_paginator(
                ctx, await constants.paginate(
                    f'{repr(result)} created:{result.created_utc} ' +
                    f'link karma: {result.link_karma} ' +
                    f'post karma: {result.comment_karma}'))

    @reddit_group.command(name='sub', hidden=True)
    @disextc.is_owner()
    async def get_submission_command(self, ctx: disextc.Context, sub_id: str):
        """ Retrieve Submission. """
        # TODO:
        #   gj4d4z -> Picture Post
        #   eu4iwf -> Self Post
        #   gjmvt8 -> Video Post
        submission: praw.reddit.Submission = \
            await self.reddit.submission(id=sub_id)
        await utils.display_submission(self.bot, ctx, submission)

    @reddit_group.command(name='com', hidden=True)
    @disextc.is_owner()
    async def get_comment_command(self, ctx: disextc.Context, com_id: str):
        """ Retrieve Comment."""
        comment: praw.reddit.Comment = await self.reddit.comment(com_id)
        await utils.display_comment(self.bot, ctx, comment)

    # Moderator Group Commands

    @reddit_group.group(name='mod', hidden=True)
    @disextc.is_owner()
    async def moderator_group(self, ctx: disextc.Context):
        """Grouping for moderator commands."""
        # TODO: Handle error more gracefully
        if ctx.invoked_subcommand is None:
            await ctx.send(f'reddit moderator subcommand not given')

    @moderator_group.command(name='stats', hidden=True)
    @disextc.is_owner()
    async def moderator_statistics(
            self, ctx: disextc.Context, over: int = 500):
        """ Retrieve the stats for mod actions. """

        # Warn user for delay
        # TODO: Move this to personality.
        await ctx.send(f'Tallying {over} log entries...')

        reddit = await self.reddit

        async with ctx.typing():
            # fetch subreddit and moderators
            #   and define the actions we care about.
            # TODO: Configurable? v Magic String
            wh = reddit.subreddit('WiiHacks')
            mods = tuple(sorted([mod.name for mod in list(wh.moderator())]))
            metered_actions = {
                'approvecomment': 'app_com',
                'approvelink': 'app_lnk',
                'distinguish': 'dst',
                'ignorereports': 'ign_rep',
                'lock': 'lck',
                'removecomment': 'rem_com',
                'removelink': 'rem_lnk',
                'spamcomment': 'spam_com',
                'spamlink': 'spm_lnk',
                'sticky': 'stky'}
            # Raw data
            data = {}
            oldest = None
            headers = ['name']

            # Populate dictionary with results
            #   as well as pull actions and actors
            for entry in wh.mod.log(limit=over):

                # Filter
                # TODO: Make this variable/configurable?
                if entry._mod not in mods or \
                        entry.action not in metered_actions.keys():
                    continue

                # save Oldest
                if oldest is None:
                    oldest = entry.created_utc
                elif entry.created_utc < oldest:
                    oldest = entry.created_utc

                # If mod isn't present, record them.
                if entry._mod not in data:
                    data[entry._mod] = {}

                # New action for mod.
                if entry.action not in data[entry._mod]:
                    data[entry._mod][entry.action] = 1

                # Increment (If you've reached here we have both mod + action)
                data[entry._mod][entry.action] += 1

            # Pull detected actors and actions
            actors = tuple(sorted([a for a in data]))
            actions = []
            for actor in actors:
                actions += list(data[actor].keys())
            actions = tuple(sorted(list(dict.fromkeys(actions))))
            for action in actions:
                headers.append(metered_actions[action])

            # Flatten the data
            # TODO: Mods that don't have stats don't show up
            flats = []
            for mod in mods:
                temp = [mod]
                for action in actions:
                    if action in metered_actions.keys():
                        if mod in data and action in data[mod]:
                            temp.append(int(data[mod][action]))
                        else:
                            temp.append(0)
                flats.append(tuple(temp))

            # Output Stats
            import datetime
            import prettytable
            table = prettytable.PrettyTable(headers)
            for row in flats:
                table.add_row(row)
            await ctx.send(f"""```{table}
Oldest Log Entry: {str(datetime.datetime.fromtimestamp(oldest))}
```""")
