import discord
import logging as lg


async def send_message(
        log: lg.Logger = None,
        dclient: discord.Client = None,
        guild_name: str = None,
        chan_name: str = None,
        text: str = None):
    guild: discord.Guild = discord.utils.find(
        lambda a: a.name == guild_name, dclient.guilds)

    if guild is None:
        log.error(f'Could not find guild: {guild_name}')
        return f'Could not find guild: {guild_name}'

    channel: discord.TextChannel = discord.utils.find(
        lambda a: a.name == chan_name, guild.channels)

    if channel is None:
        TXT_ERR_CHAN_NOT_FOUND = \
            f'Could not find channel {chan_name} in guild {guild_name}'
        log.error(TXT_ERR_CHAN_NOT_FOUND)
        return TXT_ERR_CHAN_NOT_FOUND
    await channel.send(text)
