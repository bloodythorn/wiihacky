import discord.ext.commands as disextc
from random import choice

txt_positive = [
    '1', 'affirmative', 'agree', 'agreed', 'all right', 'amen', 'aye',
    'beyond a doubt', 'by all means', 'certainly', 'definitely', 'even so',
    'exactly', 'fine', 'gladly', 'good', 'good enough', 'granted',
    'indubitably', 'just so', 'make it so', 'most assuredly', 'naturally',
    'of course', 'ok', 'okay', 'positively', 'precisely', 'sure', 'sure thing',
    'surely', 'true', 'undoubtedly', 'y', 'yah', 'ye', 'yea', 'yeah',
    'yee', 'yes']
txt_negative = [
    '0', 'cancel', 'forget it', 'n', 'nah', 'naw', 'nay', 'negative',
    'negatory', 'never', 'nix', 'no', 'not', 'null', 'refusal', 'refuse',
    'reject', 'rejection']
txt_errors = [
    'error', 'jive turkey', 'wrong', 'try again', 'psych', 'no can do',
    'Clarify?', 'Wut da hell?:', '...:', 'Hmm?', """Beg'pardon?:""",
    'Like I really have nothing better to do than listen to you babble...:',
    """User don't know what they want:"""]


def convert_to_bool(phrase: str):
    """ Convert Phrase to Boolean.

    Attempt to convert a string into a bool type based on a database of
    confirmations.

    :param phrase: str
    :return true, false, or NoneType if cannot determine.
    """
    if phrase in txt_positive:
        return True
    elif phrase in txt_negative:
        return False
    else:
        return None


class Persona(disextc.Cog):
    """ Personality Cog

    This cog handles anything that would dictate how the bot would respond to
    actions, or act in general. Some of these functions will be useful, some
    irreverent. And hopefully I'll eventually develop a way into turning on a
    'dry' mode.
    """

    def __init__(self, bot: disextc.Bot):
        """Initialize cog."""
        super().__init__()
        self.bot = bot

    # Helpers

    @property
    async def random_error(self) -> str:
        """ This property returns random errors.

        :return str containing random error.
        """
        return choice(txt_errors)

    @property
    async def random_confirmation(self) -> str:
        """ This property returns a random confirmation.

        :return str containing random confirmation.
        """
        return choice(txt_positive)

    @property
    async def random_rejection(self) -> str:
        """ This property returns a random rejection.

        :return str containing random rejection.
        """
        return choice(txt_negative)

    # Groups

    @disextc.group(name='per')
    @disextc.is_owner()
    async def persona_group(self, ctx: disextc.Context):
        """ The grouping for all persona commands. """
        if ctx.invoked_subcommand is None:
            # TODO : Collectively pull this from menusys (in all cogs)
            await ctx.send(f'persona subcommand not found.')

    # Commands

    @persona_group.command(name='randerr', is_hidden=True)
    @disextc.is_owner()
    async def get_random_error(self, ctx: disextc.Context):
        """ Access to the random error getter. """
        await ctx.send(await self.random_error)

    @persona_group.command(name='randyes', is_hidden=True)
    @disextc.is_owner()
    async def get_random_yes(self, ctx: disextc.Context):
        """ Access to the random confirmation getter. """
        await ctx.send(await self.random_confirmation)

    @persona_group.command(name='randno', is_hidden=True)
    @disextc.is_owner()
    async def get_random_no(self, ctx: disextc.Context):
        """ Access to the random rejection getter. """
        await ctx.send(await self.random_rejection)


def setup(bot: disextc.Bot) -> None:
    """ Loads Persona cog. """
    bot.add_cog(Persona(bot))
