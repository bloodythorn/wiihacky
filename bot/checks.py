import discord.ext.commands as disextc
import logging as lg

# from .constants import id_wiihacks, id_wiihacky, id_bloodythorn
import constants


# Log instance for this module
log = lg.getLogger(__name__)


# Checks

def is_developer():
    """ Check to see if author id is the developer. """
    async def predicate(ctx: disextc.Context) -> bool:
        return ctx.author.id == constants.id_bloodythorn
    return disextc.check(predicate)


def is_wiihacks():
    """ Check to see if the message came from the official discord. """
    async def predicate(ctx: disextc.Context) -> bool:
        return ctx.guild.id == constants.id_wiihacks
    return disextc.check(predicate)


def is_wiihacky():
    """ Check to see if the message came from the official bot. """
    async def predicate(ctx: disextc.Context) -> bool:
        return ctx.guild.id == constants.id_wiihacky
    return disextc.check(predicate)


def has_role(role_names):
    async def predicate(ctx: disextc.Context) -> bool:
        exe_roles = [a.name for a in ctx.message.author.roles]
        for role in role_names:
            if role in exe_roles:
                return True
        raise disextc.CommandError(f'You do not have permissions to use this.')
    return disextc.check(predicate)
