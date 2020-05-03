import discord as discord
import discord.ext.commands as disextc
import typing as typ

txt_cog_sub_err = 'Invalid discord command.'

# TODO: Client Stuff:
# TODO: Add logging to functions
# TODO: discord.version_info __version__
# TODO: User
# TODO: Activity
# TODO: Status
# TODO: latency
# TODO: Guilds
# TODO: cache_messages
# TODO: private channels
# TODO: voice clients
# TODO: Fix emj
# TODO: Allowed mentions
# TODO: Users
# Some of the following might already be implemented in id.
# TODO: get channel, guild, user, emoji, all_channels, all_members,
# TODO: Yes/no confirmation prompt with reactions, that should belong here.
# TODO: Change presence
# TODO: Fetch Guilds -> Might need to make a bot-testing guild.
# TODO: Pins -> Identify and cache files, especially syschecks.
# TODO: Create Guild
# TODO: Invites
# TODO: Widgets?
# TODO: Application info
# TODO: Webhooks
# TODO: Teams
# TODO: Voice?



class Discord(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

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
        from wiihacky import id_bloodythorn
        if reaction.emoji == emoji_axe or reaction.emoji == emoji_anger:
            if isinstance(reaction.message.channel, discord.DMChannel) and \
               reaction.message.author == self.bot.user:
                await reaction.message.delete()
                # else do nothing.
            # FIXME: This needs to be more security accessable.
            elif isinstance(reaction.message.channel, discord.TextChannel) and \
                    user.id == id_bloodythorn:
                await reaction.message.delete()

    # Discord Commands

    @disextc.group()
    @disextc.is_owner()
    async def dis(self, ctx: disextc.Context):
        """ Discord Subgroup. """
        # TODO: This should pull up subgroup help., Document
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @dis.command()
    @disextc.is_owner()
    async def act(self, ctx: disextc.Context) -> None:
        """ Bot Activity.

        This currently only retrieves and prints the bot activity.
        :param ctx -> Invocation context
        :return
        """
        # TODO: Expand this to a group and add more control.
        pass

    @dis.command()
    @disextc.is_owner()
    async def id(self, ctx: disextc.Context, what: typ.Union[
                     discord.Member,
                     discord.TextChannel,
                     discord.User,
                     discord.Message,
                     discord.Guild,
                     ]) -> None:
        """ ID member, txtchannel, user, message, guild.

        This function will take a string and see if it is a member, txtchannel,
        user, message, guild, in that order.
        """
        out = disextc.Paginator()
        out.add_line(repr(what))
        for page in out.pages:
            await ctx.send(page)

    # TODO: Status
    @dis.command()
    @disextc.is_owner()
    async def stat(self, ctx: disextc) -> None:
        """ Status of the Bot. """
        await ctx.send("TODO")

    @dis.group()
    @disextc.is_owner()
    async def msg(self, ctx: disextc.Context):
        """ Discord Messaging related commands.

        :param ctx -> Invocation context
        :return None
        """
        # TODO: Invoke help
        if ctx.invoked_subcommand is None:
            await ctx.send(txt_cog_sub_err)

    @msg.command()
    @disextc.is_owner()
    async def chn(self, ctx: disextc.Context,
                     chan: discord.TextChannel, *, mesg: str) -> None:
        """ Message to Channel.

        Given an identifiable channel name and string it will send the string
        to the channel as the bot.

        :param ctx -> Context
        :param chan -> Channel to send to.
        :param mesg -> String to send to channel.
        """
        # TODO: use ctx in log output
        await chan.send(mesg)

    @msg.command()
    @disextc.is_owner()
    async def mem(self, ctx: disextc.Context,
                  member: discord.Member, *, mesg: str) -> None:
        """ Message Member.

        Given an identifiable member name and string it will send the string
        to the member as the bot.

        :param ctx -> Context command was sent from.
        :param member -> Member to send message to.
        :param mesg -> String to sent to member.
        :return None
        """
        await member.send(mesg)

    @msg.command()
    @disextc.is_owner()
    async def delete(self, ctx: disextc.Context, mesg: discord.Message) -> None:
        """ Deletes given message.

        Given a message this function will remove it.

        :param ctx -> Context required by command
        :param mesg -> Message to be deleted
        :return None
        """
        await mesg.delete()

    @msg.command()
    @disextc.is_owner()
    async def dev(self, ctx: disextc.Context, *, mesg: str):
        """ Message the developer.

        Messages the hardcoded developer ID. If the ID is not found it will
        throw a badargument exception.

        :param ctx Context the message was invoked in
        :param mesg The text message to send.
        """
        from wiihacky import id_bloodythorn
        dev: discord.User = self.bot.get_user(id_bloodythorn)
        snd = f'From:{ctx.author}|Where:{ctx.channel}|:-> {mesg}'
        if dev is not None:
            await dev.send(snd)
        else:
            raise disextc.BadArgument(
                'Developer could not be found on discord!')

    @disextc.command()
    @disextc.is_owner()
    async def emj(self, ctx: disextc.Context):
        """ Lists custom emojis. """
        pages = disextc.Paginator()
        pages.add_line(repr(ctx.bot.emojis))
        for page in pages.pages:
            await ctx.send(page)

