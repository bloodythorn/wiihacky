import asyncio
import discord as discord
import discord.ext.commands as disextc
import logging as lg
import nltk
import praw
import random
import torch
import typing as typ

import constants
import decorators

log = lg.getLogger(__name__)

txt_cog_sub_err = 'Invalid discord subcommand.'


# TODO: Flesh out commands.
# TODO: moderator functions
# TODO: Bot CLI Channels
# TODO: cache_messages
#   This might require a 'reader'
# TODO: Allowed mentions
# Some of the following might already be implemented in id.
# TODO: get channel, guild, user, emoji, all_channels, all_members,
# TODO: Yes/no confirmation prompt with reactions, that should belong here.
# TODO: yes/no dialog or multiple choice dialog
# TODO: Change presence
# TODO: Fetch Guilds -> Might need to make a bot-testing guild.
# TODO: Pins -> Identify and cache files, especially syschecks.
# TODO: Create Guild/channel/category etc ?
# TODO: Invites
# TODO: Widgets?
# TODO: Webhooks
# TODO: Teams
# TODO: Create Group Chat.

DISCORD_MAX_CHARS = 2000


class Discord(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        # TODO: Get rid of these
        from constants import paginate, send_paginator
        self.paginate = paginate
        self.send_paginator = send_paginator

    # Helpers

    # TODO: Send Greeting (Person, Location)

    # Listeners

    @disextc.Cog.listener(name='on_member_join')
    async def greeter(self, member: discord.Member):
        # TODO: Create Welcomer Here!
        log.debug(f'on_member_join: {member}')

    # Discord Group Commands

    @disextc.group(name='dis', hidden=True)
    @disextc.is_owner()
    async def discord_group(self, ctx: disextc.Context) -> None:
        """ Discord Subgroup.

        This is the main subgroup for the Discord Cog.
        """
        # TODO: This should pull up subgroup help or handle it more gracefully
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @discord_group.command(name='act', hidden=True)
    @disextc.is_owner()
    async def activity_command(self, ctx: disextc.Context) -> None:
        """ Read Bot Activity.

        This currently only retrieves and prints the bot activity.

        :param ctx -> Invocation context
        :return None
        """
        # TODO: Expand this to a group and add more control.
        # TODO: Paginate the result
        me = discord.utils.get(self.bot.get_all_members(), id=self.bot.user.id)
        await self.send_paginator(ctx, await self.paginate(repr(me.activities)))

    @discord_group.command(name='id', hidden=True)
    @disextc.is_owner()
    async def multi_id_command(
            self,
            ctx: disextc.Context,
            what: typ.Union[
                discord.Member,
                discord.TextChannel,
                discord.VoiceChannel,
                discord.User,
                discord.Message,
                discord.Guild,
                discord.CategoryChannel,
                discord.Role,
                discord.Emoji,
                discord.PartialEmoji
            ]) -> None:
        """ ID member, txt/voicechannel, user, message, guild.

        This function will take a string and see if it is a member,
        txt/voicechannel, user, message, guild, in that order.

        :param ctx -> Invocation Context
        :param what -> What do you need IDed?
        :return None
        """
        # TODO: Paginate results.
        await self.send_paginator(ctx, await self.paginate(repr(what)))

    @discord_group.command(name='guilds', hidden=True)
    @disextc.is_owner()
    async def guild_list_command(self, ctx: disextc.Context) -> None:
        """ Guild list.

        :param ctx -> Invocation Context
        """
        # TODO Paginate better
        await self.send_paginator(
            ctx, await self.paginate(
                repr([a.name for a in list(self.bot.guilds)])))

    @discord_group.command(name='emj', hidden=True)
    @disextc.is_owner()
    async def list_custom_emoji_command(self, ctx: disextc.Context) -> None:
        """ Lists custom emojis.

        This function will return all data on custom emojis.

        :param ctx -> Invocation Context
        :return None
        """
        await self.send_paginator(
            ctx, await self.paginate(repr(ctx.bot.emojis)))

    @discord_group.command(name='latency', hidden=True)
    @disextc.is_owner()
    async def latency_command(self, ctx: disextc.Context) -> None:
        """ Reads client latency.

        This returns the latency the client is currently under.

        :param ctx -> Invocation context.
        :return None
        """
        # TODO Paginate better
        await self.send_paginator(
            ctx, await self.paginate(repr(self.bot.latency)))

    @discord_group.command(name='status', hidden=True)
    @disextc.is_owner()
    async def status_command(self, ctx: disextc.Context) -> None:
        """ Status of the Bot.

        This will read out the current status of the bot.

        :param ctx -> Invocation context.
        :return None
        """
        # TODO: Necessary?
        me = discord.utils.get(self.bot.get_all_members(), id=self.bot.user.id)
        await self.send_paginator(ctx, await self.paginate(repr(me.status)))

    @discord_group.command(name='version', hidden=True)
    @disextc.is_owner()
    async def version_control(self, ctx: disextc.Context) -> None:
        """ Return discord.py version.

        :param ctx -> Invocation Context
        :return None
        """
        # TODO: Better Pagination
        await self.send_paginator(
            ctx, await self.paginate(
                repr([discord.version_info, discord.__version__])))

    # Channel Group Commands

    @discord_group.group(name='chn', hidden=True)
    @disextc.is_owner()
    async def channel_group(self, ctx: disextc.Context):
        """ Channel Subgroup. """
        # TODO: Handle more gracefully.
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @channel_group.command(name='pos', hidden=True)
    @disextc.is_owner()
    async def position_command(
        self, ctx: disextc.Context,
        channel: typ.Union[discord.TextChannel,
                           discord.VoiceChannel]
    ) -> None:
        """ Channel Position in List. """
        # TODO: Getter/setter by adding another arg that's an integer.
        #   Also a requirement is that the channel is refered to by ID
        #   if the set command is used.
        await self.send_paginator(
            ctx, await self.paginate(repr(channel.position)))

    @channel_group.command(name='priv', hidden=True)
    @disextc.is_owner()
    async def list_private_channels_command(self, ctx: disextc.Context):
        """ List private channels. """
        # TODO: Channel functions -> Close, create, delete, permissions
        await self.send_paginator(
            ctx, await self.paginate(repr(self.bot.private_channels)))

    @channel_group.command(name='voice', hidden=True)
    @disextc.is_owner()
    async def list_voice_connections_command(self, ctx: disextc.Context):
        """ Voice connections. """
        await self.send_paginator(
            ctx, await self.paginate(repr(self.bot.voice_clients)))

    # Message Group Commands

    @discord_group.group(name='msg', hidden=True)
    @disextc.is_owner()
    async def message_group(self, ctx: disextc.Context) -> None:
        """ Discord Messaging related commands. """
        # TODO: Invoke help
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @message_group.command(name='chn', hidden=True)
    @disextc.is_owner()
    async def msg_channel_command(
            self,
            ctx: disextc.Context,
            channel: discord.TextChannel, *, message: str) -> None:
        """ Message to Channel.

        Given an identifiable channel name and string it will send the string
        to the channel as the bot.

        :param ctx -> Context
        :param channel -> Channel to send to.
        :param message -> String to send to channel.
        """
        # TODO: use ctx in log output
        await channel.send(message)

    @message_group.command(name='rct', hidden=True)
    @disextc.is_owner()
    async def react_to_message_command(
            self,
            ctx: disextc.Context,
            message: discord.Message,
            react: typ.Union[discord.Reaction,
                             discord.Emoji,
                             discord.PartialEmoji,
                             str]) -> None:
        await message.add_reaction(react)

    @message_group.command(name='mbr', hidden=True)
    @disextc.is_owner()
    async def msg_member_command(
            self, ctx: disextc.Context,
            member: discord.Member, *, message: str) -> None:
        """ Message Member.

        Given an identifiable member name and string it will send the string
        to the member as the bot.

        :param ctx -> Context command was sent from.
        :param member -> Member to send message to.
        :param message -> String to sent to member.
        :return None
        """
        await member.send(message)

    @message_group.command(name='del', hidden=True)
    @disextc.is_owner()
    async def delete_msg_command(
            self, ctx: disextc.Context,
            message: discord.Message) -> None:
        """ Deletes given message.

        Given a message this function will remove it.

        :param ctx -> Context required by command
        :param message -> Message to be deleted
        :return None
        """
        await message.delete()

    @message_group.command(name='dev', hidden=True)
    @disextc.is_owner()
    async def msg_developer_command(
            self, ctx: disextc.Context, *, message: str) -> None:
        """ Message the developer.

        Messages the hardcoded developer ID. If the ID is not found it will
        throw a badargument exception.

        :param ctx Context the message was invoked in
        :param message The text message to send.
        """
        message_format = 'From:{}|Where:{}|:-> {}'
        dev_not_found = 'Developer could not be found on discord!'
        from constants import id_bloodythorn
        dev: discord.User = self.bot.get_user(id_bloodythorn)
        if dev is not None:
            snd = message_format.format(ctx.author, ctx.channel, message)
            await dev.send(snd)
        else:
            raise disextc.BadArgument(dev_not_found)

    @discord_group.command(name='rename', hidden=True)
    @decorators.with_roles(constants.moderator_and_up)
    async def rename_command(
            self, ctx: disextc.Context,
            member: discord.Member,
            name: typ.Optional[str]
    ):
        old_name = member.display_name
        if name is None:
            new_name = random.choice(nltk.corpus.names.words())
        else:
            new_name = name
        await member.edit(
            nick=new_name, reason=f'renamed by {ctx.author.display_name}')
        await ctx.send(f'{old_name} is now {new_name}!!!')


class ModStatsDisplay:
    # TODO: Compact mode (changing padding.

    metered_actions = tuple(sorted([
        'approvecomment', 'approvelink',
        'lock', 'distinguish', 'ignorereports', 'sticky',
        'removecomment', 'removelink',
        'spamcomment', 'spamlink']))
    KEY_COLUMN_NAMES = ['col', '-', '[', 'key', ']', '+', 'row']
    MAX_CHAR_COUNT: int = 2000
    BLANK = 'X'

    def __init__(
            self,
            subreddit: praw.reddit.Subreddit,
            count: int = 500,
            display_key: bool = True,
            compact: bool = False,
            limit_to_mods: bool = True,
            limit_actions: bool = True,
            restrict_to_user: discord.User = None
    ) -> None:
        from prettytable import PrettyTable
        self._subreddit = subreddit
        self._display_table = PrettyTable(encoding='utf-8')
        self._key_table = PrettyTable(encoding='utf-8')
        self._count = count
        self._display_key = display_key
        self._limit_to_mods = limit_to_mods
        self._limit_to_actions = limit_actions
        self._user = restrict_to_user
        self._data = None
        self._oldest = None
        self._actors = None
        self._actions = None
        self._matrix = None
        self._key_zip = None
        self._low_index = 0
        self._high_index = 0
        self._compact = compact
        self._prefix = '```'
        self._suffix = '```'

    @property
    async def headers(self):
        return [self.BLANK] + \
               [str(i) for i in range(len(self._actions))] + \
               ['ttl']

    @property
    async def oldest_string(self) -> str:
        if self._oldest is None:
            return ''
        from datetime import datetime
        return str(datetime.utcfromtimestamp(self._oldest)) + ' UTC'

    @property
    async def table_display(self) -> str:
        return self._display_table[
               self._low_index:self._high_index].get_string()

    @property
    async def key_display(self) -> str:
        return self._key_table[self._low_index:self._high_index]

    async def set_display_format(self):
        """This function sets the display to its initial setting. """
        # Format Output
        # Remember that unicode is often a bad idea because monospaced
        # fonts aren't monospaced with unicode on some platforms (Windows)

        if self._compact:
            self._display_table.padding_width = 0
            self._key_table.padding_width = 0
        else:
            self._display_table.padding_width = 1
            self._key_table.padding_width = 1
        self._display_table.sortby = 'ttl'
        self._display_table.align = 'r'
        self._key_table.border = False
        self._key_table.align['col'] = 'r'
        self._key_table.align['-'] = 'c'
        self._key_table.align['['] = 'c'
        self._key_table.align['key'] = 'c'
        self._key_table.align[']'] = 'c'
        self._key_table.align['+'] = 'c'
        self._key_table.align['row'] = 'l'

        # Set end index if over DISCORD_MAX_CHARS
        while len(self._display_table.get_string()) > DISCORD_MAX_CHARS:
            if self._display_table.end is None:
                # noinspection PyProtectedMember
                self._display_table.end = len(self._display_table._rows)
            self._display_table.end -= 1

    async def prepare_data(self):
        # TODO: Docu and clean up a bit?
        # define the actors and actions we care about.
        users_to_pull = []
        if self._limit_to_mods:
            users_to_pull = \
                tuple(sorted(
                    [mod.name for mod in list(self._subreddit.moderator())]))

        actions_to_poll = []
        if self._limit_to_actions:
            actions_to_poll = self.metered_actions

        # Pull data
        self._data, self._oldest = await self.tally_moderator_actions(
            history_limit=self._count,
            subreddit=self._subreddit,
            actions_names=actions_to_poll,
            user_names=users_to_pull)

        # Pull detected actors and actions, sort, remove doubles
        self._actors = list(sorted(self._data.keys()))
        self._actions = []
        for actor in self._actors:
            self._actions += list(self._data[actor].keys())
        self._actions = list(sorted(set(self._actions)))

        # Convert to a torch tensor
        self._matrix = torch.zeros(
            len(self._actors) + 1,
            len(self._actions) + 1,
            dtype=torch.int)
        for idx_y, actor in enumerate(self._actors):
            for idx_x, action in enumerate(self._actions):
                if action in self._data[actor]:
                    self._matrix[idx_y][idx_x] = self._data[actor][action]

        # Calc the Totals
        self._matrix[len(self._actors), :] = self._matrix.sum(dim=0)
        self._matrix[:, len(self._actions)] = self._matrix.sum(dim=1)

        # Headers
        self._display_table.field_names = await self.headers

        # Add Data Rows
        for idx, actor in enumerate(self._actors):
            self._display_table.add_row(
             [idx] + list(self._matrix[idx, :].numpy()))
        self._display_table.add_row(
            ['ttl'] + list(self._matrix[len(self._actors), :].numpy()))

        # Fill in blanks of the shorter list.
        while len(self._actions) > len(self._actors):
            self._actors.append(self.BLANK)
        while len(self._actions) < len(self._actors):
            self._actions.append(self.BLANK)

        # Create Key
        self._key_zip = list(zip(self._actions, self._actors))
        self._key_table.field_names = self.KEY_COLUMN_NAMES
        for idx, row in enumerate(self._key_zip):
            self._key_table.add_row(
                [row[0], '-', '|', idx, '|', '+', row[1]])

        await self.set_display_format()

    # noinspection PyProtectedMember
    @staticmethod
    async def tally_moderator_actions(
            history_limit: int,
            subreddit: praw.reddit.Subreddit,
            user_names: typ.List[str],
            actions_names: typ.List[str]
    ):
        """Tally moderator log stats.

        Given a list of user names, and action names the mod log will
        be searched for results matching, and return a tally and a
        tuple containing the oldest entry in utc unix.

        If no user_names or action_names are given, it will return
        filter no entries in that category. (whitelist filter)

        Empty list as well.

        :param history_limit -> Integer with how many entries to search.
        :param subreddit -> The reddit subreddit to search.
        :param user_names -> List of user names to filter to.
        :param actions_names -> List of action names to filter to.
        :return a tuple containing a list of moderator log entries with
            given criteria, and the utc time code of the oldest entry.

        """
        # TODO: I'm sure this needs to check to see if the bot has access to
        #  the moderator log.
        log.debug(f'tally_moderator_actions: {history_limit}' 
                  f'{subreddit.display_name} {user_names} {actions_names}')
        return_data = {}
        oldest_entry = None
        for log_entry in subreddit.mod.log(limit=history_limit):

            # Filters : A list of users was specified and mod wasn't found.
            if len(user_names) != 0 and log_entry._mod not in user_names:
                continue

            # If an action name list was given and it wasn't in it.
            if len(actions_names) != 0 and \
                    log_entry.action not in actions_names:
                continue

            # Initialize or Update Oldest Entry
            if oldest_entry is None or log_entry.created_utc < oldest_entry:
                oldest_entry = log_entry.created_utc

            # Check if actor exists
            if log_entry._mod not in return_data:
                return_data[log_entry._mod] = {}

            # New Action for actor
            if log_entry.action not in return_data[log_entry._mod]:
                return_data[log_entry._mod][log_entry.action] = 1

            # Increment
            return_data[log_entry._mod][log_entry.action] += 1

            await asyncio.sleep(0.001)

        # add in the names on the list who no actions were found for.
        for user in user_names:
            if user not in return_data.keys():
                return_data[user] = {}

        log.debug(
            f'tally_moderator_actions data: {return_data}, {oldest_entry}')
        return return_data, oldest_entry

    async def run(self, target: discord.abc.Messageable) -> None:
        # TODO : make interactive, respect 2000 line limit.
        log.info(f'Started ModStats display...{vars(target)}')

        # Warn user for delay
        await target.send(f'Tallying {self._count} log entries...')
        await self.prepare_data()

        await target.send(
            self._prefix + self._display_table.get_string() +
            self._suffix)
        await target.send(
            self._prefix + self._key_table.get_string() + '\n' +
            'Oldest log:' + await self.oldest_string + self._suffix)

        # message = await target.send(await self.table_display)
        # Interactive Loop
        # while True:
        #    pass
        # display chart
        # set key icon
        # set page up/down if scrollable.
        # set eject/stop
        # wait for reaction from auth user
        # key?
        #   change key to page :page_with_curl:
        #   refresh display to the key
        #   make sure it doesn't exeed size limit to.
        #   remove scroll when apropro
        #   add scroll back when done
        #   this can all just be a binary flip flop display
        # up/down -> scroll display when appropriate
        # eject/stop -> normal results, exit or exit leaving display
        # timout removes display.


class PythonDataDisplay:
    """This class will take and paginate and format python data output. """
    pass


def setup(bot: disextc.Bot) -> None:
    """ Loads discord cog. """
    bot.add_cog(Discord(bot))
