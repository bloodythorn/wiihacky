import logging as lg

from praw.models import Multireddit
from praw import Reddit

import wiihacky.actions.scrape.constants as const
import actions


class ScrapeMultireddit(actions.Action):
    """This action when given a subreddit will scrape and save the data."""

    TXT_AC = const.TXT_START + ' ' + const.TXT_MULTIREDDIT

    def __init__(self, log: lg.Logger, user: str, multi: str):
        """Initialize the action."""
        actions.Action.__init__(self, log)
        self.multi = (user, multi)
        self.data = {}

    def execute(self, reddit: Reddit):
        """Execute Action."""
        try:
            multi = reddit.multireddit(*self.multi)

            # Scrape
            try:
                self.log.info(self.TXT_AC + '.')
                self.data = self.scrape(multi)
            except Exception as e:
                self.log.error(const.TXT_ERR_EXCEPT.format(self.TXT_AC + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_MULTIREDDIT.capitalize()))
                actions.scrape.save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_MULTIREDDIT), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.multi))
            raise e

        # End of Action
        actions.action_concluded(self.log, self.TXT_AC, self.executed)

    @staticmethod
    def scrape(multi: Multireddit):
        """Scrape a multi reddit.

        This function will scrape the multiredit return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        actions.scrape.fetch(multi)
        output = dict(vars(multi))
        actions.scrape.prep_dict(output, const.TXT_MULTIREDDIT)
        output[const.TXT_SUBREDDIT + 's'] = \
            [a.display_name for a in output[const.TXT_SUBREDDIT + 's']]
        output[const.TXT_PATH] = output[const.TXT_PATH]
        output[const.TXT_AUTHOR] = output['_' + const.TXT_AUTHOR].name
        output.update([
            (const.TXT_COMMENTS, [a.id for a in multi.comments()]),
            (multi.controversial.__name__,
             [a.id for a in multi.controversial()]),
            (multi.hot.__name__, [a.id for a in multi.hot()]),
            (multi.new.__name__, [a.id for a in multi.new()]),
            (multi.rising.__name__, [a.id for a in multi.rising()]),
            (multi.top.__name__, [a.id for a in multi.top()]),
        ])
        return actions.scrape.strip_all(output)
