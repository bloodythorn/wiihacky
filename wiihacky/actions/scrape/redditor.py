import logging as lg

from praw.models import Redditor

from wiihacky.actions import Action


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
        from wiihacky.actions.scrape.constants import (
            DATA_DIR, FILE_SUFFIX, TXT_NAME, TXT_SAVING,
            TXT_START, TXT_TYPE, TXT_UTC_STAMP)
        from wiihacky.actions.scrape import (ex_occurred)
        from wiihacky.actions import (action_concluded)

        ac = TXT_START + ' ' + self.TXT_REDDITOR
        complete = False
        data = {}
        # Scrape
        try:
            self.log.info(ac + '.')
            data = self.scrape()
        except Exception as e:
            ex_occurred(self.log, ac + ':', e)
        # Save
        try:
            self.log.info(
                TXT_SAVING.format(self.TXT_REDDITOR.capitalize()))
            # Assemble filename and path
            fn = data[TXT_TYPE].lower() + '-' + \
                data[TXT_NAME].lower() + '-' + \
                str(data[TXT_UTC_STAMP])
            from pathlib import Path
            pth = Path(DATA_DIR) / data[TXT_TYPE].lower() / fn
            # Confirm directories
            from os import makedirs
            makedirs(pth.parent, exist_ok=True)
            # Save File
            with open(pth.with_suffix(FILE_SUFFIX), 'w') as f:
                from yaml import safe_dump
                f.write(safe_dump(data))
            complete = True
        except Exception as e:
            ex_occurred(
                self.log, TXT_SAVING.format(self.TXT_REDDITOR), e)
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
        from wiihacky.actions.scrape.constants import (
            TXT_COMMENTS, TXT_PATH, TXT_SUBMISSION)
        from wiihacky.actions.scrape import (fetch, prep_dict, strip_all)

        fetch(self.rdr)
        output = dict(vars(self.rdr))
        prep_dict(output, self.rdr.__class__.__name__)
        output[TXT_PATH] = output['_' + TXT_PATH]
        output.update([
            (self.rdr.trophies.__name__,
             [a.name for a in self.rdr.trophies()]),
            (self.rdr.multireddits.__name__,
             [a.name for a in self.rdr.multireddits()]),
        ])
        output[TXT_COMMENTS] = {}
        output[TXT_COMMENTS].update([
            (self.rdr.comments.controversial.__name__,
             [a.id for a in self.rdr.comments.controversial()]),
            (self.rdr.comments.hot.__name__,
             [a.id for a in self.rdr.comments.hot()]),
            (self.rdr.comments.new.__name__,
             [a.id for a in self.rdr.comments.new()]),
            (self.rdr.comments.top.__name__,
             [a.id for a in self.rdr.comments.top()]),
        ])
        output[TXT_SUBMISSION + 's'] = {}
        output[TXT_SUBMISSION + 's'].update([
            (self.rdr.submissions.controversial.__name__,
             [a.id for a in self.rdr.submissions.controversial()]),
            (self.rdr.submissions.hot.__name__,
             [a.id for a in self.rdr.submissions.hot()]),
            (self.rdr.submissions.new.__name__,
             [a.id for a in self.rdr.submissions.new()]),
            (self.rdr.submissions.top.__name__,
             [a.id for a in self.rdr.submissions.top()]),
        ])
        return strip_all(output)
