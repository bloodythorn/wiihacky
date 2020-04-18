import logging as lg

from praw.models import Submission

import wiihacky.actions.scrape.constants as const
import wiihacky


class ScrapeSubmission(wiihacky.actions.Action):
    """This action when given a submission will scrape and save the data."""

    def __init__(self, log: lg.Logger, subm_id: str):
        """Initialize the action."""
        super().__init__(log)
        self.action_text = const.TXT_START + ' ' + const.TXT_SUBMISSION
        self.subm_id = subm_id
        self.data = {}

    def execute(self, wh: wiihacky.WiiHacky):
        """Execute Action."""
        reddit = wh.reddit
        try:
            submission = reddit.submission(self.subm_id)

            # Scrape
            try:
                self.log.info(self.action_text + '.')
                self.data = self.scrape(submission)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.action_text + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_SUBMISSION.capitalize()))
                wiihacky.actions.scrape.save_data(self.data)
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
        self.action_concluded()

    @staticmethod
    def scrape(subm: Submission):
        """Scrape a submission.

        This function will scrape a submission and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        wiihacky.actions.scrape.fetch(subm)
        output = dict(vars(subm))
        wiihacky.actions.scrape.prep_dict(output, const.TXT_SUBMISSION)
        display_name = output[const.TXT_SUBREDDIT].display_name
        output[const.TXT_SUBREDDIT] = display_name
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        subm.comments.replace_more(limit=0)
        output[const.TXT_COMMENTS] = \
            [a.id for a in subm.comments.list()]
        return wiihacky.actions.scrape.strip_all(output)
