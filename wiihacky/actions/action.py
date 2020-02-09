"""Base class for all actions."""
import logging as lg
from abc import ABC, abstractmethod

import actions.constants as const
import wiihacky


def action_concluded(log: lg.Logger, ac: str, complete: bool):
    """This will log the conclusion of the action."""
    log.info(const.ACTION_DONE.format(ac, const.ACTION_OK if complete else ""))


class Action(ABC):
    """Base action class."""

    def __init__(self, log: lg.Logger):
        """Initialization takes a logger, and optional message and
            priority.
        """
        super().__init__()
        self.executed = False
        self.log = log

    @abstractmethod
    def execute(self, wh: wiihacky.WiiHacky):
        """Defines execution of Action."""
        pass
