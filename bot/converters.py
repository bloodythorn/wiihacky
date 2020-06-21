import discord.ext.commands as disextc
import logging as lg

from fuzzywuzzy import process

fuzzy_error = "'{}' too ambiguous for fuzzy id."

log = lg.getLogger(__name__)


class BooleanFuzzyConverter(disextc.Converter):
    """This converter when given an argument will try to determine if it is
    intended to be true or false.
    """
    async def convert(self, ctx: disextc.Context, argument: str):
        from cogs.persona import txt_positive, txt_negative
        n_results = process.extract(argument, txt_negative)
        p_results = process.extract(argument, txt_positive)

        # Let's see what we have....
        negamax_calc = p_results[0][1] - n_results[0][1]
        thresh = 92
        neg = 5
        # Negative gets precedence
        if n_results[0][1] == 100 or \
                (negamax_calc < -1*neg and n_results[0][1] > thresh):
            return False
        elif p_results[0][1] == 100 or \
                (negamax_calc > neg and p_results[0][1] > thresh):
            return True

        # We tried...
        raise disextc.BadArgument(fuzzy_error.format(argument))


class FuzzyLogLevelName(disextc.Converter):
    async def convert(self, ctx, argument: str):
        log.debug(f'FuzzyLog Fired: {argument}')
        from fuzzywuzzy import process
        results = process.extract(argument, lg._nameToLevel.keys())
        log.debug(f'fuzzy results: {results}')
        # if we have an exact match
        if results[0][1] == 100:
            return results[0][0]

        # apply threshold
        if results[0][1] < 75 or results[0][1] - results[1][1] < 5:
            raise disextc.CommandError(f'{argument} too ambiguous')

        # return result if passed.
        return results[0][0]


class FuzzyCogName(disextc.Converter):
    async def convert(self, ctx, argument: str):
        log.debug(f'FuzzyCog Fired: {argument}')
        from fuzzywuzzy import process
        # Can't do this unless the cogs are loaded.
        await ctx.bot.wait_until_ready()
        results = process.extract(argument, ctx.bot.cogs.keys())
        log.debug(f'fuzzy results: {results}')
        # if we have an exact match
        if results[0][1] == 100:
            return results[0][0]

        # Apply threshold
        if (results[0][1] < 75) or (results[0][1] - results[1][1]) < 5:
            raise disextc.CommandError(f"'{argument}' too ambiguous.")

        # return result if passed.
        return results[0][0]
