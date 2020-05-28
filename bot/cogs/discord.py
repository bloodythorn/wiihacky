import discord as discord
import discord.ext.commands as disextc
import typing as typ

txt_cog_sub_err = 'Invalid discord subcommand.'


# TODO: Top TODOs
# TODO: Welcomer
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


class Discord(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        # TODO: Get rid of these
        from constants import paginate, send_paginator
        self.paginate = paginate
        self.send_paginator = send_paginator

    # Helpers

    # TODO: Prolly don't need a function for this.
    async def get_owner(self) -> discord.User:
        await self.bot.wait_until_ready()
        appinfo: discord.AppInfo = await self.bot.application_info()
        return appinfo.owner

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
    async def multi_id_command(self, ctx: disextc.Context, what: typ.Union[
                     discord.Member,
                     discord.TextChannel,
                     discord.VoiceChannel,
                     discord.User,
                     discord.Message,
                     discord.Guild,
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

    @message_group.command(hidden=True)
    @disextc.is_owner()
    async def channel(self, ctx: disextc.Context,
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

    @message_group.command(hidden=True)
    @disextc.is_owner()
    async def member(self, ctx: disextc.Context,
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

    @message_group.command(hidden=True)
    @disextc.is_owner()
    async def delete(self, ctx: disextc.Context,
                     message: discord.Message) -> None:
        """ Deletes given message.

        Given a message this function will remove it.

        :param ctx -> Context required by command
        :param message -> Message to be deleted
        :return None
        """
        await message.delete()

    @message_group.command(hidden=True)
    @disextc.is_owner()
    async def developer(self, ctx: disextc.Context, *, message: str) -> None:
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

    # Uncategorized
    # TODO Emoji group?

    @message_group.command(hidden=True)
    @disextc.is_owner()
    async def emoji(self, ctx: disextc.Context) -> None:
        """ Lists custom emojis.

        This function will return all data on custom emojis.

        :param ctx -> Invocation Context
        :return None
        """
        await self.send_paginator(
            ctx, await self.paginate(repr(ctx.bot.emojis)))


def setup(bot: disextc.Bot) -> None:
    """ Loads discord cog. """
    bot.add_cog(Discord(bot))
