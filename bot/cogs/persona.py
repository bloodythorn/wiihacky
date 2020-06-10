import discord.ext.commands as disextc
from random import choice

# TODO: Wait/one moment question/statement

# TODO: Move these eventually to their own module.
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
    'error', 'wrong', 'try again', 'psych', 'no can do',
    'Clarify?', 'Wut da hell?', '...:', 'Hmm?', """Beg'pardon?""",
    'Like I really have nothing better to do than listen to you babble...',
    """User don't know what they want""", 'got bad event:', 'Figure it out.']
# TODO: Flesh out insults.
txt_insults = [
    """You're spare parts, bub.""",
    """I bet you write Taylor Swift lyrics inside greeting cards.""",
    """What’s up with your body hair, Big Shots?""" +
    """ You look like a 12 year old Dutch girl.""",
    """Buddy, you couldn’t wheel a tire down a hill.""",
    "I bet you know exactly how many days there are until Christmas.",
    "You need to take about 20% of the top there, bub.",
    """Let's take about 5 to 10 percent off 'er over there.""",
]


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

    # Properties

    @property
    async def random_error(self) -> str:
        """ This property returns random errors.

        :return str containing random error.
        """
        return choice(txt_errors)

    @property
    async def random_insult(self) -> str:
        """ This property returns a random insult.

        :return str containing random insult.
        """
        return choice(txt_insults)

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

    # Persona Group Commands

    @disextc.group(name='per', hidden=True)
    @disextc.is_owner()
    async def persona_group(self, ctx: disextc.Context):
        """ The grouping for all persona commands. """
        if ctx.invoked_subcommand is None:
            # TODO : Collectively pull this from menusys (in all cogs)
            await ctx.send(f'persona subcommand not found.')

    @persona_group.command(name='randerr', hidden=True)
    @disextc.is_owner()
    async def get_random_error(self, ctx: disextc.Context):
        """ Access to the random error getter. """
        await ctx.send(await self.random_error)

    @persona_group.command(name='randins', hidden=True)
    @disextc.is_owner()
    async def get_random_insult(self, ctx: disextc.Context):
        """ Access to the random insult getter. """
        await ctx.send(await self.random_insult)

    @persona_group.command(name='randyes', hidden=True)
    @disextc.is_owner()
    async def get_random_yes(self, ctx: disextc.Context):
        """ Access to the random confirmation getter. """
        await ctx.send(await self.random_confirmation)

    @persona_group.command(name='randno', hidden=True)
    @disextc.is_owner()
    async def get_random_no(self, ctx: disextc.Context):
        """ Access to the random rejection getter. """
        await ctx.send(await self.random_rejection)


def setup(bot: disextc.Bot) -> None:
    """ Loads Persona cog. """
    bot.add_cog(Persona(bot))
