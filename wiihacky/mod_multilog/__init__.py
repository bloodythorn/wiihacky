import asyncio
import discord
import logging as lg

# Global Variables
default_level_all = lg.INFO
default_level_wiihacky = lg.DEBUG
default_level_discord = lg.DEBUG
default_level_reddit = lg.CRITICAL
#
bot_cli_channel = ('r/WiiHacks', 'bot_cli')


# TODO: Send to file.
# TODO: Reddit out
async def send_to_log(
        log: lg.Logger,
        dclient: discord.Client,
        text: str,
        lvl=lg.DEBUG):
    """
    Outputs a log message.

    Sends to the logging facilities to be printed in all manners
    demanded. The default level is debug, for quicker coding.

    Sending to logging is determined by the log level.
    Sending to mod_discord has to be checked against a setting.
    Sending to mod_reddit also has to be checked against a setting but should
        never be set beyond critical, as you don't want to spam mod_reddit
        log messages.

    :param log: a logging.Logger class for output.
    :param dclient: mod_discord.Client class for output.
    :param text: The message to be output.
    :param lvl: The log level the message is intended for.
    :return: None
    """
    # Check for mod_discord output
    log.log(level=lvl, msg=text)
    if dclient.is_ready() and lvl >= default_level_discord:
        from logging import getLevelName
        from mod_discord import send_message
        await send_message(
            log, dclient,
            bot_cli_channel[0],
            bot_cli_channel[1],
            getLevelName(lvl) + ':' + text)
