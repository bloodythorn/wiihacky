import logging as lg

# TODO: Remove STRING const
# TODO: Docu

ACTION_TREE = {
    'action': {},
    'scrape': {
        'inbox': {},
        'user': {}
    }}


class Action:
    """Base action class."""

    def __init__(self, log: lg.Logger, priority=10, msg=""):
        self.executed = False
        self.log = log
        self.msg = msg
        self.priority = priority

    def execute(self):
        self.log.info(self.msg)
        self.log.info('Execute empty action concluded.')
        self.executed = True
