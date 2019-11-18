"""Base class for all actions."""
import logging as lg

import actions.constants as constants

class Action:
    """Base action class."""

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
        self.log.info(constants.ACTION_DONE.format(
            constants.ACTION_NAME, constants.ACTION_OK))
        self.executed = True
