"""Constants for WiiHacky."""

__version__ = 'v0.0.2'
VERSION_TEXT = 'wiihacky_version'
UTC_STAMP = 'utc_timestamp'

# Logger Related
LOG_FORMAT_STRING = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'

# File Names
FILE_DEFAULT_CONFIG = 'config.yml'

# WiiHacky module txt constants
WH_INIT_LOGGED_IN = 'logged in as %s.'
WH_INIT_LOGGER_SUCC = 'successfully initialized logger.'
WH_INIT_REDDIT_SUCC = 'successfully initialized reddit instance.'
WH_INIT_SCRAPER = 'successfully initialized scraper.'
WH_RUN_INTERRUPT = 'ctrl-c interrupt detected.'
WH_RUN_START_BOT = 'starting bot. press ctrl-c to interrupt.'

# Scraper module txt constants
SCRAPE_DEL_REDDIT = '_reddit'
SCRAPE_AUTHOR = 'author'
SCRAPE_SUBREDDIT = 'subreddit'
SCRAPE_USER = 'scraping user...'
SCRAPE_INBOX = 'scraping inbox...'
SCRAPE_COMPLETE = 'scraping complete.'
SCRAPE_TYPE_UNSUPPORTED = 'general scraping does not support type %s.'
SCRAPE_TYPE = 'type'
SCRAPE_ID = 'id'
