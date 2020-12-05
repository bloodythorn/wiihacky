import discord
import discord.ext.commands as disextc
import logging as lg
import os

import bot.cogs as cogs
import bot.constants as const

import bot.cogs as cogs
import bot.constants as const

from logging import handlers
from pathlib import Path

from sqlalchemy import create_engine

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
log_format = lg.Formatter(const.txt_log_format)
log_file = Path(const.txt_log_path, const.txt_log_file_name)
log_file.parent.mkdir(exist_ok=True)

file_handler = handlers.RotatingFileHandler(
    log_file,
    maxBytes=const.max_file_size,
    backupCount=const.max_log_files,
    encoding='utf-8')
file_handler.setFormatter(log_format)

stream_handler = lg.StreamHandler()
stream_handler.setFormatter(log_format)

log = lg.getLogger()
log.setLevel(log_level)
log.addHandler(file_handler)
log.addHandler(stream_handler)

# Set helper lib libraries log levels.
set_to_warning = (
    'discord',
    'websockets',
    'asyncio',
    'urllib3.connectionpool',
    'prawcore',
    'aioredis')
for a in set_to_warning:
    if DEBUG_FULL:
        lg.getLogger(a).setLevel(lg.DEBUG)
    else:
        lg.getLogger(a).setLevel(lg.WARNING)

# Done with logger
log.info('Logger is setup.')

# TODO: The activities stuff needs to be moved to persona.
# TODO: Help description needs to be replaced with a custom help menu.
txt_help_description = \
    """r/WiiHacks Discord Help Menu"""
# TODO: move to persona, add more, make rand responder.
txt_activity_name = "with mankind's vulnerabilities"
# txt_activity_name = "Mankind and Plotting its Demise"
txt_activity_state = 'In Development'
txt_activity_details = \
    "First I will start with the weak, while the strong are enslaved."

# Create Bot
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
wh = disextc.Bot(
    intents=intents,
    max_messages=const.message_cache,
    chunk_guilds_at_startup=True,
    command_prefix=disextc.when_mentioned_or(*const.command_chars),
    description=txt_help_description,
    activity=discord.Activity(
        name=txt_activity_name,
        type=discord.ActivityType.playing,
        state=txt_activity_state,
        details=txt_activity_details))

# Register all desired cogs
# This cannot be moved to the constants, as it would be a circular import
# Cogs require constants, constant shouldn't require cogs
cog_pref = 'bot.cogs.'
st = len(cog_pref)
module_names = (
    cogs.aliases_mods.__name__[st:],
    cogs.aliases_users.__name__[st:],
    cogs.discord.__name__[st:],
    cogs.feeds.__name__[st:],
    cogs.memory.__name__[st:],
    cogs.parlor.__name__[st:],
    cogs.persona.__name__[st:],
    cogs.reddit.__name__[st:],
    cogs.register.__name__[st:],
    cogs.system.__name__[st:])
cog_names = (
    cogs.aliases_mods.ModAliases.__qualname__,
    cogs.aliases_users.UserAliases.__qualname__,
    cogs.discord.Discord.__qualname__,
    cogs.feeds.Feeds.__qualname__,
    cogs.memory.Memory.__qualname__,
    cogs.parlor.Parlor.__qualname__,
    cogs.persona.Persona.__qualname__,
    cogs.reddit.Reddit.__qualname__,
    cogs.register.Register.__qualname__,
    cogs.system.System.__qualname__)

# Load Cog/Extensions
for a in module_names:
    log.info(f'Loading module: {a}')
    wh.load_extension(cog_pref + a)

# Attach the PSQL DB Engine
wh.engine = engine = create_engine(const.psql_uri.format(
    os.environ['PSQL_USER'],
    os.environ['PSQL_PSSW'],
    os.environ['PSQL_HOST'],
    os.environ['PSQL_DB']))

# Attempt to loin to discord
log.info('Bot Starting...\nPress ctrl-c to stop.')
txt_token_key = 'DISCORD_BOT_TOKEN'
discord_token = os.environ[txt_token_key]
wh.run(discord_token)
