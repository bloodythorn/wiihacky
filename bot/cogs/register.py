import asyncio
import discord
import discord.ext.commands as disextc
import discord.ext.tasks as disextt
import discord.utils as disutil
import logging as lg
import praw
import typing as typ
import re

import bot.constants as constants
import bot.decorators as decorators

from datetime import datetime

from bot.data import User, session_scope

log = lg.getLogger(__name__)

# TODO: Move more of this to constants.
redditor_role = 'Redditor'
username_regex = re.compile(r'^([^#]*)#([0-9]*)')
up_down_vote_regex = re.compile(r'^(up|down)([_]?vote)?$')
thumbs_up = '👍'
thumbs_down = '👎'
up_vote_emoji_id = 718726011759493126
down_vote_emoji_id = 718725629847142410


# todo: command that auto-nicks you to your reddit name and alias

class Register(disextc.Cog):
    """
        This cog/module is responsible for registering users with the system,
        keeping track of their comings and goings, and associating their
        discord account with their reddit account.
    """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

        # Start processes related to this cog
        self.check_inbox_process.start()
        self.sync_users_process.start()

    def cog_unload(self):
        # Stop processes
        self.check_inbox_process.cancel()
        self.sync_users_process.cancel()

    # Checks

    @staticmethod
    def is_up_vote(emoji: discord.Emoji) -> bool:
        """Detects if the emoji qualifies as an 'up vote'. """
        log.debug(f'Testing for up vote: {emoji}')
        if hasattr(emoji, 'name'):
            result_one = re.match(up_down_vote_regex, emoji.name)
            if result_one is not None and result_one.group(1).lower() == 'up':
                log.debug(f'Pattern {up_down_vote_regex} matched.')
                return True
        elif isinstance(emoji, str):
            if emoji == thumbs_up:
                return True
        else:
            log.debug(f'Failing Emoji:{emoji}')
            return False

    @staticmethod
    def is_down_vote(emoji: discord.Emoji) -> bool:
        """Detects if the emoji qualifies as a 'down vote'. """
        log.debug(f'Testing for down vote: {emoji}')
        if hasattr(emoji, 'name'):
            result_one = re.match(up_down_vote_regex, emoji.name)
            if result_one is not None \
                    and result_one.group(1).lower() == 'down':
                return True
        elif isinstance(emoji, str):
            if emoji == thumbs_down:
                return True
        else:
            log.debug(f'Failing Emoji:{emoji}')
        return False

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
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=member.id).first()
            if usr is None:
                await self.add_user(member)
                log.debug(f'Added user {member.display_name}.')
            else:
                usr.deleted = False
                log.debug(f'Undeleted {member.display_name}.')

    @disextc.Cog.listener()
    async def on_member_remove(self, member):
        log.debug(f'register.on_member_remove: {member}')
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=member.id)
            if usr is None:
                log.warning(
                    f'User {member.display_name} was not in database but left')
            else:
                usr.deleted = True
                log.debug(f'Deleted {member.display_name}.')

    @disextc.Cog.listener()
    async def on_member_update(
        self,
        before: discord.Member,
        after: discord.Member
    ) -> None:
        """ Responsible for updating and time-stamping status changes. """
        await self.update_status(before, after)
        log.debug(f"User update done: '{before.display_name}'.")

    # TODO: A way to change these, ie add more, would be nice.
    #   Also tie it to a 'starboard'
    @disextc.Cog.listener(name='on_reaction_add')
    async def up_down_vote_add_monitor(
        self,
        reaction: discord.Reaction,
        user: discord.User
    ) -> None:
        """ Monitor Up / Down Vote Tally"""
        log.debug(f'up_downvote_add:{reaction.emoji}')
        # These tests will only work if the emoji has a name.
        log.debug(f'testing reaction: {reaction.emoji}')
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
        self,
        reaction: discord.Reaction,
        user: discord.User
    ) -> None:
        log.debug(f'up_downvote_add:{reaction.emoji}')
        # These tests will only work if the emoji has a name.
        if self.is_up_vote(reaction.emoji):
            await self.up_vote_user(reaction.message.author, add=False)
            log.debug(f'Up Vote reaction added {reaction.emoji}')
        elif self.is_down_vote(reaction.emoji):
            await self.down_vote_user(reaction.message.author, add=False)
            log.debug(f'Down Vote reaction added {reaction.emoji}')
        else:
            log.debug(f'Not up or downvote: {reaction.emoji}')

    # Helpers

    async def get_reddit(self) -> praw.Reddit:
        reddit_cog = self.bot.get_cog('Reddit')
        if not reddit_cog:
            raise RuntimeError(f'Could not retrieve reddit cog.')
        reddit = await reddit_cog.reddit
        return reddit

    async def add_user(self, user: discord.Member) -> None:
        """ Adds a user to the registry. """
        log.debug(f'add_user fired: {user}')
        from datetime import datetime
        usr = User(
            snowflake=user.id,
            reddit_name='',
            utc_added=datetime.utcnow(),
            locked=False,
            verified=False,
            last_status=str(user.status),
            since=datetime.utcnow(),
            last_online=datetime.utcnow(),
            deleted=False,
            up_votes=0,
            down_votes=0
        )
        # with session_scope as session:
        #    session.add(usr)
        with session_scope(self.bot.engine) as session:
            session.add(usr)

    async def sync_users(self) -> typ.Tuple[int, float]:
        """ Reads current users and syncs them to the register.

            This should happen at a long period (hours to days).
            :return A tuple with members added, and time taken in seconds.
        """
        await self.bot.wait_until_ready()
        log.debug('sync_users fired')
        from time import time
        start_time = time()

        wh: discord.Guild = self.bot.get_guild(constants.id_wiihacks)
        if wh is None:
            raise RuntimeError("Could not find WiiHacks Guild!")
        count = 0
        for member in wh.members:
            with session_scope(self.bot.engine) as session:
                usr = session.query(
                    User).filter_by(snowflake=member.id).first()
                if usr is None:
                    await self.add_user(member)
                    count += 1

        finish_time = time()
        duration = finish_time - start_time

        log.debug(f'Synced {count} users in {duration}.')
        return count, duration

    async def register_reddit(
        self,
        user: discord.Member,
        reddit_name: str
    ) -> None:
        """ Associate a reddit account with a discord account. """

        log.debug(f'register_reddit fired: {user.display_name}|{reddit_name}')
        with session_scope(self.bot.engine) as session:
            # TODO: This should prolly be more robust. Prolly just errors
            #   when it doesn't work
            session.query(User).filter_by(snowflake=user.id).update({
                'reddit_name': reddit_name
            })

    async def verify_user(self, user: discord.Member) -> None:
        """ Marks the user's reddit account as verified. """
        log.debug(f'verify_user fired: {user}')

        # Change verify status and and new role
        role = disutil.get(user.guild.roles, name=redditor_role)
        if role is None:
            raise RuntimeError(
                f'Could not retrieve role {redditor_role} from guild.')
        await user.add_roles(role, reason='Reddit name verified.')
        with session_scope(self.bot.engine) as session:
            session.query(User).filter_by(snowflake=user.id).update({
                'verified': True
            })

        log.info(f'verify_user success: {user}|{role}')

    async def unverify_user(self, user: discord.Member) -> None:
        """ Removes verification from user. """
        log.debug(f'unverify_user fired: {user}')

        # Change verify status and remove role
        role = disutil.get(user.guild.roles, name=redditor_role)
        if role is None:
            raise RuntimeError(
                f'Could not retrieve role {redditor_role} from guild.')
        await user.remove_roles(role, reason='Reddit name unverified')
        with session_scope(self.bot.engine) as session:
            session.query(User).filter_by(snowflake=user.id).update({
                'verified': False
            })

    async def send_verification(self, user: discord.Member) -> None:
        """Send Direct Message Verification.

        This attempts to send a message to the given user's registered
        reddit account.

        :param whu -> User to attempt to send message to.
        """
        from bot.constants import (
            confirmation_message_subject,
            confirmation_message_body)

        # Is this record a registered reddit user?
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=user.id).first()
            if usr is None:
                raise RuntimeError(
                    f"User: '{user.id}' has no registered reddit name.")
            if usr.verified:
                raise RuntimeError(
                    f"User: '{user.id}' is already verified")

            # verify that user exists,
            reddit: praw.Reddit = await self.get_reddit()
            redditor: praw.reddit.models.Redditor = \
                reddit.redditor(usr.reddit_name)
            if redditor is None:
                raise RuntimeError(
                    f'Redditor {user.id} not a valid redditor.')

            # send dm
            # This was made non-subreddit sent to prevent modmail litter.
            redditor.message(
                subject=confirmation_message_subject,
                message=confirmation_message_body.format(usr.reddit_name))
            log.debug(f'Send verification request sent to {user.id}')

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
        else:
            return False

        # If found associate it with a registered user
        from bot.constants import id_wiihacks
        wiihacks: discord.Guild = self.bot.get_guild(id_wiihacks)
        discord_display = result.group(1) + "#" + result.group(2)
        member = wiihacks.get_member_named(discord_display)

        # If we can't find the member for some reason
        if member is None:
            log.error(f'u/{msg.author.name} tried to register to '
                      f'{discord_display} discord account.')
            msg.mark_read()
            return False

        # At last validate it as a found member
        log.debug(f'Found Member: {member}')

        # Create the DB Object
        with session_scope(self.bot.engine) as session:
            # This will head off a user re-registering.
            usr = session.query(User).filter_by(snowflake=member.id).first()
            log.debug(f'Found user: {usr}')
            if usr.verified:
                log.warning(f"User '{member.id}' has re-verified.")
                msg.mark_read()
                return True

            # make sure the message came from the registered account
            if msg.author.name.lower() == usr.reddit_name.lower():
                log.debug(
                    "Successfully matched %s  == %s = %s" % (
                        msg.author.name.lower(),
                        usr.reddit_name.lower(),
                        msg.author.name.lower() == usr.reddit_name.lower()
                    )
                )

                await self.verify_user(member)
                txt_reddit_verified = 'Your reddit account has been verified!'
                await member.send(txt_reddit_verified)
                system_cog = self.bot.get_cog('System')
                if system_cog is None:
                    log.error(
                        f'Could not obtain system cog to log verify action.')
                else:
                    await system_cog.send_to_log(
                        f'{member.display_name} has been verified as '
                        f'u/{usr.reddit_name} on Reddit!')
                msg.mark_read()
                return True
            else:
                log.warning(
                    f'Registered name and message author do not match: '
                    f'{msg.author.name.lower()}|{usr.reddit_name.lower()}')
                msg.mark_read()
                return False

    async def up_vote_user(self, user: discord.User, add: bool = True):
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=user.id).first()
            if add:
                usr.up_votes += 1
            else:
                usr.up_votes -= 1

    async def down_vote_user(self, user: discord.User, add: bool = True):
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=user.id).first()
            if add:
                usr.down_votes += 1
            else:
                usr.down_votes -= 1

    async def process_inbox(self) -> None:
        """ Processes the inbox for return verifications. """
        log.debug(f'Process Inbox fired.')
        results = []
        try:
            # grab all unread inbox messages
            reddit: praw.Reddit = await self.get_reddit()

            # Check each one (only messages)
            in_messages = \
                [a for a in reddit.inbox.unread(limit=None)
                 if (type(a) == praw.reddit.models.Message)]
            results = list(await asyncio.gather(
                *(self.check_message(m) for m in in_messages)))
        except Exception as e:
            log.error(
                f'An error was encountered processing the inbox: {e.args}')
        if len(results) != 0:
            log.debug(f'results:{results}')

    async def update_status(
        self,
        before: discord.Member,
        after: discord.Member
    ) -> None:
        if before.status != after.status:
            with session_scope(self.bot.engine) as session:
                session.query(User).filter_by(snowflake=before.id).update({
                    'last_status': str(after.status),
                    'since': datetime.utcnow()
                })
                if after.status != 'online':
                    session.query(User).filter_by(
                        snowflake=before.id).update({
                            'last_online': datetime.utcnow()
                        })

    # Diagnostic Commands

    @disextc.group(name='reg', hidden=True)
    @disextc.is_owner()
    async def registry_group(self, ctx: disextc.Context) -> None:
        """Registry Group"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No sub command for registry group given.')

    @registry_group.command(name='add', hidden=True)
    @disextc.is_owner()
    async def add_user_command(
        self,
        ctx: disextc.Context,
        *, user: discord.Member
    ) -> None:
        """Adds given user to the registry."""
        if await self.add_user(user=user):
            await ctx.send(f"User '{user.name}' added to registry.")
        else:
            await ctx.send(f"Unable to save {user.name} to the registry.")

    @registry_group.command(name='get', hidden=True)
    @disextc.is_owner()
    async def get_user_command(
        self,
        ctx: disextc.Context,
        *, user: discord.Member
    ) -> None:
        """ Checks user against db and retrieves stored info."""
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=user.id).first()
            await ctx.send(f'User: {usr}')

    @registry_group.command(name='redditor', hidden=True)
    @disextc.is_owner()
    async def register_reddit_command(
        self,
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
        verified: bool = True
    ) -> None:
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
        self,
        ctx: disextc.Context,
        user: discord.Member
    ) -> None:
        """Sends a verification DM."""
        await ctx.send(f'Attempting to send DM to : {user.display_name}')
        await self.send_verification(user)
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

    @registry_group.command(name='karma', hidden=True)
    @decorators.with_roles(
        constants.moderator_and_up + [constants.reddit_user_role_id])
    async def get_user_karma_command(
        self,
        ctx: disextc.Context,
        *, user: discord.Member
    ) -> None:
        """ This will return given user's karma or executor's karma if user
            is absent, or unable to be found.
        """
        up_vote = self.bot.get_emoji(up_vote_emoji_id)
        down_vote = self.bot.get_emoji(down_vote_emoji_id)
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=user.id).first()
            await ctx.send(
                f"{user.display_name}'s karma tota: "
                f"{usr.up_votes + (-1 * usr.down_votes)}"
                f"({usr.up_votes}{up_vote}/{usr.down_votes}{down_vote})")

    @registry_group.command(name='last', hidden=True)
    @decorators.with_roles(
        constants.moderator_and_up + [constants.reddit_user_role_id])
    async def last_seen_command(
        self,
        ctx: disextc.Context,
        *, user: discord.Member
    ) -> None:
        """ Will retrieve when user was last seen. """
        if user.id == constants.id_bloodythorn:
            await ctx.send(
                f'Do you really think I am not paranoid enough not'
                f' to make something that tracks me?')
            return
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(snowflake=user.id).first()
            if usr.since == 0 or usr.last_status == '':
                await ctx.send(
                    f"User '{user.name}' has no recorded online status...")
            else:
                await ctx.send(
                    f"User '{user.name}' in {usr.last_status} status since : "
                    f"{str(usr.last_online)} UTC.")
                if usr.last_status != 'online' and usr.last_online != 0:
                    await ctx.send(
                        f"They were last in online status : "
                        f"{str(usr.last_online)} UTC")

    @registry_group.command(name='register', hidden=True)
    @decorators.without_role([constants.reddit_user_role_id])
    @decorators.log_invocation()
    async def registration_command(
        self,
        ctx: disextc.Context,
        reddit_name: str
    ) -> None:
        """ Register your Reddit account with r/WiiHacks Discord guild."""
        with session_scope(self.bot.engine) as session:
            usr = session.query(User).filter_by(
                snowflake=ctx.author.id).first()
            if usr.locked:
                await ctx.send(f're-registration fail: account is locked.')
                raise disextc.CommandError(
                    f're-register fail: {ctx.author.id}')

            # Users can only try this once without moderator intervention.
            usr.locked = True

            # Setup reddit name
            log.debug(f'name given: {reddit_name}')

            if reddit_name[0:2] == 'u/':
                log.debug(f'Trimming {reddit_name} to {reddit_name[2:]}.')
                reddit_name = reddit_name[2:]

            if reddit_name[0:3] == '/u/':
                log.debug(f'Trimming {reddit_name} to {reddit_name[3:]}.')
                reddit_name = reddit_name[3:]

            usr.reddit_name = reddit_name

        # Notify user
        register_txt = f"Registering your reddit account as " + \
                       f"u/{reddit_name}. I'll send a DM to " + \
                       f"that account to verify."
        await ctx.send(register_txt)
        await self.register_reddit(ctx.author, reddit_name)

        # Send DM
        await self.send_verification(ctx.author)
        await ctx.send(f"Verification was sent to u/{reddit_name}'s DM."
                       " Please follow the instructions contained within.")

    @registry_group.command(name='reset', hidden=True)
    @decorators.with_roles(constants.moderator_and_up)
    @decorators.log_invocation()
    async def reset_registration_command(
        self,
        ctx: disextc.Context,
        user_id: int
    ) -> None:
        """ Reset user's verification. User ID required. """
        member: discord.Member = disutil.find(
            lambda m: m.id == user_id, ctx.guild.members)
        if member is None:
            raise disextc.CommandError(
                f'Could not find member with id {user_id}')
        await ctx.send(f'Resetting registration for {member.display_name}.')
        await self.unverify_user(member)
        with session_scope(self.bot.engine) as session:
            session.query(User).filter_by(snowflake=member.id).update({
                'reddit_name': '',
                'locked': False
            })
        await ctx.send(
            f'{member.display_name} has been unregistered by {ctx.author}.')


def setup(bot: disextc.Bot) -> None:
    """ Loads register cog. """
    bot.add_cog(Register(bot))
