import aiohttp
import discord
import discord.ext.commands as disextc
import logging as lg
import os

from logging import handlers
from pathlib import Path

import bot.cogs as cogs

from dotenv import load_dotenv
load_dotenv()

# Set Debug Level: Pull debug mode from env
DEBUG_MODE = None
if 'DEBUG' in os.environ:
    DEBUG_MODE = os.environ['DEBUG']

DEBUG_FULL = None
if 'DEBUG_FULL' in os.environ:
    DEBUG_FULL = os.environ['DEBUG_FULL']

# Prep Logger
log_level = lg.DEBUG if DEBUG_MODE else lg.INFO
log_format_string = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
log_format = lg.Formatter(log_format_string)

log_file = Path('logs', 'botlog.log')
log_file.parent.mkdir(exist_ok=True)
log_file_count = 50
max_file_size = 2**16 * 8 * 2
file_handler = handlers.RotatingFileHandler(
    log_file,
    maxBytes=max_file_size,
    backupCount=log_file_count,
    encoding='utf-8')
file_handler.setFormatter(log_format)

stream_handler = lg.StreamHandler()
stream_handler.setFormatter(log_format)

log = lg.getLogger()
log.setLevel(log_level)
log.addHandler(file_handler)
log.addHandler(stream_handler)

# Set helper lib libraries log levels.
set_to_warning = ('discord', 'websockets', 'asyncio', 'urllib3.connectionpool',
                  'prawcore', 'aioredis')
for a in set_to_warning:
    if DEBUG_FULL:
        lg.getLogger(a).setLevel(lg.DEBUG)
    else:
        lg.getLogger(a).setLevel(lg.WARNING)

log.info('Logger is setup.')

# Module Constants
command_chars = ('^',)
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
cog_pref = 'bot.cogs.'
st = len(cog_pref)
module_names = (
    cogs.aliases_mods.__name__[st:],
    cogs.aliases_users.__name__[st:],
    cogs.config.__name__[st:],
    cogs.discord.__name__[st:],
    cogs.memory.__name__[st:],
    cogs.persona.__name__[st:],
    cogs.reddit.reddit.__name__[st:],
    cogs.reddit.feeds.__name__[st:],
    cogs.register.__name__[st:],
    cogs.system.__name__[st:])
cog_names = (
    cogs.aliases_mods.ModAliases.__qualname__,
    cogs.aliases_users.UserAliases.__qualname__,
    cogs.config.Config.__qualname__,
    cogs.discord.Discord.__qualname__,
    cogs.memory.Memory.__qualname__,
    cogs.persona.Persona.__qualname__,
    cogs.reddit.reddit.Reddit.__qualname__,
    cogs.reddit.feeds.Feeds.__qualname__,
    cogs.register.Register.__qualname__,
    cogs.system.System.__qualname__)

# Load Cog/Extensions
for a in module_names:
    log.info(f'Loading module: {a}')
    wh.load_extension(cog_pref + a)

# TODO: Retry/fail attempts
# Attempt to loin to discord
try:
    log.info('Bot Starting...')
    # Check to make sure we have a token
    txt_token_key = 'DISCORD_BOT_TOKEN'
    discord_token = os.environ[txt_token_key]
    wh.run(discord_token)
except KeyError as e:
    log.critical('DISCORD_BOT_TOKEN not set in env.')
    exit(-1)
except discord.errors.LoginFailure as e:
    log.error(f'Failed to login with given token: {e.args}')
    exit(-1)
except aiohttp.ClientConnectionError as e:
    log.error(f'Failed to login to discord: {e.args}')
    exit(-1)
except RuntimeError as e:
    log.info(f'Loop experienced a runtime error: {e.args}')
    exit(0)
