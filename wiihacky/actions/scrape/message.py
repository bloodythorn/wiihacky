import logging as lg

from praw.models import Message

import wiihacky.actions.scrape.constants as const
import wiihacky


class ScrapeMessage(wiihacky.actions.Action):
    """This action when given a comment will scrape and save the data."""

    def __init__(self, log: lg.Logger, msg_id: str):
        """Initialize the action."""
        super().__init__(log)
        self.action_text = const.TXT_START + ' ' + const.TXT_MESSAGE
        self.msg_id = msg_id
        self.data = {}

    def execute(self, wh: wiihacky.WiiHacky):
        """Execute action."""
        reddit = wh.reddit
        try:
            message = reddit.inbox.message(self.msg_id)

            # Scrape
            try:
                self.log.info(self.action_text + '.')
                self.data = self.scrape(message)
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(self.action_text + ':', e))
                raise e

            # Save
            try:
                self.log.info(
                    const.TXT_SAVING.format(const.TXT_MESSAGE.capitalize()))
                from wiihacky.actions.scrape import save_data
                save_data(self.data)
                self.executed = True
            except Exception as e:
                self.log.error(
                    const.TXT_ERR_EXCEPT.format(
                        const.TXT_SAVING.format(const.TXT_MESSAGE), e))
                raise e
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(
                const.TXT_FETCHING, self.msg_id))
            raise e

        # End of Action
        self.action_concluded()

    @staticmethod
    def scrape(msg: Message):
        """
        Scrape a message.

        This function will scrape a message and return a data structure
        reflecting its state.

        :param msg: Message class from PRAW
        :return: a dict with scraped data.
        """
        wiihacky.actions.scrape.fetch(msg)
        output = dict(vars(msg))
        wiihacky.actions.scrape.prep_dict(output, const.TXT_MESSAGE)
        output[const.TXT_REPLIES] = [a.id for a in output[const.TXT_REPLIES]]
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        output[const.TXT_DEST] = output[const.TXT_DEST].name
        if msg.subreddit:
            output[const.TXT_SUBREDDIT] = \
                output[const.TXT_SUBREDDIT].display_name
        return wiihacky.actions.scrape.strip_all(output)
