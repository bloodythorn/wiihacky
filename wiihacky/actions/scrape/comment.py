import logging as lg

from praw.models import Comment

import wiihacky.actions.scrape.constants as const
import wiihacky


class ScrapeComment(wiihacky.actions.Action):
    """
    This action when given a comment id will scrape and save the data.
    """

    def __init__(self, log: lg.Logger, comment_id: str):
        """Initialize the action."""
        super().__init__(log)
        self.action_text = const.TXT_START + ' ' + const.TXT_COMMENTS[:-1]
        self.comment_id = comment_id
        self.data = {}

    def execute(self, wh: wiihacky.WiiHacky):
        # Fetch Comment
        reddit = wh.reddit
        try:
            comment = reddit.comment(self.comment_id)

            # Scrape
            try:
                self.log.info(self.action_text + '.')
                self.data = self.scrape(comment)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.action_text + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(
                        const.TXT_COMMENTS[:-1].capitalize()))
                wiihacky.actions.scrape.save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_COMMENTS[:-1]), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.comment_id))
            raise e

        # End of action
        self.action_concluded()

    @staticmethod
    def scrape(comment: Comment):
        """
        Scrape a comment.

        This function will scrape the comment return a data structure reflecting
        its state.

        :param comment: Comment class from PRAW
        :return: dict with scraped data.
        """
        wiihacky.actions.scrape.fetch(comment)
        output = dict(vars(comment))
        wiihacky.actions.scrape.prep_dict(output, const.TXT_COMMENTS[:-1])
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        output[const.TXT_SUBREDDIT] = output[const.TXT_SUBREDDIT].name
        output[const.TXT_SUBMISSION] = output['_' + const.TXT_SUBMISSION]
        output[const.TXT_REPLIES] = \
            [a.id for a in output['_' + const.TXT_REPLIES]]
        return wiihacky.actions.scrape.strip_all(output)
