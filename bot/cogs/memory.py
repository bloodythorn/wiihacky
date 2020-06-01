import aioredis
import asyncio
import aiomysql
import discord
import discord.ext.commands as disextc
import logging as lg
import os
import typing as typ
# TODO: Get rid of these
from constants import paginate, send_paginator

# TODO: Make SQL Console Channel
# TODO: Clean up what you have
# TODO: Implement redis

log = lg.getLogger(__name__)

redis_db_scratch = 0
redis_db_config = 1

redis_databases = {redis_db_scratch, redis_db_config}


class Memory(disextc.Cog):
    """ Bot Memory

    This module handles permanent or cached storage.

    The following env keys need to be set for a mysql db connection:

    SQL_HOST_NAME
    SQL_PORT_NUMBER
    SQL_USER_NAME
    SQL_PASSWORD
    SQL_DB_NAME

    The following env keys need to be set for a Redis connection:

    REDIS_HOST
    REDIS_PASSWORD -> not currently implemented

    If they are not set, or the bot cannot connect to the db, db functionality
    will be disabled.

    Currently MySQL isn't used for anything, but Redis will be for
    configuration storage.
    """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        """ DB Check at startup.

        This makes sure the db credentials are set and the bot can connect
        to each configured database.
        """
        # txt/constants
        txt_on_ready_db_event = 'on_ready memory db init fired.'
        txt_no_mysql_creds = \
            'MYSQL Database credentials not setup, DB functions disabled.'

        # Wait until ready
        await self.bot.wait_until_ready()
        log.debug(txt_on_ready_db_event)

        # Grab the owner
        appinfo: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = appinfo.owner

        # TODO: Move these to their own functions. Maybe do them Async
        # MySQL
        # Check credentials in env
        if not await self.mysql_credential_check():
            log.info(txt_no_mysql_creds)
            pag = await paginate(txt_no_mysql_creds)
            if owner is not None:
                await send_paginator(owner, pag)
            # Check connection to DB
            if not await self.mysql_connection_check():
                # TODO: Better failure reason given for troubleshooting purposes
                sql_could_not_connect = \
                    'Could not connect with MYSQL creds given.'
                log.info(sql_could_not_connect)
                pag = await paginate(sql_could_not_connect)
                if owner is not None:
                    await send_paginator(owner, pag)

        # Redis
        txt_no_redis_creds = "Redis creds not setup in env, redis disabled."
        if not await self.redis_credentials_check():
            log.info(txt_no_redis_creds)
            pag = await paginate(txt_no_redis_creds)
            if owner is not None:
                await send_paginator(owner, pag)
            if not await self.redis_connection_check():
                redis_could_not_connect = \
                    "Could not connect with Redis creds given."
                log.info(redis_could_not_connect)
                pag = await paginate(redis_could_not_connect)
                if owner is not None:
                    await send_paginator(owner, pag)

    # Helpers

    @staticmethod
    async def mysql_connection_check() -> bool:
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
        except:
            return False

    @staticmethod
    async def mysql_credential_check() -> bool:
        """ Check MYSQL DB config for bot. """
        return all([
            'SQL_HOST_NAME' in os.environ,
            'SQL_PORT_NUMBER' in os.environ,
            'SQL_USER_NAME' in os.environ,
            'SQL_PASSWORD' in os.environ,
            'SQL_DB_NAME' in os.environ
        ])

    @staticmethod
    async def get_mysql_db_connection() -> typ.Optional[aiomysql.Connection]:
        """ Get the db connection. """
        log.debug('SQL Connection Requested.')
        if Memory.mysql_credential_check:
            return await aiomysql.connect(
                    host=os.environ['SQL_HOST_NAME'],
                    port=int(os.environ['SQL_PORT_NUMBER']),
                    user=os.environ['SQL_USER_NAME'],
                    password=os.environ['SQL_PASSWORD'],
                    db=os.environ['SQL_DB_NAME'],
                    loop=asyncio.get_event_loop())
        else:
            raise Exception("SQL Connection request failed.")

    @staticmethod
    async def redis_connection_check() -> bool:
        """ Check Redis DB Config for the bot. """
        test_key = 'test'
        test_value = 'value'
        redis = await aioredis.create_redis_pool(
            f"redis://{os.environ['REDIS_HOST']}")
        await redis.set(test_key, test_value)
        value = await redis.get(test_key, encoding='utf-8')
        await redis.delete(test_key)
        redis.close()
        await redis.wait_closed()
        log.debug(f'redis connection check results: {test_value}=={value}')
        return value == test_value

    @staticmethod
    async def redis_credentials_check() -> bool:
        """ Check to confirm Redis DB env variables. """
        return all([
            'REDIS_HOST' in os.environ,
            'REDIS_PASSWORD' in os.environ
        ])

    @staticmethod
    async def get_redis_pool(database: int):
        return await aioredis.create_redis_pool(
            f"redis://{os.environ['REDIS_HOST']}/{database}")

    # Memory Group Commands

    @disextc.group(name='mem', hidden=True)
    @disextc.is_owner()
    async def memory_group(self, ctx: disextc.Context) -> None:
        """ Memory command grouping. """
        # TODO: This should bring up something if invoked commandless.
        if ctx.invoked_subcommand is None:
            await ctx.send('no subcommand given for memory group.')

    # SQL Group Commands

    @memory_group.group(name='sql', hidden=True)
    @disextc.is_owner()
    async def sql_group(self, ctx: disextc.Context) -> None:
        """SQL Command Group. """
        if ctx.invoked_subcommand is None:
            await ctx.send('No sql subcommand given.')

    @sql_group.command(name='sql', hidden=True)
    @disextc.is_owner()
    async def sql_cli_command(self, ctx: disextc.Context, *, arg: str) -> None:
        """ Execute SQL """
        try:
            conn = await self.get_mysql_db_connection()
            cur = await conn.cursor()
            await cur.execute(arg)
            output = await cur.fetchone()
            await send_paginator(ctx, await paginate(f'Output: {str(output)}'))
            await cur.close()
            conn.close()
        except Exception as e:
            await ctx.send(f'SQL Raised exception : {e.args}')

    # Redis Group Commands

    @memory_group.group(name='red', hidden=True)
    @disextc.is_owner()
    async def redis_group(self, ctx: disextc.Context):
        """Redis Command Group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No redis subcommand given.")

    @redis_group.command(name='redis', hidden=True)
    @disextc.is_owner()
    async def redis_cli_command(
            self, ctx: disextc.Context, *, arg: str) -> None:
        # TODO: Implement, document
        await ctx.send(f'{await self.redis_connection_check()} {arg}')


def setup(bot: disextc.Bot) -> None:
    """ Loads memory cog. """
    bot.add_cog(Memory(bot))
