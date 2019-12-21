import logging as lg

from praw.models import Comment

from wiihacky.actions import (Action, action_concluded)
import wiihacky.actions.scrape.constants as const
import wiihacky.actions.scrape as scrape


class ScrapeComment(Action):
    """This action when given a comment will scrape and save the data."""

    def __init__(self, log: lg.Logger, cmnt: Comment):
        """Initialize the action."""
        Action.__init__(self, log)
        self.cmnt = cmnt
        self.TXT_COMMENT = self.cmnt.__class__.__name__

    def execute(self):
        """Execute Action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_COMMENT
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
                const.TXT_SAVING.format(self.TXT_COMMENT.capitalize()))
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
                self.log, const.TXT_SAVING.format(self.TXT_COMMENT), e)
        # End of action
        action_concluded(self.log, ac, complete)

    def scrape(self):
        """Scrape a comment.

        This function will scrape the comment return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        scrape.fetch(self.cmnt)
        output = dict(vars(self.cmnt))
        scrape.prep_dict(output, self.cmnt.__class__.__name__)
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        output[const.TXT_SUBREDDIT] = output[const.TXT_SUBREDDIT].name
        output[const.TXT_SUBMISSION] = output['_' + const.TXT_SUBMISSION]
        output[const.TXT_REPLIES] = \
            [a.id for a in output['_' + const.TXT_REPLIES]]
        return scrape.strip_all(output)
