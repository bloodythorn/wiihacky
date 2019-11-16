"""Constants for WiiHacky."""

# TODO: This could really use some clean-up.

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
SCRAPE_DEL_AUTHOR = '_author'
SCRAPE_DEL_AWARDERS = 'awarders'
SCRAPE_DEL_COMMENTS = '_comments'
SCRAPE_DEL_COMMENTS_BY_ID = '_comments_by_id'
SCRAPE_DEL_FETCHED = '_fetched'
SCRAPE_DEL_PATH = '_path'
SCRAPE_DEL_REDDIT = '_reddit'
SCRAPE_DEL_REPLIES = '_replies'
SCRAPE_DEL_SUBMISSION = '_submission'
SCRAPE_AUTHOR = 'author'
SCRAPE_DEST = 'dest'
SCRAPE_NAME = 'name'
SCRAPE_COMMENTS = 'comments'
SCRAPE_KARMA = 'karma'
SCRAPE_PATH = 'path'
SCRAPE_REPLIES = 'replies'
SCRAPE_SUBMISSION = 'submission'
SCRAPE_SUBMISSIONS = 'submissions'
SCRAPE_SUBREDDIT = 'subreddit'
SCRAPE_SUBREDDITS = 'subreddits'
SCRAPE_TYPE = 'type'

LOAD_CONFIG = '{}/{}'

FILE_DELIM = '-'
FILE_SUFFIX = '.yml'
FILE_PATH = '/'
FILE_FORMAT_ONE = '{}'+FILE_DELIM+'{}.dat'
FILE_FORMAT_TWO = '{}'+FILE_DELIM+'{}'+FILE_DELIM+'{}.dat'
FILE_FORMAT_THREE = '{}'+FILE_DELIM+'{}'+FILE_DELIM+'{}'+FILE_DELIM+'{}.dat'

ENCODE = 'utf-8'

KEY_ID = 'id'
KEY_OWNER = 'owner'
KEY_NAME = 'name'

TYPE_COMMENT = 'Comment'
TYPE_INBOX = 'Inbox'
TYPE_MESSAGE = 'Message'
TYPE_MULTIREDDIT = 'Multireddit'
TYPE_REDDITOR = 'Redditor'
TYPE_SUBMISSION = 'Submission'
TYPE_SUBREDDIT = 'Subreddit'
TYPE_USER = 'User'

DEBUG_ERROR_TXT = 'TODO: CHECK ME!'

DEFAULT_CONFIG = {
    'auth': {
        'user_agent': 'PutAgentNameHere',
        'client_id': 'PutClientIDHere',
        'client_secret': 'PutClientSecretHere',
        'username': 'PutUserNameHere',
        'password': 'PutPasswordHere',
        'admins': ["ListAdmins", "ByUserName", "Here"]}}
