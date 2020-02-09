import logging as lg

from praw.models import Redditor
from praw import Reddit

import wiihacky.actions.scrape.constants as const
import actions


class ScrapeRedditor(actions.Action):
    """This action when given a redditor will scrape and save the data."""

    TXT_AC = const.TXT_START + ' ' + const.TXT_REDDITOR

    def __init__(self, log: lg.Logger, redditor_name: str):
        """Initialize the action."""
        actions.Action.__init__(self, log)
        self.redditor_name = redditor_name
        self.data = {}

    def execute(self, reddit: Reddit):
        """Execute Action."""
        try:
            redditor = reddit.redditor(self.redditor_name)

            # Scrape
            try:
                self.log.info(self.TXT_AC + '.')
                self.data = self.scrape(redditor)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.TXT_AC + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_REDDITOR.capitalize()))
                actions.scrape.save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_REDDITOR), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.redditor_name))
            raise e

        # End of Action
        actions.action_concluded(self.log, self.TXT_AC, self.executed)

    @staticmethod
    def scrape(redditor: Redditor):
        """Scrape a redditor.

        This function will scrape a redditor and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        actions.scrape.fetch(redditor)
        output = dict(vars(redditor))
        actions.scrape.prep_dict(output, const.TXT_REDDITOR)
        output.update([
            (redditor.trophies.__name__,
             [a.name for a in redditor.trophies()]),
            (redditor.multireddits.__name__,
             [a.name for a in redditor.multireddits()]),
        ])
        output[const.TXT_COMMENTS] = {}
        output[const.TXT_COMMENTS].update([
            (redditor.comments.controversial.__name__,
             [a.id for a in redditor.comments.controversial()]),
            (redditor.comments.hot.__name__,
             [a.id for a in redditor.comments.hot()]),
            (redditor.comments.new.__name__,
             [a.id for a in redditor.comments.new()]),
            (redditor.comments.top.__name__,
             [a.id for a in redditor.comments.top()]),
        ])
        output[const.TXT_SUBMISSION + 's'] = {}
        output[const.TXT_SUBMISSION + 's'].update([
            (redditor.submissions.controversial.__name__,
             [a.id for a in redditor.submissions.controversial()]),
            (redditor.submissions.hot.__name__,
             [a.id for a in redditor.submissions.hot()]),
            (redditor.submissions.new.__name__,
             [a.id for a in redditor.submissions.new()]),
            (redditor.submissions.top.__name__,
             [a.id for a in redditor.submissions.top()]),
        ])
        return actions.scrape.strip_all(output)
