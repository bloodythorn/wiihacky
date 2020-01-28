import logging as lg

from praw.models import Message

from wiihacky.actions import Action


class ScrapeMessage(Action):
    """This action when given a comment will scrape and save the data."""

    def __init__(self, log: lg.Logger, msg: Message):
        """Initialize the action."""
        Action.__init__(self, log)
        self.msg = msg
        self.TXT_MESSAGE = self.msg.__class__.__name__
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_MESSAGE
        self.complete = False
        self.data = {}

    def execute(self):
        """Execute action."""
        from wiihacky.actions.scrape.constants import (
            TXT_ERR_EXCEPT, TXT_SAVING)

        # Scrape
        try:
            self.log.info(self.ac + '.')
            self.data = self.scrape()
        except Exception as e:
            self.log.error(TXT_ERR_EXCEPT.format(self.ac + ':', e))
            raise e

        # Save
        try:
            self.log.info(
                TXT_SAVING.format(self.TXT_MESSAGE.capitalize()))
            from wiihacky.actions.scrape import save_data
            save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                TXT_ERR_EXCEPT.format(TXT_SAVING.format(self.TXT_MESSAGE), e))
            raise e

        # End of Action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.ac, self.complete)

    def scrape(self):
        """Scrape a message.

        This function will scrape a message and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.
        """
        from wiihacky.actions.scrape.constants import (
            TXT_AUTHOR, TXT_DEST, TXT_REPLIES, TXT_SUBREDDIT)
        from wiihacky.actions.scrape import fetch, prep_dict, strip_all

        fetch(self.msg)
        output = dict(vars(self.msg))
        prep_dict(output, self.msg.__class__.__name__)
        output[TXT_REPLIES] = [a.id for a in output[TXT_REPLIES]]
        output[TXT_AUTHOR] = output[TXT_AUTHOR].name
        output[TXT_DEST] = output[TXT_DEST].name
        if self.msg.subreddit:
            output[TXT_SUBREDDIT] = \
                output[TXT_SUBREDDIT].display_name
        return strip_all(output)
