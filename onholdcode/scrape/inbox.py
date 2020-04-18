import logging as lg

from praw.models import Inbox

import wiihacky.actions.scrape.constants as const
import wiihacky


class ScrapeInbox(wiihacky.actions.Action):
    """
    This action when given the inbox will scrape and save the data.
    """

    def __init__(self, log: lg.Logger):
        """Initialize the action."""
        super().__init__(log)
        self.action_text = const.TXT_START + ' ' + const.TXT_INBOX
        self.data = {}
        self.complete = False

    def execute(self, wh: wiihacky.WiiHacky):
        # Scrape
        reddit = wh.reddit
        try:
            self.log.info(self.action_text + '.')
            self.data = self.scrape(reddit.inbox)
        except Exception as e:
            self.log.error(
                const.TXT_ERR_EXCEPT.format(self.action_text + ':', e))
            raise e

        # Save
        try:
            self.log.info(
                const.TXT_SAVING.format(const.TXT_INBOX.capitalize()))
            wiihacky.actions.scrape.save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                const.TXT_ERR_EXCEPT.format(
                    const.TXT_SAVING.format(const.TXT_INBOX), e))
            raise e

        # End of Action
        self.action_concluded()

    @staticmethod
    def scrape(inbox: Inbox):
        """
        Scrape inbox.

        This function will scrape the inbox return a data structure reflecting
        its state.

        :param inbox: Inbox class from PRAW
        :return: dict with scraped data.
        """
        output = dict()
        wiihacky.actions.scrape.prep_dict(output, const.TXT_INBOX)
        output.update([
            (inbox.all.__name__, [a.id for a in inbox.all()]),
            (inbox.mentions.__name__,
             [a.id for a in inbox.mentions()]),
            (inbox.sent.__name__, [a.id for a in inbox.sent()]),
            (inbox.unread.__name__, [a.id for a in inbox.unread()])])
        return wiihacky.actions.scrape.strip_all(output)
