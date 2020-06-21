import decorators
import discord
import discord.ext.commands as disextc
import logging as lg
import os
import praw
import typing as typ

import constants
import cogs.reddit.utils as utils
from converters import BooleanFuzzyConverter as bool_fuzz

# TODO: Upvote/downvote query.
# TODO: watch for upvote/down vote, tally per user, use as money.
# todo: strip &#x200B;
# todo: persistence
# TODO: Submission/Comment search
# TODO: Search by timestamp
# https://www.reddit.com/r/redditdev/comments/5gfvik/praw_getting_all_submissions_for_the_past_two/
# https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html?highlight=submissions#praw.models.Subreddit.submissions

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
    @moderator_group.command(name='stats', hidden=True)
    @decorators.with_roles(constants.moderator_and_up)
    async def moderator_statistics(
            self,
            ctx: disextc.Context,
            count: int = 500,
            display_key: bool_fuzz = True,
            limit_to_mods: bool_fuzz = True,
            limit_actions: bool_fuzz = True):
        """ Retrieve the stats for mod actions. """
        # Protection
        if count > 5000:
            raise disextc.CommandError('Cannot parse more than 5000 entries.')

        # Warn user for delay
        await ctx.send(f'Tallying {count} log entries...')

        reddit = await self.reddit

        async with ctx.typing():
            # fetch sub & mods and define the actions we care about.
            # TODO: Configurable? v Magic String
            wh = reddit.subreddit('WiiHacks')
            users_to_pull = set()
            if limit_to_mods:
                users_to_pull = \
                    tuple(sorted([mod.name for mod in list(wh.moderator())]))
            metered_actions = tuple()
            if limit_actions:
                metered_actions = tuple(sorted([
                    'approvecomment', 'approvelink',
                    'lock', 'distinguish', 'ignorereports', 'sticky',
                    'removecomment', 'removelink',
                    'spamcomment', 'spamlink']))

            # Raw data
            data, oldest = await utils.tally_moderator_actions(
                history_limit=count,
                subreddit=wh,
                user_names=[*users_to_pull],
                actions_names=[*metered_actions])

            # Pull detected actors and actions
            actors = tuple(sorted(data.keys()))
            actions = []
            for actor in actors:
                actions += list(data[actor].keys())
            # Sorted List of actions with removed doubles.
            actions = tuple(sorted(set(actions)))

            # Convert to an np array
            import numpy as np
            tally = np.full(
                shape=(len(actors) + 1, len(actions) + 1), fill_value=0)
            for idx_y, actor in enumerate(actors):
                for idx_x, action in enumerate(actions):
                    if action in data[actor]:
                        tally[idx_y][idx_x] = data[actor][action]

            # Calc the Totals
            tally[len(actors), :] = tally.sum(axis=0)
            tally[:, len(actions)] = tally.sum(axis=1)

            # Headers
            import prettytable
            fields = ['X'] + [str(i) for i in range(len(actions))] + ['ttl']
            table = prettytable.PrettyTable(fields)
            for field in fields:
                table.align[field] = 'r'

            # Rows
            for idx, actor in enumerate(actors):
                table.add_row([idx] + list(tally[idx, :]))
            table.add_row(['ttl'] + list(tally[len(actors), :]))

            # Format Output
            output1 = f'Moderator Statistics Table:\n{table}'

            # Create Key
            column_key = [(str(idx), action)
                          for idx, action in enumerate(actions)]
            row_key = [(str(idx), action) for idx, action in enumerate(actors)]
            # Fill in blanks of the shorter list.
            blank = ('-', 'X')
            if len(column_key) > len(row_key):
                while len(column_key) > len(row_key):
                    row_key.append(blank)
            else:
                while len(column_key) < len(row_key):
                    column_key.append(blank)

            key_zip = list(zip(column_key, row_key))
            template = '{: >22} - |{: ^}| - {: <}\n'
            output2 = '{: >24} {: ^} {: <}\n'.format("column", "| |", "row")
            for row in key_zip:
                if len(column_key) > len(row_key):
                    output2 += template.format(
                        row[0][1], row[0][0], row[1][1])
                else:
                    output2 += template.format(
                        row[0][1], row[0][0], row[1][1])
            output2 += f'Oldest Log Entry : '
            import datetime
            output2 += str(datetime.datetime.utcfromtimestamp(oldest)) + ' UTC'

            # send
            log.debug(f'sizes o1: {len(output1)} | o2: {len(output2)}')
            if len(output1) >= 2000:
                # FIXME: This is hackish ^
                await ctx.send(f'```Table too large to output...```')
            else:
                await ctx.send(f'```{output1}```')
            if display_key:
                await ctx.send(f'```{output2}```')


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Reddit(bot))
