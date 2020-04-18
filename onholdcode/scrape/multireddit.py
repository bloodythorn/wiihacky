import logging as lg

from praw.models import Multireddit

import wiihacky.actions.scrape.constants as const
import wiihacky


class ScrapeMultireddit(wiihacky.actions.Action):
    """This action when given a subreddit will scrape and save the data."""

    def __init__(self, log: lg.Logger, user: str, multi: str):
        """Initialize the action."""
        super().__init__(log)
        self.action_text = const.TXT_START + ' ' + const.TXT_MULTIREDDIT
        self.multi = (user, multi)
        self.data = {}

    def execute(self, wh: wiihacky.WiiHacky):
        """Execute Action."""
        reddit = wh.reddit
        try:
            multi = reddit.multireddit(*self.multi)

            # Scrape
            try:
                self.log.info(self.action_text + '.')
                self.data = self.scrape(multi)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.action_text + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_MULTIREDDIT.capitalize()))
                wiihacky.actions.scrape.save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_MULTIREDDIT), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.multi))
            raise e

        # End of Action
        self.action_concluded()

    @staticmethod
    def scrape(multi: Multireddit):
        """
        Scrape a multi reddit.

        This function will scrape the multireddit return a data structure
        reflecting its state.

        :param multi: Multireddit class from PRAW
        :return: a dict with scraped data.
        """
        wiihacky.actions.scrape.fetch(multi)
        output = dict(vars(multi))
        wiihacky.actions.scrape.prep_dict(output, const.TXT_MULTIREDDIT)
        output[const.TXT_SUBREDDIT + 's'] = \
            [a.display_name for a in output[const.TXT_SUBREDDIT + 's']]
        output[const.TXT_PATH] = output[const.TXT_PATH]
        output[const.TXT_AUTHOR] = output['_' + const.TXT_AUTHOR].name
        output.update([
            (const.TXT_COMMENTS, [a.id for a in multi.comments()]),
            (multi.controversial.__name__,
             [a.id for a in multi.controversial()]),
            (multi.hot.__name__, [a.id for a in multi.hot()]),
            (multi.new.__name__, [a.id for a in multi.new()]),
            (multi.rising.__name__, [a.id for a in multi.rising()]),
            (multi.top.__name__, [a.id for a in multi.top()]),
        ])
        return wiihacky.actions.scrape.strip_all(output)
