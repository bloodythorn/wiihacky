import logging as lg

from praw.models import Inbox

from actions import (Action, action_concluded)
import actions.scrape.constants as const
import actions.scrape as scrape


class ScrapeInbox(Action):
    """This action when given the inbox will scrape and save the data."""

    def __init__(self, log: lg.Logger, inbx: Inbox):
        """Only the inbox is needed."""
        Action.__init__(self, log)
        self.inbox = inbx
        self.TXT_INBOX = self.inbox.__class__.__name__

    def execute(self):
        """Execute Action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_INBOX
        complete = False
        data = {}
        # Scrape
        try:
            self.log.info(ac + '.')
            data = self.scrape()
        except Exception as e:
            scrape.ex_occurred(self.log, ac + ':', e)
        # Save
        try:
            self.log.info(
                const.TXT_SAVING.format(self.TXT_INBOX.capitalize()))
            # Assemble filename and path
            fn = data[const.TXT_TYPE].lower() + '-' + \
                str(data[const.TXT_UTC_STAMP]) + '.' + \
                const.FILE_SUFFIX
            from pathlib import Path, Path
            pth = Path(const.DATA_DIR) / data[const.TXT_TYPE].lower() / fn
            # Confirm directories
            from os import makedirs
            makedirs(pth.parent, exist_ok=True)
            # Save File
            with open(pth, 'w') as f:
                from yaml import safe_dump
                f.write(safe_dump(data))
        except Exception as e:
            scrape.ex_occurred(
                self.log, const.TXT_SAVING.format(self.TXT_INBOX), e)
        # End of Action
        action_concluded(self.log, ac, complete)

    def scrape(self):
        """Scrape inbox.

        This function will scrape the inbox return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        output = dict()
        scrape.prep_dict(output, self.inbox.__class__.__name__)
        output.update([
            (self.inbox.all.__name__, [a.id for a in self.inbox.all()]),
            (self.inbox.mentions.__name__,
             [a.id for a in self.inbox.mentions()]),
            (self.inbox.sent.__name__, [a.id for a in self.inbox.sent()]),
            (self.inbox.unread.__name__, [a.id for a in self.inbox.unread()])])
        return scrape.strip_all(output)
