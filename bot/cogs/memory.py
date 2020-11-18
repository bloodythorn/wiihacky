import aioredis
import discord.ext.commands as disextc
import logging as lg
import os

import bot.constants as const
import bot.data as data

from contextlib import asynccontextmanager
from datetime import datetime
from sqlalchemy import create_engine

__version__ = '0.0.2'
log = lg.getLogger(__name__)

txt_testing_redis = """redis crd|con: %s/%s"""
txt_testing_sql = """psql  crd|con: %s/%s"""
def_enc = 'utf-8'


# External Helpers

async def redis_credentials_check() -> bool:
    """ Determines if the conditions are set for the bot to be able to connect
        to the redis server.
    """
    # TODO: Redis needs to be more secure.
    return all([
        'REDIS_HOST' in os.environ,
    ])


async def redis_connection_check() -> bool:
    """ Determine if the bot is able to connect to the Redis server.
    """
    test_key = 'key'
    test_value = 'value'
    redis = redis = await aioredis.create_redis_pool(
        const.redis_uri.format(
            os.environ['REDIS_HOST'], const.redis_config_db))
    await redis.set(test_key, test_value)
    value = await redis.get(test_key, encoding='utf-8')
    await redis.delete(test_key)
    log.debug(f'redis connection check results: {test_value==value}')
    redis.close()
    await redis.wait_closed()
    return test_value == value


async def psql_credentials_check() -> bool:
    """ Determine if credentials have been set.
    """
    return all([
        'PSQL_USER' in os.environ,
        'PSQL_PSSW' in os.environ,
        'PSQL_HOST' in os.environ,
        'PSQL_DB' in os.environ,
    ])


async def psql_connection_check(engine) -> bool:
    """ PSQL Connection check.
    """
    log.debug(f'psql connection check fired.')
    try:
        engine.connect()
    except Exception as e:
        log.debug(f'sql Connection fail: {e}')
        return False
    log.debug(f'psql connection check succeeded.')
    return True


@asynccontextmanager
async def redis_scope(db_number):
    """ Context for redis use.
    """
    redis = await aioredis.create_redis_pool(
        const.redis_uri.format(
            os.environ['REDIS_HOST'], db_number))
    try:
        yield redis
    except Exception as e:
        log.error(f"Exception trying to access Redis: {e}")
        redis.close()
        await redis.wait_closed()
        raise e
    else:
        redis.close()
        await redis.wait_closed()


