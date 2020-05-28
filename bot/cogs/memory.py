import asyncio
import aiomysql
import discord
import discord.ext.commands as disextc
import logging as lg
import os
# TODO: Get rid of these
from constants import paginate, send_paginator

# TODO: Make SQL Console Channel


class Memory(disextc.Cog):
    """ Bot Memory

    This module handles DB connections. Currently only mysql is supported.

    The following env keys need to be set for a db connection:
    SQL_HOST_NAME
    SQL_PORT_NUMBER
    SQL_USER_NAME
    SQL_PASSWORD
    SQL_DB_NAME

    If they are not set, or the bot cannot connect to the db, db functionality
    will be disabled.
    """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ DB Check at startup.

        This makes sure the db credentials are set and the bot can connect.
        """
        # txt/constants
        txt_on_ready_db_event = 'on_ready memory db init fired.'
        txt_no_creds = \
            'Database credentials not setup, DB functions disabled.'

        lg.getLogger().debug(txt_on_ready_db_event)

        # Wait until ready
        await self.bot.wait_until_ready()

        # Grab the owner
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = appinfo.owner

        # Check credentials in env
        if not await self.credential_check():
            lg.getLogger().info(txt_no_creds)
            pag = await paginate(txt_no_creds)
            if owner is not None:
                await send_paginator(owner, pag)
            return
            # No reason to keep going.

        # Check connection to DB
        if not await self.db_connection_check():
            # TODO: Return connection error?
            could_not_connect = \
                'Could not connect with DB creds given.'
            lg.getLogger().info(could_not_connect)
            pag = await paginate(could_not_connect)
            if owner is not None:
                await send_paginator(owner, pag)

    # Helpers

    @staticmethod
    async def db_connection_check():
        """ Verify bot can connect to DB. """
        try:
            conn = await aiomysql.connect(
                host=os.environ['SQL_HOST_NAME'],
                port=int(os.environ['SQL_PORT_NUMBER']),
                user=os.environ['SQL_USER_NAME'],
                password=os.environ['SQL_PASSWORD'],
                db='mysql',
                loop=asyncio.get_event_loop())
            cur = await conn.cursor()
            await cur.execute("SELECT VERSION()")
            output = await cur.fetchall()
            await cur.close()
            conn.close()
            return True
        except Exception as e:
            return False

    @staticmethod
    async def credential_check() -> bool:
        """ Check DB config for bot. """
        return True if 'SQL_HOST_NAME' in os.environ and \
                       'SQL_PORT_NUMBER' in os.environ and \
                       'SQL_USER_NAME' in os.environ and \
                       'SQL_PASSWORD' in os.environ and \
                       'SQL_DB_NAME' in os.environ else False

    @staticmethod
    async def get_db_connection() -> aiomysql.Connection:
        """ Get the db connection. """
        lg.getLogger().debug('SQL Connection Requested.')
        return await aiomysql.connect(
                host=os.environ['SQL_HOST_NAME'],
                port=int(os.environ['SQL_PORT_NUMBER']),
                user=os.environ['SQL_USER_NAME'],
                password=os.environ['SQL_PASSWORD'],
                db=os.environ['SQL_DB_NAME'],
                loop=asyncio.get_event_loop())

    # Memory Group Commands

    @disextc.group(name='mem', hidden=True)
    @disextc.is_owner()
    async def memory(self, ctx: disextc.Context) -> None:
        """ Memory command grouping. """
        # TODO: This should bring up something if invoked commandless.
        if ctx.invoked_subcommand is None:
            await ctx.send('no subcommand given for memory group.')

    @memory.command(hidden=True)
    @disextc.is_owner()
    async def sql(self, ctx: disextc.Context, *, arg: str) -> None:
        """ Execute SQL """
        try:
            conn = await aiomysql.connect(
                host=os.environ['SQL_HOST_NAME'],
                port=int(os.environ['SQL_PORT_NUMBER']),
                user=os.environ['SQL_USER_NAME'],
                password=os.environ['SQL_PASSWORD'],
                db=os.environ['SQL_DB_NAME'],
                loop=asyncio.get_event_loop())
            cur = await conn.cursor()
            await cur.execute(arg)
            output = await cur.fetchone()
            await send_paginator(ctx, await paginate(f'Output: {str(output)}'))
            await cur.close()
            conn.close()
        except Exception as e:
            await ctx.send(f'SQL Raised exception : {e.args}')


def setup(bot: disextc.Bot) -> None:
    """ Loads memory cog. """
    bot.add_cog(Memory(bot))
