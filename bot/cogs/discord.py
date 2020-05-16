import discord as discord
import discord.ext.commands as disextc
import typing as typ

txt_cog_sub_err = 'Invalid discord command.'


# TODO: Welcomer
# TODO: Top TODOs
#   Flesh out commands.
#   make a defaults system

# TODO: moderator functions
# TODO: Add logging to functions
#   Logging will need a state of a list of tuples storing guild/channel
# TODO: To prevent botspam, the main help engine might only want to invoke
#   in a single channel instead of other channels, then ping the user....
#   sooo a CLI and a log channel? Log private? CLI Public?
# TODO: cache_messages
#   This might require a 'reader'
# TODO: Allowed mentions
# Some of the following might already be implemented in id.
# TODO: get channel, guild, user, emoji, all_channels, all_members,
# TODO: Yes/no confirmation prompt with reactions, that should belong here.
# TODO: Change presence
# TODO: Fetch Guilds -> Might need to make a bot-testing guild.
# TODO: Pins -> Identify and cache files, especially syschecks.
# TODO: Create Guild ?
# TODO: Invites
# TODO: Widgets?
# TODO: Webhooks
# TODO: Teams
# TODO: Create Group Chat.


class Discord(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        from constants import paginate, send_paginator
        self.paginate = paginate
        self.send_paginator = send_paginator

    # Helpers
    async def get_owner(self) -> discord.User:
        await self.bot.wait_until_ready()
        appinfo: discord.AppInfo = await self.bot.application_info()
        return appinfo.owner

    # Discord Cog Listeners

    @disextc.Cog.listener(name='on_reaction_add')
    async def angry_axe_listener(
            self, reaction: discord.Reaction, user: discord.User) -> None:
        """ Listener for Angry Axe™.

        on_reaction_add this function inspects the message and user adding the
        reaction to determine whether or not the message will be deleted.
        This is originally developed as a troubleshooting tool to delete the
        bot's DMs.

        :param reaction -> The reaction that caused the event.
        :param user -> The user that added the reaction.
        :return None
        """
        # TODO: FINISH THIS/FIX THIS
        emoji_anger = '💢'
        emoji_axe = '🪓'
        from constants import id_bloodythorn
        if reaction.emoji == emoji_axe or reaction.emoji == emoji_anger:
            if isinstance(reaction.message.channel, discord.DMChannel) and \
               reaction.message.author == self.bot.user:
                await reaction.message.delete()
                # else do nothing.
            # FIXME: This needs to be more security accessable.
            elif isinstance(reaction.message.channel, discord.TextChannel) and \
                    user.id == id_bloodythorn:
                await reaction.message.delete()

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

    @discord_group.command(hidden=True)
    @disextc.is_owner()
    async def activity(self, ctx: disextc.Context) -> None:
        """ Read Bot Activity.

        This currently only retrieves and prints the bot activity.

        :param ctx -> Invocation context
        :return None
        """
        # TODO: Expand this to a group and add more control.
        # TODO: Paginate the result
        me = discord.utils.get(self.bot.get_all_members(), id=self.bot.user.id)
        await self.send_paginator(ctx, await self.paginate(repr(me.activities)))

    @discord_group.command(hidden=True)
    @disextc.is_owner()
    async def id(self, ctx: disextc.Context, what: typ.Union[
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

    @discord_group.command(hidden=True)
    @disextc.is_owner()
    async def guilds(self, ctx: disextc.Context) -> None:
        """ Guild list.

        :param ctx -> Invocation Context
        """
        # TODO Paginate better
        await self.send_paginator(
            ctx, await self.paginate(
                repr([a.name for a in list(self.bot.guilds)])))

    @discord_group.command(hidden=True)
    @disextc.is_owner()
    async def latency(self, ctx: disextc.Context) -> None:
        """ Reads client latency.

        This returns the latency the client is currently under.

        :param ctx -> Invocation context.
        :return None
        """
        # TODO Paginate better
        await self.send_paginator(
            ctx, await self.paginate(repr(self.bot.latency)))

    @discord_group.command(hidden=True)
    @disextc.is_owner()
    async def status(self, ctx: disextc.Context) -> None:
        """ Status of the Bot.

        This will read out the current status of the bot.

        :param ctx -> Invocation context.
        :return None
        """
        me = discord.utils.get(self.bot.get_all_members(), id=self.bot.user.id)
        await self.send_paginator(ctx, await self.paginate(repr(me.status)))

    @discord_group.command(hidden=True)
    @disextc.is_owner()
    async def version(self, ctx: disextc.Context) -> None:
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

    @channel_group.command(hidden=True)
    @disextc.is_owner()
    async def pos(self, ctx: disextc.Context,
                  channel: typ.Union[discord.TextChannel,
                                     discord.VoiceChannel]
                  ) -> None:
        """ Channel Position in List. """
        # TODO: Getter/setter by adding another arg that's an integer.
        #   Also a requirement is that the channel is refered to by ID
        #   if the set command is used.
        await self.send_paginator(
            ctx, await self.paginate(repr(channel.position)))

    @channel_group.command(hidden=True)
    @disextc.is_owner()
    async def private(self, ctx: disextc.Context):
        """ List private channels. """
        # TODO: Channel functions -> Close, create, delete, permissions
        await self.send_paginator(
            ctx, await self.paginate(repr(self.bot.private_channels)))

    @channel_group.command(hidden=True)
    @disextc.is_owner()
    async def voice(self, ctx: disextc.Context):
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
