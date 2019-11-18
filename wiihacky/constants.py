# File Names
FILE_DEFAULT_CONFIG = 'config.yml'
LOAD_CONFIG = '{}/{}'

# Logger Related
LOG_FORMAT_STRING = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'

WH_INIT_LOGGED_IN = 'logged in as %s.'
WH_INIT_LOGGER_SUCC = 'successfully initialized logger.'
WH_INIT_REDDIT_SUCC = 'successfully initialized reddit instance.'
WH_RUN_INTERRUPT = 'ctrl-c interrupt detected.'
WH_RUN_START_BOT = 'starting bot. press ctrl-c to interrupt.'

# Version
__version__ = 'v0.0.2'
VERSION_TEXT = 'wiihacky_version'

DEFAULT_CONFIG = {
    'auth': {
        'user_agent': 'PutAgentNameHere',
        'client_id': 'PutClientIDHere',
        'client_secret': 'PutClientSecretHere',
        'username': 'PutUserNameHere',
        'password': 'PutPasswordHere',
        'admins': ["ListAdmins", "ByUserName", "Here"]}}
