import logging as lg

from praw.models import User
from praw import Reddit

import wiihacky.actions.scrape.constants as const
import actions


class ScrapeUser(actions.Action):
    """This action when given the user will scrape and save the data."""

    TXT_AC = const.TXT_START + ' ' + const.TXT_USER

    def __init__(self, log: lg.Logger):
        """Only the user is needed."""
        actions.Action.__init__(self, log)
        self.data = {}

    def execute(self, reddit: Reddit):
        """Execute Action."""
        # Scrape
        try:
            self.log.info(self.TXT_AC + '.')
            self.data = self.scrape(reddit.user)
        except Exception as e:
            self.log.error(const.TXT_ERR_EXCEPT.format(self.TXT_AC + ':', e))

        # Save
        try:
            self.log.info(
                const.TXT_SAVING.format(const.TXT_USER.capitalize()))
            actions.scrape.save_data(self.data)
            self.executed = True
        except Exception as e:
            self.log.error(
                const.TXT_ERR_EXCEPT.format(
                    const.TXT_SAVING.format(const.TXT_USER), e))

        # End of Action
        actions.action_concluded(self.log, self.TXT_AC, self.executed)

    @staticmethod
    def scrape(user: User):
        """Scrape user.

        This function will scrape the user return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        output = dict()
        actions.scrape.prep_dict(output, const.TXT_USER)
        output.update([
            (const.TXT_NAME, user._me.name),
            (const.TXT_KARMA,
             dict([(a.display_name, b) for a, b in user.karma().items()])),
            (user.preferences.__class__.__name__,
             dict(user.preferences())),
            (user.moderator_subreddits.__name__,
             [a.display_name for a in user.moderator_subreddits()]),
            (user.subreddits.__name__,
             [a.display_name for a in user.subreddits()]),
            (user.blocked.__name__,
             [a.display_name for a in user.blocked()]),
            (user.friends.__name__,
             [a.display_name for a in user.friends()]),
            (user.multireddits.__name__,
             [a.display_name for a in user.multireddits()])])
        return actions.scrape.strip_all(output)
