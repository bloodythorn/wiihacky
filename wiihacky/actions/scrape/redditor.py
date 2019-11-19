import logging as lg

from praw.models import Redditor

from actions import (Action, action_concluded)
import actions.scrape.constants as const
import actions.scrape as scrape


class ScrapeRedditor(Action):
    """This action when given a redditor will scrape and save the data."""

    def __init__(self, log: lg.Logger, rdr: Redditor):
        """Initialize the action."""
        Action.__init__(self, log)
        self.rdr = rdr
        self.TXT_REDDITOR = self.rdr.__class__.__name__

    def execute(self):
        """Execute Action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_REDDITOR
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
                const.TXT_SAVING.format(self.TXT_REDDITOR.capitalize()))
            # Assemble filename and path
            fn = data[const.TXT_TYPE].lower() + '-' + \
                data[const.TXT_NAME].lower() + '-' + \
                str(data[const.TXT_UTC_STAMP])
            from pathlib import Path
            pth = Path(const.DATA_DIR) / data[const.TXT_TYPE].lower() / fn
            # Confirm directories
            from os import makedirs
            makedirs(pth.parent, exist_ok=True)
            # Save File
            with open(pth.with_suffix(const.FILE_SUFFIX), 'w') as f:
                from yaml import safe_dump
                f.write(safe_dump(data))
            complete = True
        except Exception as e:
            scrape.ex_occurred(
                self.log, const.TXT_SAVING.format(self.TXT_REDDITOR), e)
        # End of Action
        action_concluded(self.log, ac, complete)

    def scrape(self):
        """Scrape a redditor.

        This function will scrape a redditor and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        scrape.fetch(self.rdr)
        output = dict(vars(self.rdr))
        scrape.prep_dict(output, self.rdr.__class__.__name__)
        output[const.TXT_PATH] = output['_' + const.TXT_PATH]
        output.update([
            (self.rdr.trophies.__name__,
             [a.name for a in self.rdr.trophies()]),
            (self.rdr.multireddits.__name__,
             [a.name for a in self.rdr.multireddits()]),
        ])
        output[const.TXT_COMMENTS] = {}
        output[const.TXT_COMMENTS].update([
            (self.rdr.comments.controversial.__name__,
             [a.id for a in self.rdr.comments.controversial()]),
            (self.rdr.comments.hot.__name__,
             [a.id for a in self.rdr.comments.hot()]),
            (self.rdr.comments.new.__name__,
             [a.id for a in self.rdr.comments.new()]),
            (self.rdr.comments.top.__name__,
             [a.id for a in self.rdr.comments.top()]),
        ])
        output[const.TXT_SUBMISSION + 's'] = {}
        output[const.TXT_SUBMISSION + 's'].update([
            (self.rdr.submissions.controversial.__name__,
             [a.id for a in self.rdr.submissions.controversial()]),
            (self.rdr.submissions.hot.__name__,
             [a.id for a in self.rdr.submissions.hot()]),
            (self.rdr.submissions.new.__name__,
             [a.id for a in self.rdr.submissions.new()]),
            (self.rdr.submissions.top.__name__,
             [a.id for a in self.rdr.submissions.top()]),
        ])
        return scrape.strip_all(output)
