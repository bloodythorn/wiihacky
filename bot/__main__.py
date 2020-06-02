import aiohttp
import discord
import discord.ext.commands as disextc
import logging as lg
import os

from logging import handlers
from pathlib import Path

import cogs

# Set Debug Level: Pull debug mode from env
DEBUG_MODE = None
if 'DEBUG' in os.environ:
    DEBUG_MODE = os.environ['DEBUG']

# Prep Logger
log_level = lg.DEBUG if DEBUG_MODE else lg.INFO
log_format_string = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
log_format = lg.Formatter(log_format_string)

log_file = Path('logs', 'botlog.log')
log_file.parent.mkdir(exist_ok=True)
file_handler = handlers.RotatingFileHandler(
    log_file, maxBytes=524880, backupCount=10, encoding='utf-8')
file_handler.setFormatter(log_format)

stream_handler = lg.StreamHandler()
stream_handler.setFormatter(log_format)

log = lg.getLogger()
log.setLevel(log_level)
log.addHandler(file_handler)
log.addHandler(stream_handler)

# Set helper lib libraries log levels.
lg.getLogger('discord').setLevel(lg.WARNING)
lg.getLogger('websockets').setLevel(lg.WARNING)
lg.getLogger('asyncio').setLevel(lg.WARNING)
lg.getLogger('urllib3.connectionpool').setLevel(lg.WARNING)
lg.getLogger('prawcore').setLevel(lg.WARNING)

log.info('Logger is setup.')

# A grouping of all installed cogs
installed_cogs = (
    cogs.config.Config.qualified_name,
    cogs.discord.Discord.qualified_name,
    cogs.memory.Memory.qualified_name,
    cogs.menusys.MenuSys.qualified_name,
    cogs.persona.Persona.qualified_name,
    cogs.reddit.Reddit.qualified_name,
    cogs.reddit.Feeds.qualified_name,
    cogs.security.Security.qualified_name,)

# Module Constants
command_chars = ('!',)
message_cache = 1000 * 10
txt_help_description = \
    """r/WiiHacks Discord Help Menu"""
txt_activity_name = "Mankind and Plotting its Demise"
txt_activity_state = 'In Development'
txt_activity_details = \
    "First I will start with the weak, while the strong are enslaved."

# Create Bot
wh = disextc.Bot(
    max_messages=message_cache,
    command_prefix=disextc.when_mentioned_or(*command_chars),
    fetch_offline_members=True,
    description=txt_help_description,
    activity=discord.Activity(
        name=txt_activity_name,
        type=discord.ActivityType.watching,
        state=txt_activity_state,
        details=txt_activity_details))

# Load Cog/Extensions
wh.load_extension('cogs.config')
wh.load_extension('cogs.discord')
wh.load_extension('cogs.memory')
wh.load_extension('cogs.menusys')
wh.load_extension('cogs.persona')
wh.load_extension('cogs.reddit')
wh.load_extension('cogs.security')
wh.load_extension('cogs.system')

# TODO: Retry/fail attempts
# Attempt to loin to discord
try:
    log.info('Bot Starting...')
    # Check to make sure we have a token
    import os
    txt_token_key = 'DISCORD_BOT_TOKEN'
    discord_token = os.environ[txt_token_key]
    wh.run(discord_token)
except KeyError as e:
    log.critical('DISCORD_BOT_TOKEN not set in env.')
    exit(-1)
except discord.errors.LoginFailure as e:
    log.error('Failed to login with given token: {}'.format(e.args))
    exit(-1)
except aiohttp.ClientConnectionError as e:
    log.error(f'Failed to login to discord: {e.args}')
    exit(-1)
except RuntimeError as e:
    log.info('Loop experienced a runtime error: {}'.format(e.args))
    exit(0)
