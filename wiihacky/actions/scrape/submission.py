import logging as lg

from praw.models import Submission

from wiihacky.actions import Action


class ScrapeSubmission(Action):
    """This action when given a submission will scrape and save the data."""

    def __init__(self, log: lg.Logger, subm: Submission):
        """Initialize the action."""
        Action.__init__(self, log)
        self.subm = subm
        self.TXT_SUBMISSION = self.subm.__class__.__name__
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_SUBMISSION
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
            raise e

        # Save
        try:
            self.log.info(
                TXT_SAVING.format(self.TXT_SUBMISSION.capitalize()))
            from wiihacky.actions.scrape import save_data
            save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                TXT_ERR_EXCEPT.format(
                    TXT_SAVING.format(self.TXT_SUBMISSION), e))
            raise e

        # End of action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.ac, self.complete)

    def scrape(self):
        """Scrape a submission.

        This function will scrape a submission and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        from wiihacky.actions.scrape.constants import (
            TXT_AUTHOR, TXT_COMMENTS, TXT_SUBREDDIT)
        from wiihacky.actions.scrape import (fetch, prep_dict, strip_all)

        fetch(self.subm)
        output = dict(vars(self.subm))
        prep_dict(output, self.subm.__class__.__name__)
        display_name = output[TXT_SUBREDDIT].display_name
        output[TXT_SUBREDDIT] = display_name
        output[TXT_AUTHOR] = output[TXT_AUTHOR].name
        self.subm.comments.replace_more(limit=0)
        output[TXT_COMMENTS] = \
            [a.id for a in self.subm.comments.list()]
        return strip_all(output)
