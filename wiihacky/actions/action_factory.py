import logging as lg
from discord import Message


class ActionFactory:

    def __init__(self, log: lg.Logger):
        self.log = log

    def parse_message(self, message: Message):
        pass

    def parse_action(self, action_txt):
        # This should make sure any configuration is entered into the factory.
        # Then the factory can be given the text string.
        # It will return an action.
        # otherwise it will probably exception with a custom error.
        from actions.discord import SendMessage
        return SendMessage(self.log)
