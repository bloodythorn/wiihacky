import praw as pr

DATA_DIR = 'data'

FILE_DELIM = '-'
FILE_SUFFIX = '.yml'

TXT_ERR_DIR = 'Could not verify directory: {}'
TXT_ERR_EXCEPT = 'An exception occurred while {}: {}'
TXT_ERR_SAVE = 'Could not save file: {}'

TXT_ID = 'id'
TXT_KARMA = 'karma'
TXT_NAME = 'name'
TXT_START = 'Scraping'
TXT_SAVING = 'Saving {} data'
TXT_TYPE = 'type'
TXT_UTC_STAMP = 'utc_timestamp'

TXT_FETCH_FUNC = pr.models.reddit.base.RedditBase._fetch.__name__


# TXT_AUTHOR = 'author'
# TXT_INBOX = 'Inbox'
# TXT_COMMENT = 'comment'
# TXT_MESSAGE = 'Message'
# TXT_REDDITOR = 'redditor'
# TXT_REPLIES = 'replies'
# TXT_SUBMISSION = 'submission'
# TXT_SUBREDDIT = 'subreddit'
# OB_USER = 'User'
# FILE_PATH = '/'
#KEY_OWNER = 'owner'
#TYPE_COMMENT = 'Comment'
#TYPE_MULTIREDDIT = 'Multireddit'
#TYPE_SUBREDDIT = 'Subreddit'
#TYPE_USER = 'User'
# Scraper module txt constants
#SCRAPE_DEL_AUTHOR = '_author'
#SCRAPE_DEL_AWARDERS = 'awarders'
#SCRAPE_DEL_COMMENTS = '_comments'
#SCRAPE_DEL_COMMENTS_BY_ID = '_comments_by_id'
#SCRAPE_DEL_PATH = '_path'
#SCRAPE_DEL_REDDIT = '_reddit'
#SCRAPE_DEST = 'dest'
#SCRAPE_NAME = 'name'
#SCRAPE_COMMENTS = 'comments'
#SCRAPE_KARMA = 'karma'
#SCRAPE_PATH = 'path'
#SCRAPE_SUBMISSIONS = 'submissions'
#SCRAPE_SUBREDDITS = 'subreddits'
