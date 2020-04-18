import logging as lg

from praw.models import Subreddit

import wiihacky.actions.scrape.constants as const
import wiihacky


class ScrapeSubreddit(wiihacky.actions.Action):
    """This action when given a subreddit will scrape and save the data."""

    def __init__(self, log: lg.Logger, subreddit_name: str):
        """Initialize the action."""
        super().__init__(log)
        self.action_text = const.TXT_START + ' ' + const.TXT_SUBREDDIT
        self.subreddit_name = subreddit_name
        self.data = {}

    def execute(self, wh: wiihacky.WiiHacky):
        """Execute Action."""
        reddit = wh.reddit
        try:
            subreddit = reddit.subreddit(self.subreddit_name)

            # Scrape
            try:
                self.log.info(self.action_text + '.')
                self.data = self.scrape(subreddit)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.action_text + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_SUBREDDIT.capitalize()))
                wiihacky.actions.scrape.save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_SUBREDDIT), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.subreddit_name))
            raise e

        # End of Action
        self.action_concluded()

    @staticmethod
    def scrape(subr: Subreddit):
        """
        Scrape a subreddit.

        This function will scrape a subreddit and return a data structure
        reflecting its state.

        :param subr: Subreddit data type from praw
        :return: Dict with scraped data.
        """
        wiihacky.actions.scrape.fetch(subr)
        output = dict(vars(subr))
        wiihacky.actions.scrape.prep_dict(output, const.TXT_SUBREDDIT)
        output[const.TXT_PATH] = output['_' + const.TXT_PATH]
        output.update([
            (const.TXT_COMMENTS, [a.id for a in subr.comments()]),
            (subr.controversial.__name__,
             [a.id for a in subr.controversial()]),
            (subr.hot.__name__, [a.id for a in subr.hot()]),
            (subr.new.__name__, [a.id for a in subr.new()]),
            (subr.rising.__name__, [a.id for a in subr.rising()]),
            (subr.top.__name__, [a.id for a in subr.top()]),
        ])
        return wiihacky.actions.scrape.strip_all(output)
