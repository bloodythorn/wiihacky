import discord.ext.commands as disextc


reserved_commands = [
    'giphy', 'tenor', 'tts', 'me', 'tableflip',
    'unflip', 'shrug', 'spoiler']

__version__ = 'v0.0.2'
text_wh_version = 'wiihacky_version'
id_bloodythorn = 574629343142346757
id_wiihacks = 582816924359065611
id_wiihacky = 630280409137283085


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


async def paginate(
        message: str,
        pag: disextc.Paginator = disextc.Paginator()
        ) -> disextc.Paginator:
    """ Helper to use the Paginator.

    TODO: Document
    """
    pag.add_line(message)
    return pag


async def send_paginator(ctx: disextc.Context, pag: disextc.Paginator):
    """ Helper to send a paginator.

    # TODO: Document
    """
    for page in pag.pages:
        await ctx.send(page)
