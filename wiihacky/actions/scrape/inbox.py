import logging as lg

from praw.models import Inbox

from wiihacky.actions import Action


class ScrapeInbox(Action):
    """This action when given the inbox will scrape and save the data."""

    def __init__(self, log: lg.Logger, inbx: Inbox):
        """Initialize the action."""
        Action.__init__(self, log)
        self.inbox = inbx
        self.TXT_INBOX = self.inbox.__class__.__name__
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_INBOX
        self.data = {}
        self.complete = False

    def execute(self):
        """Execute Action."""
        from wiihacky.actions.scrape.constants import (
            TXT_ERR_EXCEPT, TXT_SAVING)

        # Scrape
        try:
            self.log.info(self.ac + '.')
            self.data = self.scrape()
        except Exception as e:
            self.log.error(TXT_ERR_EXCEPT.format(self.ac + ':', e))

        # Save
        try:
            self.log.info(
                TXT_SAVING.format(self.TXT_INBOX.capitalize()))
            from wiihacky.actions.scrape import save_data
            save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                TXT_ERR_EXCEPT.format(TXT_SAVING.format(self.TXT_INBOX), e))

        # End of Action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.ac, self.complete)

    def scrape(self):
        """Scrape inbox.

        This function will scrape the inbox return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        from wiihacky.actions.scrape import prep_dict, strip_all

        output = dict()
        prep_dict(output, self.inbox.__class__.__name__)
        output.update([
            (self.inbox.all.__name__, [a.id for a in self.inbox.all()]),
            (self.inbox.mentions.__name__,
             [a.id for a in self.inbox.mentions()]),
            (self.inbox.sent.__name__, [a.id for a in self.inbox.sent()]),
            (self.inbox.unread.__name__, [a.id for a in self.inbox.unread()])])
        return strip_all(output)
