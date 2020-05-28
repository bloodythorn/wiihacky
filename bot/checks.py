import discord.ext.commands as disextc

from .constants import id_wiihacks, id_wiihacky, id_bloodythorn


# Checks

@disextc.check
async def is_developer():
    """ Check to see if author id is the developer. """
    async def predicate(ctx):
        return ctx.author.id == id_bloodythorn
    return disextc.check(predicate)


@disextc.check
async def is_wiihacks():
    """ Check to see if the message came from the official discord. """
    async def predicate(ctx: disextc.Context):
        return ctx.guild.id == id_wiihacks
    return disextc.check(predicate)


@disextc.check
async def is_wiihacky():
    """ Check to see if the message came from the official bot. """
    async def predicate(ctx: disextc.Context):
        return ctx.guild.id == id_wiihacky
    return disextc.check(predicate)


