import discord as dis
import discord.ext.commands as dec
import typing as typ

tt = '```'


# TODO: error handler on_command_error needs to be listened.
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.on_command_error


class Discord(dec.Cog):

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot

    # Discord Cog Listeners

    @dec.Cog.listener(name='on_reaction_add')
    async def angry_axe_listener(
            self, reaction: dis.Reaction, user: dis.User) -> None:
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
        emoji_axe = '🪓'
        emoji_anger = '💢'
        from wiihacky import id_bloodythorn
        if reaction.emoji == emoji_axe or reaction.emoji == emoji_anger:
            if isinstance(reaction.message.channel, dis.DMChannel) and \
               reaction.message.author == self.bot.user:
                await reaction.message.delete()
                # else do nothing.
            # FIXME: This needs to be more security accessable.
            elif isinstance(reaction.message.channel, dis.TextChannel) and \
                    user.id == id_bloodythorn:
                await reaction.message.delete()

    @dec.command()
    @dec.is_owner()
    async def id(
            self, ctx: dec.Context,
            what: typ.Union[dis.TextChannel, dis.Member]) -> None:
        """ ID channel or member.

        This function will take a string and see if it is a channel, or member
        in that order.
        """
        out = dec.Paginator()
        out.add_line(repr(what))
        for page in out.pages:
            await ctx.send(page)

    @id.error
    async def error_id(self, ctx: dec.Context, error) -> None:
        await ctx.send(f'Could not ID: {error}')

    @dec.command()
    @dec.is_owner()
    async def msgchn(self,
                     ctx: dec.Context,
                     chan: dis.TextChannel,
                     *, mesg: str) -> None:
        """ Message to Channel.

        Given an identifiable channel name and string it will send the string
        to the channel as the bot.

        :param ctx -> Context
        :param chan -> Channel to send to.
        :param mesg -> String to send to channel.
        """
        await chan.send(mesg)

    @dec.command()
    @dec.is_owner()
    async def msgmem(self,
                     ctx: dec.Context,
                     member: dis.Member,
                     *, mesg: str) -> None:
        """ Message Member.

        Given an identifiable member name and string it will send the string
        to the member as the bot.

        :param ctx -> Context command was sent from.
        :param member -> Member to send message to.
        :param mesg -> String to sent to member.
        :return None
        """
        await member.send(mesg)

    @msgchn.error
    @msgmem.error
    async def error_msg(self, ctx: dec.Context, error):
        await ctx.send(f'Could not send message: {error}')

    @dec.command()
    @dec.is_owner()
    async def msgdel(self, ctx: dec.Context, mesg: dis.Message) -> None:
        """ Deletes given message.

        Given a message this function will remove it.

        :param ctx -> Context required by command
        :param mesg -> Message to be deleted
        :return None
        """
        await mesg.delete()

    @msgdel.error
    async def msgdel(self, ctx: dec.Context, error):
        await ctx.sent(f'Could not delete message: {error}')

    @dec.command()
    @dec.is_owner()
    async def msgdev(self, ctx: dec.Context, *, msg: str):
        """ Message the developer.

        Messages the hardcoded developer ID. If the ID is not found it will
        throw a badargument exception.

        :param ctx Context the message was invoked in
        :param msg The text message to send.
        """
        from wiihacky import id_bloodythorn
        dev: dis.User = self.bot.get_user(id_bloodythorn)
        snd = f'From:{ctx.author}|Where:{ctx.channel}|:-> {msg}'
        if dev is not None:
            await dev.send(snd)
        else:
            raise dec.BadArgument('Developer could not be found on discord!')

