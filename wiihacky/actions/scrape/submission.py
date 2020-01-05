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

    def execute(self):
        """Execute Action."""
        from wiihacky.actions.scrape.constants import (
            DATA_DIR, FILE_SUFFIX, TXT_ID, TXT_SAVING,
            TXT_START, TXT_TYPE, TXT_UTC_STAMP)
        from wiihacky.actions.scrape import ex_occurred
        from wiihacky.actions import action_concluded

        ac = TXT_START + ' ' + self.TXT_SUBMISSION
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
                TXT_SAVING.format(self.TXT_SUBMISSION.capitalize()))
            # Assemble filename and path
            fn = data[TXT_TYPE].lower() + '-' + \
                data[TXT_ID] + '-' + \
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
                self.log, TXT_SAVING.format(self.TXT_SUBMISSION), e)
        # End of action
        action_concluded(self.log, ac, complete)

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
