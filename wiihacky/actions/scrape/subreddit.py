import logging as lg

from praw.models import Subreddit

from actions import (Action, action_concluded)
import actions.scrape.constants as const
import actions.scrape as scrape


class ScrapeSubreddit(Action):

    def __init__(self, log: lg.Logger, subr: Subreddit):
        """Initialize the action."""
        Action.__init__(self, log)
        self.subr = subr
        self.TXT_SUBREDDIT = self.subr.__class__.__name__

    def execute(self):
        """Execute Action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_SUBREDDIT
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
                const.TXT_SAVING.format(self.TXT_SUBREDDIT.capitalize()))
            # Assemble filename and path
            fn = data[const.TXT_TYPE].lower() + '-' + \
                data[const.TXT_DISPLAY_NAME].lower() + '-' + \
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
                self.log, const.TXT_SAVING.format(self.TXT_SUBREDDIT), e)
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
        scrape.fetch(self.subr)
        output = dict(vars(self.subr))
        scrape.prep_dict(output, self.subr.__class__.__name__)
        output[const.TXT_PATH] = output['_' + const.TXT_PATH]
        output.update([
            (const.TXT_COMMENTS, [a.id for a in self.subr.comments()]),
            (self.subr.controversial.__name__,
             [a.id for a in self.subr.controversial()]),
            (self.subr.hot.__name__, [a.id for a in self.subr.hot()]),
            (self.subr.new.__name__, [a.id for a in self.subr.new()]),
            (self.subr.rising.__name__, [a.id for a in self.subr.rising()]),
            (self.subr.top.__name__, [a.id for a in self.subr.top()]),
        ])
        return scrape.strip_all(output)
