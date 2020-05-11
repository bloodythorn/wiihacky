import discord
import discord.ext.commands as disextc

# Constants

reserved_commands = [
    'giphy', 'tenor', 'tts', 'me', 'tableflip',
    'unflip', 'shrug', 'spoiler']

__version__ = 'v0.0.2'
text_wh_version = 'wiihacky_version'
id_bloodythorn = 574629343142346757
id_wiihacks = 582816924359065611
id_wiihacky = 630280409137283085

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


# Helpers

async def paginate(
        message: str,
        pag: disextc.Paginator = None
        ) -> disextc.Paginator:
    """ Helper to use the Paginator.

    Given a line of text it will format it and return the paginator to add
    more lines.

    :param message -> str type with message to send
    :param pag -> Pagenator to add to, or none to create a new.
    :return -> Paginator containing line of text.
    """
    if pag is None:
        pag = disextc.Paginator()
    pag.add_line(message)
    return pag


async def send_paginator(
        to: discord.abc.Messageable,
        pag: disextc.Paginator) -> None:
    """ Helper to send a paginator.

    Given a messageable and a paginator, this function will send the
    paginator the target.

    :param to -> Messageable recipient.
    :param pag -> Pagenator to send.
    :return None
    """
    for page in pag.pages:
        await to.send(page)
