import logging as lg

from praw.models import Submission
from praw import Reddit

import wiihacky.actions.scrape.constants as const
import actions


class ScrapeSubmission(actions.Action):
    """This action when given a submission will scrape and save the data."""

    TXT_AC = const.TXT_START + ' ' + const.TXT_SUBMISSION

    def __init__(self, log: lg.Logger, subm_id: str):
        """Initialize the action."""
        actions.Action.__init__(self, log)
        self.subm_id = subm_id
        self.data = {}

    def execute(self, reddit: Reddit):
        """Execute Action."""
        try:
            submission = reddit.submission(self.subm_id)

            # Scrape
            try:
                self.log.info(self.TXT_AC + '.')
                self.data = self.scrape(submission)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.TXT_AC + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_SUBMISSION.capitalize()))
                actions.scrape.save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_SUBMISSION), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.subm_id))
            raise e

        # End of action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.TXT_AC, self.executed)

    @staticmethod
    def scrape(subm: Submission):
        """Scrape a submission.

        This function will scrape a submission and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        actions.scrape.fetch(subm)
        output = dict(vars(subm))
        actions.scrape.prep_dict(output, const.TXT_SUBMISSION)
        display_name = output[const.TXT_SUBREDDIT].display_name
        output[const.TXT_SUBREDDIT] = display_name
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        subm.comments.replace_more(limit=0)
        output[const.TXT_COMMENTS] = \
            [a.id for a in subm.comments.list()]
        return actions.scrape.strip_all(output)
