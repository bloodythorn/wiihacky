import logging as lg

from praw.models import Message
from praw import Reddit

import wiihacky.actions.scrape.constants as const
import actions


class ScrapeMessage(actions.Action):
    """This action when given a comment will scrape and save the data."""

    TXT_AC = const.TXT_START + ' ' + const.TXT_MESSAGE

    def __init__(self, log: lg.Logger, msg_id: str):
        """Initialize the action."""
        actions.Action.__init__(self, log)
        self.msg_id = msg_id
        self.data = {}

    def execute(self, reddit: Reddit):
        """Execute action."""
        try:
            message = reddit.inbox.message(self.msg_id)

            # Scrape
            try:
                self.log.info(self.TXT_AC + '.')
                self.data = self.scrape(message)
            except Exception as e:
                self.log.error(const.TXT_ERR_EXCEPT.format(self.TXT_AC + ':', e))
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
        actions.action_concluded(self.log, self.TXT_AC, self.executed)

    @staticmethod
    def scrape(msg: Message):
        """Scrape a message.

        This function will scrape a message and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.
        """
        actions.scrape.fetch(msg)
        output = dict(vars(msg))
        actions.scrape.prep_dict(output, const.TXT_MESSAGE)
        output[const.TXT_REPLIES] = [a.id for a in output[const.TXT_REPLIES]]
        output[const.TXT_AUTHOR] = output[const.TXT_AUTHOR].name
        output[const.TXT_DEST] = output[const.TXT_DEST].name
        if msg.subreddit:
            output[const.TXT_SUBREDDIT] = \
                output[const.TXT_SUBREDDIT].display_name
        return actions.scrape.strip_all(output)
