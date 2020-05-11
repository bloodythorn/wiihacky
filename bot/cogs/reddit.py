import constants
import discord
import discord.ext.commands as disextc
import discord.ext.tasks as disextt
import logging as lg
import os
import praw as prw
import typing as typ

# TODO : Comment Scroll Setup and Continue
# TODO : Submission Scroll ^


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
        # Start daemon.
        self.reddit_processes.start()
        self.setup_asked = False

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ Test Reddit Cog credentials and config. """
        lg.getLogger().debug('on_ready reddit init fired.')
        await self.bot.wait_until_ready()
        if self.reddit is None:
            await self.reddit_init()

    # Processes

    @disextt.loop(seconds=5.0)
    async def reddit_processes(self) -> None:
        """ Reddit's Automated Processes. """
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

    @disextc.group(name='red')
    @disextc.is_owner()
    async def reddit_group(self, ctx: disextc.Context):
        """ Grouping for the reddit cog commands. """
        if ctx.invoked_subcommand is None:
            await ctx.send('No subcommand given.')

    # TODO: Toggle doesn't turn it off, or it doesn't read that display that it
    #   it is off.
    @reddit_group.command(name='daemon')
    @disextc.is_owner()
    async def toggle_daemon(
            self, ctx: disextc.Context, on: typ.Optional[bool]) -> None:
        """ Toggle Process Status.

        Without bool -> status given
        with bool -> set status

        :param ctx -> Invocation Context
        :param on -> Bool with desired state of running.
        :return None
        """
        if on is None:
            running_status = 'The reddit daemon is currenty {}running'.format(
                    ('' if self.reddit_processes.loop.is_running() else 'not '))
            pag = await constants.paginate(running_status)
            await constants.send_paginator(ctx, pag)
        elif on:
            await ctx.send('Toggling reddit daemon on.')
        else:
            await ctx.send('Toggling reddit daemon off.')

    @reddit_group.command(name='id')
    @disextc.is_owner()
    async def get_profile_info(self, ctx: disextc.Context, redditor: str):
        """ This retrieves a redditor's profile. """
        result: prw.reddit.models.Redditor = self.reddit.redditor(redditor)
        if result is None:
            await ctx.send(f'Could not find redditor: {redditor}')
        else:
            await constants.send_paginator(
                ctx, await constants.paginate(
                    f'{repr(result)} created:{result.created_utc} link Karma: {result.link_karma} post karma: {result.comment_karma}'))


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Reddit(bot))
