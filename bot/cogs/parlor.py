import asyncio
import discord.ext.commands as disextc
import logging as lg
import numpy as np
import re


__version__ = '0.0.2'
regex_die_roll = re.compile(
    r"^([0-9]{,2})d([0-9]{1,2})(?:([+|-])([0-9]{1,2}))?(?:x([0-9]{1,2}))?$")
log = lg.getLogger(__name__)

# TODO: Store/retrieve/delete results, print results in different formats.
# TODO: Cards

class Parlor(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

    @staticmethod
    async def dice_roll(roll: str) -> str:
        # Run Regex search
        try:
            result = re.findall(regex_die_roll, roll)[0]
        except IndexError:
            return "Could not identify a die roll."

        log.debug(f'dice regex result:{result}')

        # Setup operation
        sides = int(result[1])
        dice = int(result[0]) if result[0] != '' else 1
        times = int(result[4]) if result[4] != '' else 1

        dice = np.random.random_integers(1, high=sides, size=(times, dice))

        add_sub = result[2]
        modifier = int(result[3]) if result[3] != '' else None
        if modifier is not None:
            modifier *= 1 if add_sub == '+' else -1
            dice += modifier

        return dice

    # TODO: Clean up result display
    @disextc.command(name='roll')
    @disextc.is_owner()
    async def roll_dice_command(self, ctx: disextc.Context, *args):
        """ Roll a dice set. Dice set must be in the format '1d6+1x6'.
            The number of dice, the modifier and the multiplier are all
            optional.
        """
        await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
        results = map(self.dice_roll, args)
        await ctx.send(f'results:\n{await asyncio.gather(*results)}')


def setup(bot: disextc.Bot) -> None:
    """ Loads memory cog. """
    bot.add_cog(Parlor(bot))
