import logging as lg

from praw.models import Comment

from wiihacky.actions import Action


class ScrapeComment(Action):
    """This action when given a comment will scrape and save the data."""

    def __init__(self, log: lg.Logger, comment: Comment):
        """Initialize the action."""
        Action.__init__(self, log)
        self.complete = False
        self.comment = comment
        self.data = {}
        self.TXT_COMMENT = self.comment.__class__.__name__
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_COMMENT

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

        # Save
        try:
            self.log.info(
                TXT_SAVING.format(self.TXT_COMMENT.capitalize()))
            from wiihacky.actions.scrape import save_data
            save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                TXT_ERR_EXCEPT.format(TXT_SAVING.format(self.TXT_COMMENT), e))

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

        fetch(self.comment)
        output = dict(vars(self.comment))
        prep_dict(output, self.TXT_COMMENT)
        output[TXT_AUTHOR] = output[TXT_AUTHOR].name
        output[TXT_SUBREDDIT] = output[TXT_SUBREDDIT].name
        output[TXT_SUBMISSION] = output['_' + TXT_SUBMISSION]
        output[TXT_REPLIES] = \
            [a.id for a in output['_' + TXT_REPLIES]]
        return strip_all(output)
