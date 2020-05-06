import discord
import logging as lg
import os
from wiihacky import Wiihacky
from logging import handlers
from pathlib import Path


DEBUG_MODE = None
if 'DEBUG' in os.environ:
    DEBUG_MODE = os.environ['DEBUG']

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

lg.getLogger('discord').setLevel(lg.WARNING)
lg.getLogger('websockets').setLevel(lg.WARNING)
lg.getLogger('asyncio').setLevel(lg.WARNING)
log.info('Logger is setup.')

wh = Wiihacky()

wh.load_extension('cogs.config')
wh.load_extension('cogs.discord')
wh.load_extension('cogs.memory')
wh.load_extension('cogs.menusys')
wh.load_extension('cogs.persona')
wh.load_extension('cogs.reddit')
wh.load_extension('cogs.security')
wh.load_extension('cogs.system')
# TODO: Discogs?!?

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
    log.error(
        'Failed to login with given token: {}'.format(e.args))
    exit(-1)
except RuntimeError as e:
    log.info('Looop experienced a runtime error: {}'.format(e.args))
    exit(0)
