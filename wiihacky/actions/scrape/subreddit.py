import logging as lg

from praw.models import Subreddit

from wiihacky.actions import Action


class ScrapeSubreddit(Action):
    """This action when given a subreddit will scrape and save the data."""

    def __init__(self, log: lg.Logger, subr: Subreddit):
        """Initialize the action."""
        Action.__init__(self, log)
        self.subr = subr
        self.TXT_SUBREDDIT = self.subr.__class__.__name__

    def execute(self):
        """Execute Action."""
        from wiihacky.actions.scrape.constants import (
            DATA_DIR, FILE_SUFFIX, TXT_DISPLAY_NAME, TXT_SAVING,
            TXT_START, TXT_TYPE, TXT_UTC_STAMP)
        from wiihacky.actions.scrape import ex_occurred
        from wiihacky.actions import action_concluded

        ac = TXT_START + ' ' + self.TXT_SUBREDDIT
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
                TXT_SAVING.format(self.TXT_SUBREDDIT.capitalize()))
            # Assemble filename and path
            fn = data[TXT_TYPE].lower() + '-' + \
                data[TXT_DISPLAY_NAME].lower() + '-' + \
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
                self.log, TXT_SAVING.format(self.TXT_SUBREDDIT), e)
        # End of Action
        action_concluded(self.log, ac, complete)

    def scrape(self):
        """Scrape a subreddit.

        This function will scrape a subreddit and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        from wiihacky.actions.scrape.constants import (
            TXT_COMMENTS, TXT_PATH)
        from wiihacky.actions.scrape import (fetch, prep_dict, strip_all)

        fetch(self.subr)
        output = dict(vars(self.subr))
        prep_dict(output, self.subr.__class__.__name__)
        output[TXT_PATH] = output['_' + TXT_PATH]
        output.update([
            (TXT_COMMENTS, [a.id for a in self.subr.comments()]),
            (self.subr.controversial.__name__,
             [a.id for a in self.subr.controversial()]),
            (self.subr.hot.__name__, [a.id for a in self.subr.hot()]),
            (self.subr.new.__name__, [a.id for a in self.subr.new()]),
            (self.subr.rising.__name__, [a.id for a in self.subr.rising()]),
            (self.subr.top.__name__, [a.id for a in self.subr.top()]),
        ])
        return strip_all(output)
