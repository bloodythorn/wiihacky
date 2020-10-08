import aioredis
import discord.ext.commands as disextc
import logging as lg
import os

log = lg.getLogger(__name__)

# txt/constants
redis_db_scratch = 0
redis_db_config = 1
redis_databases = {redis_db_scratch, redis_db_config}
txt_on_ready_db_event = 'on_ready memory db init fired.'
redis_uri = 'redis://{}'


async def redis_connection_check() -> bool:
    """ Determine if the bot is able to connect to the Redis server.
    """
    test_key = 'key'
    test_value = 'value'

    try:
        redis = await aioredis.create_redis_pool(
            redis_uri.format(os.environ['REDIS_HOST']))
        await redis.set(test_key, test_value)
        value = await redis.get(test_key, encoding='utf-8')
        await redis.delete(test_key)
        redis.close()
        await redis.wait_closed()
        log.debug(f'redis connection check results: {test_value==value}')
        return value == test_value
    except Exception as e:
        log.debug(f'Failure connecting to redis db: {e}')
        return False


async def redis_credentials_check() -> bool:
    """ Determines if the conditions are set for the bot to be able to connect
    to the redis server.
    """
    # TODO: Redis needs to be more secure.
    return all([
        'REDIS_HOST' in os.environ,
    ])


async def test_database_connections() -> bool:
    """ This is all the above tests in a single sequence.
    """
    check = all([
        await redis_credentials_check(),
        await redis_connection_check()])
    log.debug(f'DB full test result: {check}')
    return check


class Memory(disextc.Cog):
    # TODO: This needs to be redone
    """ Bot Memory

        Handler for redis interaction

        Currently to work you need:

        # Redis:
        REDIS_HOST='localhost'

        Changed to match the information for your DB.

    """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self):
        # TODO: Description needs to be redone
        """ DB Check at startup.

        This makes sure the db credentials are set and the bot can connect
        to each configured database.
        """

        # Wait until ready
        await self.bot.wait_until_ready()
        log.debug(txt_on_ready_db_event)

        system = self.bot.get_cog('System')
        if system is None:
            txt_no_system_cog = 'System cog unable to be retrieved.'
            log.error(txt_no_system_cog)
        if not await test_database_connections():
            log.debug('db check failed.')

    # Helpers

    @staticmethod
    async def redis_connection_check() -> bool:
        """ Check Redis DB Config for the bot. """
        test_key = 'key'
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
    async def get_redis_pool(database: int):
        return await aioredis.create_redis_pool(
            f"redis://{os.environ['REDIS_HOST']}", db=database)

    @staticmethod
    async def redis_get(key: str, database: int = 0) -> str:
        rd = await aioredis.create_redis_pool(
            f"redis://{os.environ['REDIS_HOST']}", db=database)
        output = await rd.get(key)
        await rd.close()
        await rd.wait_closed()
        return output

    @staticmethod
    async def redis_set(key: str, value: str, database: int = 0) -> None:
        rd = await aioredis.create_redis_pool(
            f"redis://{os.environ['REDIS_HOST']}", db=database)
        rt = await rd.set(key, value)
        await rd.close()
        await rd.wait_closed()
        return rt

    @staticmethod
    async def redis_del(key: str, database: int = 0) -> None:
        rd = await aioredis.create_redis_pool(
            f"redis://{os.environ['REDIS_HOST']}", db=database)
        rt = await rd.delete(key)
        await rd.close()
        await rd.wait_closed()
        return rt

    # Memory Group Commands

    @disextc.group(name='mem', hidden=True)
    @disextc.is_owner()
    async def memory_group(self, ctx: disextc.Context) -> None:
        """ Memory command grouping. """
        # TODO: This should bring up something if invoked commandless.
        if ctx.invoked_subcommand is None:
            await ctx.send('no subcommand given for memory group.')

    # Redis Group Commands

    @memory_group.group(name='red', hidden=True)
    @disextc.is_owner()
    async def redis_group(self, ctx: disextc.Context):
        """Redis Command Group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No redis subcommand given.")

    @redis_group.command(name='crd', hidden=True)
    @disextc.is_owner()
    async def redis_credentials_check_command(self, ctx: disextc.Context):
        if await redis_credentials_check():
            await ctx.send(f'Redis credentials have been set.')
        else:
            await ctx.send(f'Redis credentials are NOT set!')

    @redis_group.command(name='con', hidden=True)
    @disextc.is_owner()
    async def redis_connection_check_command(self, ctx: disextc.Context):
        if await redis_connection_check():
            await ctx.send(f'Connection to Redis DB established.')
        else:
            await ctx.send(
                f'Unable to connect to Redis. Check log for details.')


def setup(bot: disextc.Bot) -> None:
    """ Loads memory cog. """
    bot.add_cog(Memory(bot))
