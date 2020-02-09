import logging as lg

from praw.models import Inbox
from praw import Reddit

import wiihacky.actions.scrape.constants as const
import actions


class ScrapeInbox(actions.Action):
    """This action when given the inbox will scrape and save the data."""

    TXT_AC = const.TXT_START + ' ' + const.TXT_INBOX

    def __init__(self, log: lg.Logger):
        """Initialize the action."""
        actions.Action.__init__(self, log)
        self.data = {}
        self.complete = False

    def execute(self, reddit: Reddit):
        """Execute Action."""
        # Scrape
        try:
            self.log.info(self.TXT_AC + '.')
            self.data = self.scrape(reddit.inbox)
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(self.TXT_AC + ':', e))
            raise e

        # Save
        try:
            self.log.info(
                const.TXT_SAVING.format(const.TXT_INBOX.capitalize()))
            actions.scrape.save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                const.TXT_ERR_EXCEPT.format(
                    const.TXT_SAVING.format(const.TXT_INBOX), e))
            raise e

        # End of Action
        actions.action_concluded(self.log, self.TXT_AC, self.complete)

    @staticmethod
    def scrape(inbox: Inbox):
        """Scrape inbox.

        This function will scrape the inbox return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        output = dict()
        actions.scrape.prep_dict(output, const.TXT_INBOX)
        output.update([
            (inbox.all.__name__, [a.id for a in inbox.all()]),
            (inbox.mentions.__name__,
             [a.id for a in inbox.mentions()]),
            (inbox.sent.__name__, [a.id for a in inbox.sent()]),
            (inbox.unread.__name__, [a.id for a in inbox.unread()])])
        return actions.scrape.strip_all(output)
