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
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_SUBREDDIT
        self.complete = False
        self.data = {}

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
                TXT_SAVING.format(self.TXT_SUBREDDIT.capitalize()))
            from wiihacky.actions.scrape import save_data
            save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                TXT_ERR_EXCEPT.format(
                    TXT_SAVING.format(self.TXT_SUBREDDIT), e))

        # End of Action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.ac, self.complete)

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
