import aioredis
import asyncio
import dataclasses as dc
import discord
import discord.ext.commands as disextc
import discord.ext.tasks as disextt
import discord.utils as disutil
import logging as lg
import praw
import typing as typ
import re

import constants
import decorators

log = lg.getLogger(__name__)
index_key = 'registry_index'
user_prefix = 'user:'
snowflake_prefix = 'snowflake:'
reddit_prefix = 'reddit:'
redditor_role = 'Redditor'
username_regex = re.compile(r'^([^#]*)#([0-9]*)')
updown_vote_regex = re.compile(r'^(up|down)([_]?vote)?$')


@dc.dataclass()
class WiiHacksUser:
    """ Data class for community user. """
    snowflake_id: int
    utc_added: int
    registry_id: int
    reddit_name: str = ''
    verified: bool = False
    last_attempt_failed: bool = False
    last_status: str = ''
    last_status_since: int = 0
    last_online: int = 0
    deleted: bool = False
    up_votes: int = 0
    down_votes: int = 0


class Register(disextc.Cog):
    """
    This cog/module is responsible for registering users with the system,
    keeping track of their comings and goings, and associating their discord
    account with their reddit account.
    """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self.check_inbox_process.start()
        self.sync_users_process.start()

    def cog_unload(self):
        pass
        self.check_inbox_process.cancel()
        self.sync_users_process.cancel()

    # Checks

    @staticmethod
    def in_context(reaction: discord.Reaction, user: discord.User) -> bool:
        # TODO: Currently it's a free-for all. Refine this later maybe?
        # TODO: Context Considerations:
        #   reaction.message.author
        #   reaction.emoji.name
        #   user
        return True

    @staticmethod
    def is_up_vote(emoji: discord.Emoji) -> bool:
        if hasattr(emoji, 'name'):
            _result = re.match(updown_vote_regex, emoji.name)
            if _result is not None and _result.group(1).lower() == 'up':
                return True
        return False

    @staticmethod
    def is_down_vote(emoji: discord.Emoji) -> bool:
        if hasattr(emoji, 'name'):
            _result = re.match(updown_vote_regex, emoji.name)
            if _result is not None and _result.group(1).lower() == 'down':
                return True
        return False

    async def is_user(
            self,
            user: typ.Union[discord.User, discord.Member]) -> bool:
        """Is User

        Verifies if the user is contained in the DB

        :param user -> Discord user or member to verify
        :return True/False
        """
        redis: aioredis.Redis = await self.get_redis()
        cross_key = snowflake_prefix + str(user.id)
        result = None
        try:
            result = await redis.get(cross_key)
        finally:
            redis.close()
            await redis.wait_closed()
        return result is not None

    # Getters

    # TODO: This needs to change to the live DB when done.
    async def get_redis(self) -> aioredis.Redis:
        """ This will retrieve the redis for use.

        Make sure the redis is properly closed when used.
        redis.close()
        await redis.wait_closed()
        """
        # Grab the memory cog
        memory = self.bot.get_cog('Memory')
        if memory is None:
            raise RuntimeError('I have no memory.')

        # TODO: Change this to the live DB once you finish.
        from cogs.memory import redis_db_scratch
        return await memory.get_redis_pool(redis_db_scratch)

    async def get_next_index(self) -> int:
        """ Returns and reserves next index."""
        # If the index doesn't exist, create it.
        redis: aioredis.Redis = await self.get_redis()
        registry_id = await redis.incr(index_key)
        redis.close()
        await redis.wait_closed()
        return registry_id

    # User Read/Write

    async def user_read(
            self,
            user: typ.Union[discord.Member, discord.User]) -> WiiHacksUser:
        """Read user from redis.

        This will pull a wiihacks user from redis based on the discord user
        given. If the user doesn't exist, it will throw.
        :param user -> Discord user to retrieve
        :return WiiHacksUser containing record.
        """
        def str_to_bool(txt: str) -> bool:
            if txt == 'True':
                return True
            elif txt == 'False':
                return False
            else:
                return False
        redis: aioredis.Redis = await self.get_redis()
        cross_key = snowflake_prefix + str(user.id)
        record_key = await redis.get(cross_key)
        if not record_key:
            raise RuntimeError(
                f'User not found {user.name}:{user.id}')
        record = await redis.hgetall(record_key, encoding='utf-8')
        redis.close()
        await redis.wait_closed()
        return WiiHacksUser(
            snowflake_id=int(record['snowflake_id']),
            utc_added=int(record['utc_added']),
            registry_id=int(record['registry_id']),
            reddit_name=record['reddit_name'],
            verified=str_to_bool(record['verified']),
            last_attempt_failed=str_to_bool(record['last_attempt_failed']),
            last_status=record['last_status'],
            last_status_since=int(record['last_status_since']),
            last_online=int(record['last_online']),
            deleted=str_to_bool(record['deleted']),
            up_votes=int(record['up_votes']),
            down_votes=int(record['down_votes']))

    async def user_write(self, whu: WiiHacksUser) -> None:
        """Write user to redis

        Given a WiiHacksUser, this will write it to the DB. This is an
        indiscriminate destructive write and should only be used by functions
        that do proper checks first.
        :param whu -> WiiHacks user record to insert.
        :return None
        """
        redis = await self.get_redis()
        cross_key = snowflake_prefix + str(whu.snowflake_id)
        record_key = user_prefix + str(whu.registry_id)
        await redis.hmset_dict(
            record_key,
            snowflake_id=whu.snowflake_id,
            utc_added=whu.utc_added,
            registry_id=whu.registry_id,
            reddit_name=whu.reddit_name,
            verified=str(whu.verified),
            last_attempt_failed=str(whu.last_attempt_failed),
            last_status=whu.last_status,
            last_status_since=whu.last_status_since,
            last_online=whu.last_online,
            deleted=str(whu.deleted),
            up_votes=whu.up_votes,
            down_votes=whu.down_votes)
        await redis.set(cross_key, record_key)
        redis.close()
        await redis.wait_closed()

    # Helpers

    async def set_reddit_key(self, whu: WiiHacksUser, remove=False):
        """ Set user's reddit key for quick lookup. """
        redis = await self.get_redis()
        try:
            reddit_key = reddit_prefix + whu.reddit_name
            if remove:
                await redis.delete(reddit_key)
            else:
                record_key = user_prefix + str(whu.registry_id)
                await redis.set(reddit_key, record_key)
        except Exception as e:
            log.error(f'Could not set/remove reddit_key for {whu}|{e.args}')
        finally:
            redis.close()
            await redis.wait_closed()

    async def get_reddit(self) -> praw.Reddit:
        reddit_cog = self.bot.get_cog('Reddit')
        if not reddit_cog:
            raise RuntimeError(f'Could not retrieve reddit cog.')
        reddit = await reddit_cog.reddit
        return reddit

    async def add_user(self, user: discord.Member) -> None:
        """ Adds a user to the registry. """
        log.debug(f'add_user fired: {user}')

        if await self.is_user(user):
            raise RuntimeError(
                f'User is already registered in DB.')

        # Create new user
        from datetime import datetime
        whu = WiiHacksUser(
            snowflake_id=user.id,
            utc_added=int(datetime.utcnow().timestamp()),
            registry_id=await self.get_next_index())

        # Okay good to record
        await self.user_write(whu)
        log.debug(f'add_user succeeded: {whu}')

    async def sync_users(self) -> typ.Tuple[int, float]:
        """ Reads current users and syncs them to the register.

        This should happen at a long period (hours to days).
        :return A tuple with members added, and time taken in seconds.
        """
        await self.bot.wait_until_ready()
        log.debug('sync_users fired')
        from constants import id_wiihacks
        from time import time

        start_time = time()

        wh: discord.Guild = self.bot.get_guild(id_wiihacks)
        if wh is None:
            raise RuntimeError("Could not find WiiHacks Guild!")
        members = wh.members
        futures = []
        for member in members:
            if not await self.is_user(member):
                futures.append(self.add_user(member))
        await asyncio.gather(*futures)

        finish_time = time()
        duration = finish_time - start_time

        log.debug(f'Synced {len(futures)} users in {duration}.')
        return len(futures), duration

    async def delete_user(
            self,
            user: typ.Union[discord.User, discord.Member]) -> None:
        """ Marks a user deleted in the registry. """
        whu: WiiHacksUser = await self.user_read(user)
        whu.deleted = True
        await self.user_write(whu)

    async def undelete_user(
            self,
            user: typ.Union[discord.User, discord.Member]) -> None:
        """ Un marks a user deleted in the registry. """
        whu: WiiHacksUser = await self.user_read(user)
        whu.deleted = False
        await self.user_write(whu)

    async def register_reddit(self, user: discord.Member, reddit_name: str):
        """ Associate a reddit account with a discord account. """
        log.debug(f'register_reddit fired: {user.display_name}|{reddit_name}')
        whu: WiiHacksUser = await self.user_read(user)
        whu.reddit_name = reddit_name
        await self.user_write(whu)

    async def verify_user(self, user: discord.Member):
        """ Marks the user's reddit account as verified. """
        log.debug(f'verify_user fired: {user}')

        # Get user
        whu: WiiHacksUser = await self.user_read(user)

        # Change verify status and and new role
        role = disutil.get(user.guild.roles, name=redditor_role)
        if role is None:
            raise RuntimeError(
                f'Could not retrieve role {redditor_role} from guild.')
        await user.add_roles(role, reason='Reddit name verified.')
        await self.set_reddit_key(whu)
        whu.verified = True

        # Replace user record
        await self.user_write(whu)
        log.debug(f'verify_user success: {user}|{whu}|{role}')

    async def unverify_user(self, user: discord.Member) -> None:
        """ Removes verification from user. """
        log.debug(f'unverify_user fired: {user}')

        # get user
        whu: WiiHacksUser = await self.user_read(user)

        # Change verify status and remove role
        whu.verified = False
        role = disutil.get(user.guild.roles, name=redditor_role)
        if role is None:
            raise RuntimeError(
                f'Could not retrieve role {redditor_role} from guild.')
        await user.remove_roles(role, reason='Reddit name unverified')
        await self.set_reddit_key(whu, remove=True)
        await self.user_write(whu)

    async def send_verification(self, whu: WiiHacksUser) -> None:
        """Send Direct Message Verification.

        This attempts to send a message to the given user's registered
        reddit account.

        :param whu -> User to attempt to send message to.
        """
        from constants import (
            confirmation_message_subject,
            confirmation_message_body)

        # Is this record a registered reddit user?
        if whu.reddit_name == '':
            raise RuntimeError(
                f"User: '{whu.snowflake_id}' has no registered reddit name.")
        if whu.verified:
            raise RuntimeError(
                f"User: '{whu.snowflake_id}' is already verified")

        # verify that user exists,
        reddit: praw.Reddit = await self.get_reddit()
        redditor: praw.reddit.models.Redditor = reddit.redditor(whu.reddit_name)
        if redditor is None:
            raise RuntimeError(
                f'Redditor {whu.reddit_name} not a valid redditor.')

        # send dm
        # This was made non-subreddit sent to prevent modmail litter.
        redditor.message(
            subject=confirmation_message_subject,
            message=confirmation_message_body.format(whu.reddit_name))
        log.debug(f'Send verification request sent to {whu.reddit_name}')

    async def check_message(self, msg: praw.reddit.models.Message) -> bool:
        """Check Messages for Confirmation.

        This function, given a msg will determine if it meets the conditions
        of successful verification.
        :param msg -> Praw Message
        """
        await self.bot.wait_until_ready()
        log.debug(f'check_message fired: {repr(msg)}')

        # regex search it for the {name}#{discriminator} format
        result = re.match(username_regex, msg.body)
        if result is not None:
            log.debug(f'Matched {result.group()} | '
                      f'group1: {result.group(1)} | group2: {result.group(2)}')

        # If found associate it with a whu
        from constants import id_wiihacks
        wiihacks: discord.Guild = self.bot.get_guild(id_wiihacks)
        discord_display = result.group(1) + "#" + result.group(2)
        member = wiihacks.get_member_named(discord_display)
        if member is None:
            log.error(f'u/{msg.author.name} tried to register to ' +
                      f'{discord_display} discord account.')
            msg.mark_read()
            return False
        log.debug(f'Found Member: {member}')

        # make sure the message came from the registered account in whu
        whu = await self.user_read(member)
        log.debug(f'Found user: {whu}|{whu.reddit_name}')

        # make sure everything matches up.
        if msg.author.name.lower() == whu.reddit_name.lower():
            log.debug(f'Successfully match {msg.author.name.lower()} == '
                      f'{whu.reddit_name.lower()} = '
                      f'{msg.author.name.lower() == whu.reddit_name.lower()}')
            await self.verify_user(member)
            txt_reddit_verified = 'Your reddit account has been verified!'
            await member.send(txt_reddit_verified)
            system_cog = self.bot.get_cog('System')
            if system_cog is None:
                log.error(f'Could not obtain system cog to log verify action.')
            else:
                await system_cog.send_to_log(
                    f'{member.display_name} has been verified as '
                    f'u/{whu.reddit_name} on Reddit!')
            return True
        else:
            log.warning(
                f'Registered name and message author do not match: '
                f'{msg.author.name.lower()}|{whu.reddit_name.lower()}')
            msg.mark_read()
            return False

    async def up_vote_user(self, user: discord.User, add: bool = True):
        whu = await self.user_read(user)
        if add:
            whu.up_votes += 1
        else:
            whu.up_votes -= 1
        await self.user_write(whu)

    async def down_vote_user(self, user: discord.User, add: bool = True):
        whu = await self.user_read(user)
        if add:
            whu.down_votes += 1
        else:
            whu.down_votes -= 1
        await self.user_write(whu)

    async def process_inbox(self) -> None:
        """ Processes the inbox for return verifications. """
        def mark_read(
                m: praw.reddit.models.Message
        ) -> praw.reddit.models.Message:
            if m[1] is True:
                m[0].mark_read()
                return m

        log.debug(f'Process Inbox fired.')
        # grab all unread inbox messages
        reddit: praw.Reddit = await self.get_reddit()

        # Check each one (only messages)
        in_messages = \
            [a for a in reddit.inbox.unread(limit=None)
             if (type(a) == praw.reddit.models.Message)]
        results = list(zip(
            in_messages,
            await asyncio.gather(
                *(self.check_message(m) for m in in_messages))))
        verified = list(map(mark_read, results))
        log.debug(f'{results}|{verified}')

    # Processes

    @disextt.loop(minutes=1)
    async def check_inbox_process(self):
        """This fires the process inbox function at a 1 minute interval."""
        # No debug due to frequency
        await self.process_inbox()

    @disextt.loop(hours=24)
    async def sync_users_process(self):
        """ This processes users every 24 hours."""
        log.debug(f'sync_users_process fired.')
        count, ex_time = await self.sync_users()
        log.info(f'Synced {count} users in {ex_time} seconds.')

    # Listeners

    @disextc.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """ When a member joins, add the record, or undelete it. """
        log.debug(f'register.on_member_join: {member}')
        if await self.is_user(member):
            await self.undelete_user(member)
            log.debug(f'Undeleted {member.display_name}.')
        else:
            await self.add_user(member)
            log.debug(f'Added user {member.display_name}.')

    @disextc.Cog.listener()
    async def on_member_remove(self, member):
        log.debug(f'register.on_member_remove: {member}')
        if await self.is_user(member):
            await self.delete_user(member)
            log.debug(f'Deleted {member.display_name}.')
        else:
            log.warning(
                f'User {member.display_name} was not in database but left')

    @disextc.Cog.listener()
    async def on_member_update(
            self, before: discord.Member, after: discord.Member):
        """ Responsible for updating and time-stamping status changes. """
        if before.status != after.status:
            if await self.is_user(before):
                whu = await self.user_read(before)
                whu.last_status = str(after.status)
                from datetime import datetime
                whu.last_status_since = int(datetime.utcnow().timestamp())
                if after.status != 'online':
                    whu.last_online = int(datetime.utcnow().timestamp())
                await self.user_write(whu)
                log.debug(
                    f'member update '
                    f'{before.display_name} {before.status} {after.status}')
            else:
                log.debug(f"User '{before.display_name}' not in redis.")

    @disextc.Cog.listener(name='on_reaction_add')
    async def up_down_vote_add_monitor(
            self, reaction: discord.Reaction, user: discord.User):
        """ Monitor Up / Down Vote Tally"""
        log.debug(f'up_downvote_add:{reaction}')
        # Context matters most
        if self.in_context(reaction=reaction, user=user):
            # These tests will only work if the emoji has a name.
            if self.is_up_vote(reaction.emoji):
                await self.up_vote_user(reaction.message.author)
                log.debug(f'Up Vote reaction added {reaction.emoji}')
            elif self.is_down_vote(reaction.emoji):
                await self.down_vote_user(reaction.message.author)
                log.debug(f'Down Vote reaction added {reaction.emoji}')
            else:
                log.debug(f'Not up or downvote: {reaction.emoji}')

    @disextc.Cog.listener(name='on_reaction_remove')
    async def up_down_vote_remove_monitor(
            self, reaction: discord.Reaction, user: discord.User):
        log.debug(f'up_downvote_add:{reaction}')
        # Context matters most
        if self.in_context(reaction=reaction, user=user):
            # These tests will only work if the emoji has a name.
            if self.is_up_vote(reaction.emoji):
                await self.up_vote_user(reaction.message.author, add=False)
                log.debug(f'Up Vote reaction added {reaction.emoji}')
            elif self.is_down_vote(reaction.emoji):
                await self.down_vote_user(reaction.message.author, add=False)
                log.debug(f'Down Vote reaction added {reaction.emoji}')
            else:
                log.debug(f'Not up or downvote: {reaction.emoji}')

    # Diagnostic Commands

    @disextc.group(name='reg', hidden=True)
    @disextc.is_owner()
    async def registry_group(self, ctx: disextc.Context) -> None:
        """Registry Group"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No subcommend for registry group given.')

    @registry_group.command(name='add', hidden=True)
    @disextc.is_owner()
    async def add_user_command(
            self, ctx: disextc.Context, *, user: discord.Member):
        """Adds given user to the registry."""
        if await self.add_user(user=user):
            await ctx.send(f"User '{user.name}' added to registry.")
        else:
            await ctx.send(f"Unable to save {user.name} to the registry.")

    @registry_group.command(name='get', hidden=True)
    @disextc.is_owner()
    async def get_user_command(
            self, ctx: disextc.Context, *, user: discord.Member):
        """ Checks user against db and retrieves stored info."""
        if await self.is_user(user):
            await ctx.send(repr(await self.user_read(user)))
        else:
            await ctx.send(f"No user found for {user.name}.")

    @registry_group.command(name='redditor', hidden=True)
    @disextc.is_owner()
    async def register_reddit_command(self,
                                      ctx: disextc.Context,
                                      reddit_name: str,
                                      user: discord.Member
                                      ) -> None:
        """ Registers the reddit username to the discord account.

        Send empty double quotes to clear.
        !<> reddit "" bloodythorn
        """
        await self.register_reddit(user, reddit_name)
        await ctx.send(
            f'Successfully associated '
            f'Reddit: u/{reddit_name} with User:{user.name}')

    @registry_group.command(name='verify', hidden=True)
    @disextc.is_owner()
    async def verify_user_command(
            self,
            ctx: disextc.Context,
            user: discord.Member,
            verified: bool = True) -> None:
        """ Toggles user as a registered redditor. """
        if verified:
            await self.verify_user(user)
            await ctx.send(f'Verfied {user.name}.')
        else:
            await self.unverify_user(user)
            await ctx.send(f'Unverified {user.name}.')

    @registry_group.command(name='send', hidden=True)
    @disextc.is_owner()
    async def send_verify_dm_command(
            self, ctx: disextc.Context, user: discord.Member) -> None:
        """Sends a verification DM."""
        await ctx.send(f'Attempting to send DM to : {user.display_name}')
        whu: WiiHacksUser = await self.user_read(user)
        await self.send_verification(whu)
        await ctx.send(f'Verification DM sent to {user.display_name}.')

    @registry_group.command(name='sync', hidden=True)
    @disextc.is_owner()
    async def sync_users_command(self, ctx: disextc.Context) -> None:
        """Checks all currently registered users against the DB. """
        txt_sync = "Syncing all current users..."
        async with ctx.typing():
            await ctx.send(txt_sync)
            log.info(txt_sync)
            count, ex_time = await self.sync_users()
            await ctx.send(f'{count} users synced in {ex_time} seconds.')

    # TODO: move the constants out of here.
    # TODO: Might want to put log output in console not discord. (make a deco)
    @registry_group.command(name='karma', hidden=True)
    @decorators.with_roles(constants.moderator_and_up + [708924829679747073])
    async def get_user_karma_command(
            self, ctx: disextc.Context, *, user: discord.Member):
        """ This will return given user's karma or executor's karma if user
        is absent, or unable to be found.
        """
        up_vote = self.bot.get_emoji(718726011759493126)
        down_vote = self.bot.get_emoji(718725629847142410)
        whu: WiiHacksUser = await self.user_read(user)
        display_name = user.display_name
        await ctx.send(
            f"{display_name}'s karma total: " +
            f"{whu.up_votes + (-1 * whu.down_votes)} " +
            f'({whu.up_votes}{up_vote}/{whu.down_votes}{down_vote})')

    @registry_group.command(name='last', hidden=True)
    @decorators.with_roles(constants.moderator_and_up + [708924829679747073])
    async def last_seen_command(
            self, ctx: disextc.Context, *, user: discord.Member) -> None:
        """ Will retrieve when user was last seen. """
        from constants import id_bloodythorn
        if user.id == id_bloodythorn:
            await ctx.send(
                f'Do you really think I am not paranoid enough not'
                f' to make something that tracks me?')
            return
        whu = await self.user_read(user)
        if whu.last_status_since == 0 or \
                whu.last_status == '':
            await ctx.send(
                f"User '{user.name}' has a default entry: {whu}")
        else:
            from datetime import datetime
            await ctx.send(
                f"User '{user.name}' in {whu.last_status} status since : " +
                f"{str(datetime.fromtimestamp(whu.last_status_since))} UTC.")
            if whu.last_status != 'online' and whu.last_online != 0:
                await ctx.send(
                    f"They were last in online status : " +
                    f"{str(datetime.fromtimestamp(whu.last_online))} UTC")

    # TODO: Constants
    @registry_group.command(name='register', hidden=True)
    @decorators.without_role([708924829679747073])
    @decorators.log_invocation()
    async def registration_command(
            self, ctx: disextc.Context, reddit_name: str) -> None:
        """ Register your Reddit account with r/WiiHacks Discord guild."""
        try:
            # Pull user to check
            if not await self.is_user(ctx.author):
                await self.add_user(ctx.author)
            whu: WiiHacksUser = await self.user_read(ctx.author)
            if whu.last_attempt_failed:
                raise disextc.CommandError(f're-register fail')
            whu.last_attempt_failed = True
            whu.reddit_name = reddit_name
            await self.user_write(whu)
            await ctx.send(
                f'Registering your reddit account as u/{reddit_name}...')
            await self.register_reddit(ctx.author, reddit_name)
            await ctx.send(f'Sending a DM to u/{whu.reddit_name}...')
            await self.send_verification(whu)
            await ctx.send(f"Verification was sent to {reddit_name}'s DM." +
                           " Please follow the instructions contained within.")
            await self.user_write(whu)
        except Exception as e:
            await ctx.send(
                f'An error occurred while trying to register your reddit' +
                f' account. Please contact a moderator or bot dev.')
            log.error(f'An error has occurred registering {ctx.author} ' +
                      f'| {e.args}')
            whu: WiiHacksUser = await self.user_read(ctx.author)
            whu.last_attempt_failed = True
            await self.user_write(whu)
            system_cog = self.bot.get_cog('System')
            if system_cog is not None:
                await system_cog.send_to_log(
                    f"{ctx.author} has encountered an error in associating " +
                    f"their account with " +
                    f"u/{reddit_name} | {e.args}")

    @registry_group.command(name='reset', hidden=True)
    @decorators.with_roles(constants.moderator_and_up)
    @decorators.log_invocation()
    async def reset_registration_command(
            self, ctx: disextc.Context, user_id: int) -> None:
        """ Reset user's verification. User ID required. """
        member: discord.Member = disutil.find(
            lambda m: m.id == user_id, ctx.guild.members)
        if member is None:
            raise disextc.CommandError(
                f'Could not find member with id {user_id}')
        await ctx.send(f'Resetting registration for {member.display_name}.')
        await self.unverify_user(member)
        whu: WiiHacksUser = await self.user_read(member)
        whu.reddit_name = ''
        whu.verify_attempts = 0
        whu.last_attempt_failed = False
        await self.user_write(whu)
        await ctx.send(
            f'{member.display_name} has been unregistered by {ctx.author}.')


def setup(bot: disextc.Bot) -> None:
    """ Loads register cog. """
    bot.add_cog(Register(bot))
