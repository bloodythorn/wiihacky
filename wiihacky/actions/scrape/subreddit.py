import logging as lg

from praw.models import Subreddit
from praw import Reddit

import wiihacky.actions.scrape.constants as const
import actions


class ScrapeSubreddit(actions.Action):
    """This action when given a subreddit will scrape and save the data."""

    TXT_AC = const.TXT_START + ' ' + const.TXT_SUBREDDIT

    def __init__(self, log: lg.Logger, subreddit_name: str):
        """Initialize the action."""
        actions.Action.__init__(self, log)
        self.subreddit_name = subreddit_name
        self.data = {}

    def execute(self, reddit: Reddit):
        """Execute Action."""
        try:
            subreddit = reddit.subreddit(self.subreddit_name)

            # Scrape
            try:
                self.log.info(self.TXT_AC + '.')
                self.data = self.scrape(subreddit)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.TXT_AC + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_SUBREDDIT.capitalize()))
                actions.scrape.save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_SUBREDDIT), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.subreddit_name))
            raise e

        # End of Action
        actions.action_concluded(self.log, self.TXT_AC, self.executed)

    @staticmethod
    def scrape(subr: Subreddit):
        """Scrape a subreddit.

        This function will scrape a subreddit and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """

        actions.scrape.fetch(subr)
        output = dict(vars(subr))
        actions.scrape.prep_dict(output, const.TXT_SUBREDDIT)
        output[const.TXT_PATH] = output['_' + const.TXT_PATH]
        output.update([
            (const.TXT_COMMENTS, [a.id for a in subr.comments()]),
            (subr.controversial.__name__,
             [a.id for a in subr.controversial()]),
            (subr.hot.__name__, [a.id for a in subr.hot()]),
            (subr.new.__name__, [a.id for a in subr.new()]),
            (subr.rising.__name__, [a.id for a in subr.rising()]),
            (subr.top.__name__, [a.id for a in subr.top()]),
        ])
        return actions.scrape.strip_all(output)
