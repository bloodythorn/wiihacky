import logging as lg

from praw.models import Submission

from actions import (Action, action_concluded)
import actions.scrape.constants as const
import actions.scrape as scrape


class ScrapeSubmission(Action):
    """This action when given a submission will scrape and save the data."""

    def __init__(self, log: lg.Logger, subm: Submission):
        """Initialize the action."""
        Action.__init__(self, log)
        self.subm = subm
        self.TXT_SUBMISSION = self.subm.__class__.__name__

    def execute(self):
        """Execute Action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_SUBMISSION
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
                const.TXT_SAVING.format(self.TXT_SUBMISSION.capitalize()))
            # Assemble filename and path
            fn = data[const.TXT_TYPE].lower() + '-' + \
                data[const.TXT_ID] + '-' + \
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
                self.log, const.TXT_SAVING.format(self.TXT_SUBMISSION), e)
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
        scrape.fetch(self.subm)
        output = dict(vars(self.subm))
        scrape.prep_dict(output, self.subm.__class__.__name__)
        output[const.TXT_SUBREDDIT] = \
            output[const.TXT_SUBREDDIT].display_name
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        self.subm.comments.replace_more(limit=0)
        output[const.TXT_COMMENTS] = \
            [a.id for a in self.subm.comments.list()]
        return scrape.strip_all(output)
