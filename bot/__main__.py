import aiohttp
import discord
import discord.ext.commands as disextc
import logging as lg
import os

from logging import handlers
from pathlib import Path

import cogs

# TODO: Make the log level settable at during runtime.

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

# TODO: Make the logger dynamically setable at runtime.

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
lg.getLogger('aioredis').setLevel(lg.WARNING)


log.info('Logger is setup.')

# Module Constants
command_chars = ('!',)
message_cache = 1000 * 10
txt_help_description = \
    """r/WiiHacks Discord Help Menu"""
# todo: move to persona, add more, make rand responder.
txt_activity_name = "with mankind's vulnerabilities"
# txt_activity_name = "Mankind and Plotting its Demise"
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
        type=discord.ActivityType.playing,
        state=txt_activity_state,
        details=txt_activity_details))

# I believe this needs to be here
module_names = (
    cogs.aliases_mods.__name__[5:],
    cogs.aliases_users.__name__[5:],
    cogs.config.__name__[5:],
    cogs.discord.__name__[5:],
    cogs.laboratory.__name__[5:],
    cogs.memory.__name__[5:],
    cogs.menusys.__name__[5:],
    cogs.persona.__name__[5:],
    cogs.reddit.reddit.__name__[5:],
    cogs.reddit.feeds.__name__[5:],
    cogs.register.__name__[5:],
    cogs.security.__name__[5:],
    cogs.system.__name__[5:])
cog_names = (
    cogs.aliases_mods.ModAliases.__qualname__,
    cogs.aliases_users.UserAliases.__qualname__,
    cogs.config.Config.__qualname__,
    cogs.discord.Discord.__qualname__,
    cogs.laboratory.Laboratory.__qualname__,
    cogs.memory.Memory.__qualname__,
    cogs.menusys.MenuSys.__qualname__,
    cogs.persona.Persona.__qualname__,
    cogs.reddit.reddit.Reddit.__qualname__,
    cogs.reddit.feeds.Feeds.__qualname__,
    cogs.register.Register.__qualname__,
    cogs.security.Security.__qualname__,
    cogs.system.System.__qualname__)

# Load Cog/Extensions
wh.load_extension('cogs.aliases_mods')
wh.load_extension('cogs.aliases_users')
wh.load_extension('cogs.config')
wh.load_extension('cogs.discord')
wh.load_extension('cogs.laboratory')
wh.load_extension('cogs.memory')
wh.load_extension('cogs.menusys')
wh.load_extension('cogs.persona')
wh.load_extension('cogs.reddit.reddit')
wh.load_extension('cogs.reddit.feeds')
wh.load_extension('cogs.register')
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
