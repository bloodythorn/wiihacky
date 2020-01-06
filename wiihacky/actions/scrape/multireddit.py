import logging as lg

from praw.models import Multireddit

from wiihacky.actions import Action


class ScrapeMultireddit(Action):
    """This action when given a subreddit will scrape and save the data."""

    def __init__(self, log: lg.Logger, multi: Multireddit):
        """Initialize the action."""
        Action.__init__(self, log)
        self.multi = multi
        self.TXT_MULTIREDDIT = self.multi.__class__.__name__
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_MULTIREDDIT
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
                TXT_SAVING.format(self.TXT_MULTIREDDIT.capitalize()))
            from wiihacky.actions.scrape import save_data
            save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                TXT_ERR_EXCEPT.format(
                    TXT_SAVING.format(self.TXT_MULTIREDDIT), e))

        # End of Action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.ac, self.complete)

    def scrape(self):
        """Scrape a multi reddit.

        This function will scrape the multiredit return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        from wiihacky.actions.scrape import (fetch, prep_dict, strip_all)
        from wiihacky.actions.scrape.constants import (
            TXT_AUTHOR, TXT_COMMENTS, TXT_PATH, TXT_SUBREDDIT)

        fetch(self.multi)
        output = dict(vars(self.multi))
        prep_dict(output, self.multi.__class__.__name__)
        output[TXT_SUBREDDIT + 's'] = \
            [a.display_name for a in output[TXT_SUBREDDIT + 's']]
        output[TXT_PATH] = output[TXT_PATH]
        output[TXT_AUTHOR] = output['_' + TXT_AUTHOR].name
        output.update([
            (TXT_COMMENTS, [a.id for a in self.multi.comments()]),
            (self.multi.controversial.__name__,
             [a.id for a in self.multi.controversial()]),
            (self.multi.hot.__name__, [a.id for a in self.multi.hot()]),
            (self.multi.new.__name__, [a.id for a in self.multi.new()]),
            (self.multi.rising.__name__, [a.id for a in self.multi.rising()]),
            (self.multi.top.__name__, [a.id for a in self.multi.top()]),
        ])
        return strip_all(output)
