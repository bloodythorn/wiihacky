import constants
import discord
import discord.ext.commands as disextc
import discord.ext.tasks as disextt
import logging as lg
import os
import praw as prw
import typing as typ


class Reddit(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self.reddit = None
        # Start daemon.
        self.reddit_processes.start()
        self.setup_asked = False

    # Processes

    @disextt.loop(seconds=5.0)
    async def reddit_processes(self) -> None:
        """ Reddit's Automated Processes. """
        await self.bot.wait_until_ready()
        # We only want the Connection Check reminder to happen once per boot
        if self.reddit is None and not self.setup_asked:
            self.setup_asked = True
            await self.reddit_init()
        # TODO : reddit init
        # TODO : Comment Scroll Setup and Continue
        # TODO : Submission Scroll ^

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
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = appinfo.owner
        # This fires if the bot can't find the credentials in env.
        if not await self.credential_check():
            no_creds = \
                'Reddit credentials not setup, Reddit functions disabled.'
            lg.getLogger().info(no_creds)
            pag_msg = await constants.paginate(no_creds)
            if owner is not None:
                await constants.send_paginator(owner, pag_msg)
            self.reddit_processes.stop()
            return
        try:
            # This is if the bot does find the creds.
            self.reddit = prw.Reddit(
                user_agent=os.environ['REDDIT_USER_AGENT'],
                client_id=os.environ['REDDIT_CLIENT_ID'],
                client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                username=os.environ['REDDIT_USERNAME'],
                password=os.environ['REDDIT_PASSWORD']
            )
        except Exception as e:
            login_failed = \
                f'Unable to log into reddit: {e.args}. Reboot to try again.'
            lg.getLogger().info(login_failed)
            pag_msg = await constants.paginate(login_failed)
            await constants.send_paginator(owner, pag_msg)
            return

        # Success!
        lg.getLogger().info('Logged into reddit.')

    # Groups

    @disextc.group(name='red')
    @disextc.is_owner()
    async def reddit_group(self, ctx: disextc.Context):
        """ Grouping for the reddit cog commands. """
        if ctx.invoked_subcommand is None:
            await ctx.send('No subcommand given.')

    # Commands

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
            running_status = 'The reddit daemon is currenty {} running'.format(
                    ('' if self.reddit_processes.loop.is_running() else 'not'))
            pag = await constants.paginate(running_status)
            await constants.send_paginator(ctx, pag)
        elif on:
            await ctx.send('Toggling reddit daemon on.')
        else:
            await ctx.send('Toggling reddit daemon off.')


def setup(bot: disextc.Bot) -> None:
    """ Loads reddit cog. """
    bot.add_cog(Reddit(bot))