class Memory(disextc.Cog):
    """ Bot Memory

        Handler for redis interaction, as well as the starting point for sql.

        Currently to work you need:

        # Redis:
        REDIS_HOST='localhost'

        # PostgreSQL
        PSQL_HOST='hostname'
        PSQL_USER='username'
        PSQL_PSSW='password'
        PSQL_DB='database'

        Changed to match the information for your DB.
    """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self._engine = None

    # Listeners

    @disextc.Cog.listener()
    async def on_ready(self) -> None:
        """ DB Check at startup.

            This makes sure the db credentials are set and the bot can connect
            to each configured database.

            It also will create the engine to be used to connect to the psqldb.

        """
        # Function Constants/Text
        txt_mem_on_ready = 'Memory on ready fired.'

        # Wait until ready
        await self.bot.wait_until_ready()
        log.debug(txt_mem_on_ready)

    # Properties

    @property
    async def engine(self):
        txt_psql_create_engine = 'Attempting to create PSQL Engine'
        txt_psql_crd_error = 'PSQL credentials are not set.'
        txt_psql_engine_ready = 'Successfully created PSQL db engine.'
        if self._engine is None:
            log.debug(txt_psql_create_engine)
            try:
                self._engine = create_engine(const.psql_uri.format(
                    os.environ['PSQL_USER'],
                    os.environ['PSQL_PSSW'],
                    os.environ['PSQL_HOST'],
                    os.environ['PSQL_DB']))
            except KeyError:
                log.error(txt_psql_crd_error)
            log.debug(txt_psql_engine_ready)
        return self._engine

    # Helpers

    async def redis_result(self, ctx, com, result) -> None:
        """ Helper function to convert 0/1 of return result to verbal.
        """
        if result == 0:
            await ctx.send(f"'{com}' operation failed.")
        else:
            await ctx.send(f"'{com}' operation successful.")

    # Hash Functions

    # Memory Group Commands

    @disextc.group(name='mem', hidden=True)
    @disextc.is_owner()
    async def memory_group(self, ctx: disextc.Context) -> None:
        """ Memory command grouping. """
        if ctx.invoked_subcommand is None:
            txt_testing_db = txt_testing_redis % (
                await redis_credentials_check(),
                await redis_connection_check())
            txt_testing_db += "\n" + txt_testing_sql % (
                await psql_credentials_check(),
                await psql_connection_check(await self.engine))
            await ctx.send(txt_testing_db)

    # Redis Group Commands

    @memory_group.group(name='red', hidden=True)
    @disextc.is_owner()
    async def redis_group(self, ctx: disextc.Context):
        """Redis command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_testing_redis % (
                await redis_credentials_check(),
                await redis_connection_check()))

    @redis_group.command(name='crd', hidden=True)
    @disextc.is_owner()
    async def redis_credentials_check_command(
        self,
        ctx: disextc.Context
    ) -> None:
        """ Check Redis credentials.
        """
        try:
            if await redis_credentials_check():
                await ctx.send(f'Redis credentials have been set.')
            else:
                await ctx.send(f'Redis credentials are NOT set!')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='con', hidden=True)
    @disextc.is_owner()
    async def redis_connection_check_command(
        self,
        ctx: disextc.Context
    ) -> None:
        """ Check Redis connection.
        """
        try:
            if await redis_connection_check():
                await ctx.send(f'Connection to Redis DB established.')
            else:
                await ctx.send(
                    f'Unable to connect to Redis. Check log for details.')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='set', hidden=True)
    @disextc.is_owner()
    async def redis_set_command(
        self,
        ctx: disextc.Context,
        key: str,
        value: str,
    ) -> None:
        """ Set Redis key to given string value.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.set(key, value)
            await self.redis_result(ctx, 'set', result)
            await ctx.send(f'Key {key} set to {value}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='get', hidden=True)
    @disextc.is_owner()
    async def redis_get_command(self, ctx: disextc.Context, key: str) -> None:
        """ Retrieve key from Redis db
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.get(key, encoding=def_enc)
            await ctx.send("Key %s retrieved as '%s'" % (key, result))
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='del', hidden=True)
    @disextc.is_owner()
    async def redis_del_command(self, ctx: disextc.Context, key: str) -> None:
        """ Deletes a key from the Redis db
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.delete(key)
            await self.redis_result(ctx, 'delete', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='exi', hidden=True)
    @disextc.is_owner()
    async def redis_exists_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Checks to see if a key exists in Redis.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.exists(key)
            await self.redis_result(ctx, 'exists', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='exp', hidden=True)
    @disextc.is_owner()
    async def redis_expire_command(
        self,
        ctx: disextc.Context,
        key: str,
        seconds: int
    ) -> None:
        """ Set the key to expire in the given seconds.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.expire(key, seconds)
            await self.redis_result(ctx, 'expire', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='exa', hidden=True)
    @disextc.is_owner()
    async def redis_expireat_command(
        self,
        ctx: disextc.Context,
        key: str,
        when: str
    ) -> None:
        """ Set the key to expire at the given timestamp.
        """
        try:
            timestamp = datetime.fromisoformat(when)
            # Set the expire time
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.expireat(key, timestamp.timestamp())
            await self.redis_result(ctx, 'expireat', result)
        except ValueError:
            await ctx.send(
                f'Could not convert {when} from iso format to timestamp.')
            return
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    # TODO: see if you can make an optional value to increment by
    @redis_group.command(name='inc', hidden=True)
    @disextc.is_owner()
    async def redis_increment_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Incremented given key by one, assuming an integer value.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.incr(key)
            await self.redis_result(ctx, 'increment', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='key', hidden=True)
    @disextc.is_owner()
    async def redis_keys_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Find set of keys that fit pattern.
        """
        try:
            items = None
            async with redis_scope(const.redis_config_db) as redis:
                items = await redis.keys(key, encoding=def_enc)
            await ctx.send(f'Keys found: {items}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='per', hidden=True)
    @disextc.is_owner()
    async def redis_persist_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Removes expiration from key.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.persist(key)
            await self.redis_result(ctx, 'persist', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='pex', hidden=True)
    @disextc.is_owner()
    async def redis_pexpire_command(
        self,
        ctx: disextc.Context,
        key: str,
        timestamp: int
    ) -> None:
        """ Sets expiration in milliseconds.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.pexpire(key, timestamp)
            await self.redis_result(ctx, 'pexpire', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='ttl', hidden=True)
    @disextc.is_owner()
    async def redis_ttl_command(
        self,
        ctx: disextc.Context,
        key: str,
    ) -> None:
        """ Shows time to live for a key..
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.ttl(key)
            await ctx.send(f'ttl:{result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='ptl', hidden=True)
    @disextc.is_owner()
    async def redis_pttl_command(
        self,
        ctx: disextc.Context,
        key: str,
    ) -> None:
        """ Shows time to live for a key in milliseconds.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.pttl(key)
            await ctx.send(f'ttl:{result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='ren', hidden=True)
    @disextc.is_owner()
    async def redis_rename_command(
        self,
        ctx: disextc.Context,
        key: str,
        new_key: str,
    ) -> None:
        """ Renames a key from one name, to another.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.rename(key, new_key)
            await self.redis_result(ctx, 'rename', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.command(name='rnx', hidden=True)
    @disextc.is_owner()
    async def redis_renamenx_command(
        self,
        ctx: disextc.Context,
        key: str,
        new_key: str,
    ) -> None:
        """ Renames key from one to another if key doesn't exist.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.renamenx(key, new_key)
            await self.redis_result(ctx, 'renamenx', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.group(name='lst')
    @disextc.is_owner()
    async def redis_list_group(self, ctx: disextc.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No subcommand given for lst')

    @redis_list_group.command(name='idx', hidden=True)
    @disextc.is_owner()
    async def redis_lindex_command(
        self,
        ctx: disextc.Context,
        key: str,
        index: int,
    ) -> None:
        """ Retrieves element from list by index.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.lindex(key, index, encoding=def_enc)
            await ctx.send(f'{key}:{index}:{result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    # TODO: TEST
    # FIXME: This is not working
    @redis_list_group.command(name='ins', hidden=True)
    @disextc.is_owner()
    async def redis_linsert_command(
        self,
        ctx: disextc.Context,
        key: str,
        pivot: int,
        value: str,
        before=False
    ) -> None:
        """ Inserts value at given index, before or after.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.linsert(key, pivot, value, before)
            await self.redis_result(ctx, 'linsert', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='len', hidden=True)
    @disextc.is_owner()
    async def redis_llen_command(self, ctx: disextc.Context, key: str) -> None:
        """ Returns the length of the given key.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.llen(key)
            await ctx.send(f'{key}:{result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='lpo', hidden=True)
    @disextc.is_owner()
    async def redis_lpop_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Returns leftmost element and removes it.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.lpop(key, encoding=def_enc)
            await ctx.send(f'{key}:{result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='lpu', hidden=True)
    @disextc.is_owner()
    async def redis_lpush_command(
        self,
        ctx: disextc.Context,
        key: str, value: str
    ) -> None:
        """ Pushes element to the left side of the array.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.lpush(key, value)
            await self.redis_result(ctx, 'lpush', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='lpx', hidden=True)
    @disextc.is_owner()
    async def redis_lpushx_command(
        self,
        ctx: disextc.Context,
        key: str, value: str
    ) -> None:
        """ Pushes element to the left side of the array. Only if key exists
            and holds a list.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.lpushx(key, value)
            await self.redis_result(ctx, 'lpush', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='rng', hidden=True)
    @disextc.is_owner()
    async def redis_lrange_command(
        self,
        ctx: disextc.Context,
        key: str, start: int, stop: int,
    ) -> None:
        """ Returns a list of elements of a given range.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.lrange(key, start, stop, encoding=def_enc)
            await ctx.send(f'{key}[{start}:{stop}]={result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='rem', hidden=True)
    @disextc.is_owner()
    async def redis_lrem_command(
        self,
        ctx: disextc.Context,
        key: str,
        count: int,
        value: str
    ) -> None:
        """ Removes the first count occurrences of elements equal to the value.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.lrem(key, count, value)
            await self.redis_result(ctx, 'lrem', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='set', hidden=True)
    @disextc.is_owner()
    async def redis_lset_command(
        self,
        ctx: disextc.Context,
        key: str, index: int, value: str
    ) -> None:
        """ Sets the list element at the index to value.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.lset(key, index, value)
            await self.redis_result(ctx, 'lset', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='trm', hidden=True)
    @disextc.is_owner()
    async def redis_ltrim_command(
        self,
        ctx: disextc.Context,
        key: str, start: int, stop: int
    ) -> None:
        """ Trims list to a given range.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.ltrim(key, start, stop)
            await self.redis_result(ctx, 'ltrim', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='rpo', hidden=True)
    @disextc.is_owner()
    async def redis_rpop_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Returns and removes element from right side of array.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.rpop(key, encoding=def_enc)
            await ctx.send(f'{key}:rpo={result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='rpu', hidden=True)
    @disextc.is_owner()
    async def redis_rpush_command(
        self,
        ctx: disextc.Context,
        key: str, value: str
    ) -> None:
        """ Pushes value to right side of key.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.rpush(key, value)
            await self.redis_result(ctx, 'rpush', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_list_group.command(name='rpx', hidden=True)
    @disextc.is_owner()
    async def redis_rpushx_command(
        self,
        ctx: disextc.Context,
        key: str, value: str
    ) -> None:
        """ Pushes value to right side of key only if it exists and holds
            a list.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.rpushx(key, value)
            await self.redis_result(ctx, 'rpushx', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_group.group(name='hsh')
    @disextc.is_owner()
    async def redis_hash_group(self, ctx: disextc.Context) -> None:
        """ Group for redis hash commands.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No sub command given for hsh subgroup')

    # TODO: TEST
    @redis_hash_group.command(name='del')
    @disextc.is_owner()
    async def redis_hdel_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str
    ) -> None:
        """ Delete one hash field.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hdel(key, field)
            await self.redis_result(ctx, 'hdel', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='exi')
    @disextc.is_owner()
    async def redis_hexists_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str
    ) -> None:
        """ Determine if hash field exists.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hexists(key, field)
            await self.redis_result(ctx, 'hexists', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='get')
    @disextc.is_owner()
    async def redis_hget_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str
    ) -> None:
        """ Get the value of a hash field.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hget(key, field, encoding=def_enc)
            await ctx.send(
                'Key %s:%s retrieved as %s' % (key, field, result))
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='gal')
    @disextc.is_owner()
    async def redis_hgetall_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Get all the fields and values in a hash.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hgetall(key, encoding=def_enc)
                await ctx.send(f'Key {key} retrieved: {result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='inb')
    @disextc.is_owner()
    async def redis_hincrby_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str,
        incr: int = 1
    ) -> None:
        """ Increment the integer value of a hash field by the given number
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hincrby(key, field, incr)
                await self.redis_result(ctx, 'hincrby', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='inf')
    @disextc.is_owner()
    async def redis_hincby_float_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str,
        incr: float = 1.0
    ) -> None:
        """ Increment the float value of a hash field by the given number.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hincrbyfloat(key, field, incr)
                await self.redis_result(ctx, 'hincrby', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='key')
    @disextc.is_owner()
    async def redis_hkeys_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Get all the fields in a hash.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hkeys(key, encoding=def_enc)
                await ctx.send(f'Keys {key} retrieved: {result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='len')
    @disextc.is_owner()
    async def redis_hlen_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Get the number of fields in a hash.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hlen(key)
                await ctx.send(f'Keys {key} length retrieved: {result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='set')
    @disextc.is_owner()
    async def redis_hset_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str,
        value: str
    ) -> None:
        """ Set the string value of a hash field.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hset(key, field, value)
                await self.redis_result(ctx, 'hset', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='stx')
    @disextc.is_owner()
    async def redis_hsetnx_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str,
        value: str
    ) -> None:
        """ Set the value of a hash field, only if the field does not exist.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hsetnx(key, field, value)
                await self.redis_result(ctx, 'hsetnx', result)
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @redis_hash_group.command(name='sln')
    @disextc.is_owner()
    async def redis_hstrlen_command(
        self,
        ctx: disextc.Context,
        key: str,
        field: str
    ) -> None:
        """ Get the length of the value of a hash field.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hstrlen(key, field)
                await ctx.send(
                    f'Keys value {key}:{field} length retrieved: {result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    # TODO: TEST
    @redis_hash_group.command(name='val')
    @disextc.is_owner()
    async def redis_hvals_command(
        self,
        ctx: disextc.Context,
        key: str
    ) -> None:
        """ Get all the values in a hash.
        """
        try:
            result = None
            async with redis_scope(const.redis_config_db) as redis:
                result = await redis.hvals(key, encoding=def_enc)
                await ctx.send(
                    f'Values for key {key}: {result}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    # PSQL Group Commands

    @memory_group.group(name='sql', hidden=True)
    @disextc.is_owner()
    async def psql_group(self, ctx: disextc.Context) -> None:
        """ PostreSQL command group.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_testing_sql % (
                await psql_credentials_check(),
                await psql_connection_check(await self.engine)))

    @psql_group.command(name='crd', hidden=True)
    @disextc.is_owner()
    async def psql_credentials_check(self, ctx: disextc.Context) -> None:
        """ Checks PostgreSQL credentials
        """
        try:
            if await psql_credentials_check():
                await ctx.send(f'PostreSQL credentials have been set.')
            else:
                await ctx.send(f'PostreSQL credentials are NOT set!')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @psql_group.command(name='con', hidden=True)
    @disextc.is_owner()
    async def psql_connection_check(self, ctx: disextc.Context) -> None:
        """ Checks PostgreSQL connection.
        """
        try:
            if await psql_connection_check(await self.engine):
                await ctx.send(f'PostreSQL connection verified..')
            else:
                await ctx.send(f'Could not connect to PostgreSQL db!')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @psql_group.command(name='eng', hidden=True)
    @disextc.is_owner()
    async def psql_engine_check_command(self, ctx: disextc.Context) -> None:
        try:
            await ctx.send(f'Engine: {await self.engine}')
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @psql_group.command(name='ini', hidden=True)
    @disextc.is_owner()
    async def psql_database_initialize(self, ctx: disextc.Context) -> None:
        """ Creates the bot's sql database schema if it doesn't already exist.
            Otherwise it does nothing.
        """
        try:
            data.DataBase.metadata.create_all(bind=(await self.engine))
            await ctx.send("Database successfully created.")
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)

    @psql_group.command(name='rem', hidden=True)
    @disextc.is_owner()
    async def psql_database_remove(self, ctx: disextc.Context) -> None:
        """ Drops the entire bot's DB schema, use this with caution.
        """
        # TODO: This will need some form of security. Typing it by accident
        #   would suck
        try:
            data.DataBase.metadata.drop_all(bind=(await self.engine))
            await ctx.send("Database successfully dropped.")
        except Exception as e:
            error = f"Exception during operation: {e}"
            log.error(error)
            await ctx.send(error)


def setup(bot: disextc.Bot) -> None:
    """ Loads memory cog. """
    bot.add_cog(Memory(bot))
