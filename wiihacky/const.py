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
WH_RUN_INTERRUPT = 'ctrl-c interrupt detected.'
WH_RUN_START_BOT = 'starting bot. press ctrl-c to interrupt.'

# Scraper module txt constants
SCRAPE_DEL_REDDIT = '_reddit'
SCRAPE_DEL_AUTHOR = '_author'
SCRAPE_AUTHOR = 'author'
SCRAPE_ID = 'id'
SCRAPE_COMMENTS = 'comments'
SCRAPE_KARMA = 'karma'
SCRAPE_SUBMISSIONS = 'submissions'
SCRAPE_SUBREDDIT = 'subreddit'
SCRAPE_SUBREDDITS = 'subreddits'
SCRAPE_TYPE = 'type'
