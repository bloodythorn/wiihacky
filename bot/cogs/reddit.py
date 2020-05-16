import constants
import discord
import discord.ext.commands as disextc
import discord.ext.tasks as disextt
import logging as lg
import os
import praw as prw
import typing as typ

# from constants import paginate, send_paginator


# TODO : Comment Scroll Setup and Continue
# TODO : Submission Scroll ^

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
        self.reddit = None
        self.feeds = {}

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Test Reddit Cog credentials and config. """
        lg.getLogger().debug('on_ready reddit init fired.')
        await self.bot.wait_until_ready()
        if self.reddit is None:
            await self.reddit_init()

    # Processes

    @disextt.loop(seconds=1.0)
    async def feed_processing(self) -> None:
        """This processes all configured feeds."""
        pass

    @disextt.loop(seconds=10.0)
    async def reddit_processes(self) -> None:
        """ Reddit's Automated Processes. """
        # lg.getLogger().debug(
        #    f'Reddit Tick: {repr(self.reddit_processes.loop)}')
        pass

    # Helpers

    @staticmethod
    async def credential_check() -> bool:
        """ Check Reddit config for bot. """
        return True if 'REDDIT_USER_AGENT' in os.environ and \
                       'REDDIT_CLIENT_ID' in os.environ and \
                       'REDDIT_CLIENT_SECRET' in os.environ and \
                       'REDDIT_USERNAME' in os.environ and \
                       'REDDIT_PASSWORD' in os.environ else False

    async def reddit_init(self) -> None:
        """ Init and attach Reddit API. """
        txt_no_creds = \
            'Reddit credentials not setup, Reddit functions disabled.'
        txt_login_failed = \
            'Unable to log into reddit: {}. Reboot to try again.'
        txt_logged_in = 'Logged into reddit.'

        # Fetch Owner
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = appinfo.owner

        # This fires if the bot can't find the credentials in env.
        if not await self.credential_check():
            lg.getLogger().info(txt_no_creds)
            pag_msg = await constants.paginate(txt_no_creds)
            if owner is not None:
                await constants.send_paginator(owner, pag_msg)
            self.reddit_processes.stop()
            return

        # This is if the bot does find the creds.
        try:
            self.reddit = prw.Reddit(
                user_agent=os.environ['REDDIT_USER_AGENT'],
                client_id=os.environ['REDDIT_CLIENT_ID'],
                client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                username=os.environ['REDDIT_USERNAME'],
                password=os.environ['REDDIT_PASSWORD']
            )
        except Exception as e:
            lg.getLogger().info(txt_login_failed.format(e.args))
            pag_msg = await constants.paginate(txt_login_failed)
            await constants.send_paginator(owner, pag_msg)
            return

        # Success!
        lg.getLogger().info(txt_logged_in)

    # Reddit Group Commands

    @disextc.group(name='red', hidden=True)
    @disextc.is_owner()
    async def reddit_group(self, ctx: disextc.Context):
        """ Grouping for the reddit cog commands. """
        if ctx.invoked_subcommand is None:
            await ctx.send('No subcommand given.')

    @reddit_group.command(name='daemon', hidden=True)
    @disextc.is_owner()
    async def daemon_toggle_command(
            self, ctx: disextc.Context, on: typ.Optional[bool]) -> None:
        """ Toggle Process Status.

        Without bool -> status given
        with bool -> set status

        :param ctx -> Invocation Context
        :param on -> Bool with desired state of running.
        :return None
        """
        if on is None:
            running_status = 'The reddit daemon is currenty '
            if self.reddit_processes.is_being_cancelled():
                running_status += 'is being canceled.'
            else:
                running_status += \
                    f'running. Next in' + \
                    f' :{self.reddit_processes.next_iteration}' \
                    if self.reddit_processes.next_iteration is not None \
                    else 'stopped.'
            pag = await constants.paginate(running_status)
            await constants.send_paginator(ctx, pag)
        else:
            if self.reddit_processes.is_being_cancelled():
                await ctx.send('Currently cancelling...')
            elif self.reddit_processes.loop.is_running():
                if on:
                    await ctx.send(f'Reddit processes starting.')
                    self.reddit_processes.start()
                else:
                    await ctx.send(f'Reddit processes stopping.')
                    self.reddit_processes.stop()

    @reddit_group.command(name='id', hidden=True)
    @disextc.is_owner()
    async def get_profile_command(self, ctx: disextc.Context, redditor: str):
        """ This retrieves a redditor's profile. """
        result: prw.reddit.models.Redditor = self.reddit.redditor(redditor)
        if result is None:
            await ctx.send(f'Could not find redditor: {redditor}')
        else:
            await constants.send_paginator(
                ctx, await constants.paginate(
                    f'{repr(result)} created:{result.created_utc} ' +
                    f'link karma: {result.link_karma} ' +
                    f'post karma: {result.comment_karma}'))

    # Feed Group Commands

    @reddit_group.group()
    @disextc.is_owner()
    async def feed_group(self, ctx: disextc.Context):
        """Grouping for reddit feed related commands. """

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

        # TODO: Turn this into a check
        # No reddit, no execute.
        if self.reddit is None:
            lg.getLogger().debug('Reddit function used without reddit init.')
            return

        # Warn user for delay
        # TODO: Move this to personality.
        await ctx.send('This may take a moment...')

        # fetch subreddit and moderators, and define the actions we care about.
        wh = self.reddit.subreddit('WiiHacks')
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

        # Populate dictionary with results, as well as pull actions and actors
        for log in wh.mod.log(limit=over):

            # Filter
            # TODO: Make this variable/configurable?
            if log._mod not in mods or log.action not in metered_actions.keys():
                continue

            # save Oldest
            if oldest is None:
                oldest = log.created_utc
            elif log.created_utc < oldest:
                oldest = log.created_utc

            # If mod isn't present, record them.
            if log._mod not in data:
                data[log._mod] = {}

            # New action for mod.
            if log.action not in data[log._mod]:
                data[log._mod][log.action] = 1

            # Increment (If you've reached here we have both mod + action)
            data[log._mod][log.action] += 1

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
        await ctx.send(f"""```
{table}
Oldest Log Entry: {str(datetime.datetime.fromtimestamp(oldest))}
```""")


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Reddit(bot))
