import logging as lg
from abc import ABC, abstractmethod

import actions.constants as const


class Action(ABC):
    """
    Base class for all actions.
    """

    def __init__(self, log: lg.Logger, *args, **kwargs):
        """Initialization takes a logger, and optional message and
            priority.
        """
        super().__init__()
        self._ACTION_TEXT = None
        self.executed = False
        self.log = log

    @property
    def action_text(self):
        """
        Text contains the action statement, a description of what is
        being performed.

        :return: action text in a string
        """
        return self._ACTION_TEXT

    @action_text.setter
    def action_text(self, value):
        """
        Setter for action_text.

        :param value: New value
        :return: None
        """
        self._ACTION_TEXT = value

    @action_text.deleter
    def action_text(self):
        """
        Deleter for property action_text.

        :return: None
        """
        del self._ACTION_TEXT

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Abstract Method defining the execution method for the action. This
        will perform whatever action is intended, and leave the action in
        a 'finished' state, determined by the subclass.

        :param wh:
        :return:
        """
        pass

    def action_concluded(self):
        """
        This function sends out a log message to signify that the action has
        concluded, and in what state.

        :return: None
        """
        """This will log the conclusion of the action."""
        self.log.info(
            const.ACTION_DONE.format(
                self.action_text,
                const.ACTION_OK if self.executed else ""))
