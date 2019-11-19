"""Base class for all actions."""
import logging as lg

import actions.constants as const


def action_concluded(log: lg.Logger, ac: str, complete: bool):
    """This will log the conclusion of the action."""
    log.info(const.ACTION_DONE.format(ac, const.ACTION_OK if complete else ""))


class Action:
    """Base action class."""
    ACTION_NAME = 'EmptyAction'

    def __init__(self, log: lg.Logger, msg="", priority=10):
        """Initialization takes a logger, and optional message and
            priority.
        """
        self.executed = False
        self.log = log
        self.msg = msg
        self.priority = priority

    def execute(self):
        """This function should be overwritten by the inherited class's
            own action routine.

            If the function is not, or if the base class is executed, it will
            print the log message.
        """
        self.log.info(self.msg)
        action_concluded(self.log, self.ACTION_NAME, const.ACTION_OK)
        self.executed = True
