import logging as lg

from praw.models import Comment

from wiihacky.actions import Action


class ScrapeComment(Action):
    """This action when given a comment will scrape and save the data."""

    def __init__(self, log: lg.Logger, cmnt: Comment):
        """Initialize the action."""
        Action.__init__(self, log)
        self.complete = False
        self.cmnt = cmnt
        self.data = {}
        self.TXT_COMMENT = self.cmnt.__class__.__name__
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_COMMENT

    def execute(self):
        """Execute Action."""
        from wiihacky.actions.scrape import ex_occurred, gen_filename
        from wiihacky.actions.scrape.constants import (
            DATA_DIR, FILE_SUFFIX, TXT_SAVING, TXT_TYPE)

        # Scrape
        try:
            self.log.info(self.ac + '.')
            self.data = self.scrape()
        except Exception as e:
            ex_occurred(self.log, self.ac + ':', e)

        # Save
        try:
            self.log.info(
                TXT_SAVING.format(self.TXT_COMMENT.capitalize()))

            # Assemble filename and path
            fn = gen_filename(self.data)
            from pathlib import Path
            pth = Path(DATA_DIR) / self.data[TXT_TYPE].lower() / fn

            # Confirm directories
            from os import makedirs
            makedirs(pth.parent, exist_ok=True)

            # Save File
            with open(pth.with_suffix(FILE_SUFFIX), 'w') as f:
                from yaml import safe_dump
                f.write(safe_dump(self.data))
            self.complete = True
        except Exception as e:
            ex_occurred(
                self.log, TXT_SAVING.format(self.TXT_COMMENT), e)

        # End of action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.ac, self.complete)

    def scrape(self):
        """Scrape a comment.

        This function will scrape the comment return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        from wiihacky.actions.scrape.constants import (
            TXT_AUTHOR, TXT_REPLIES, TXT_SUBREDDIT, TXT_SUBMISSION)
        from wiihacky.actions.scrape import (fetch, prep_dict, strip_all)

        fetch(self.cmnt)
        output = dict(vars(self.cmnt))
        prep_dict(output, self.cmnt.__class__.__name__)
        output[TXT_AUTHOR] = output[TXT_AUTHOR].name
        output[TXT_SUBREDDIT] = output[TXT_SUBREDDIT].name
        output[TXT_SUBMISSION] = output['_' + TXT_SUBMISSION]
        output[TXT_REPLIES] = \
            [a.id for a in output['_' + TXT_REPLIES]]
        return strip_all(output)
