import logging as lg

from praw.models import User

import wiihacky.actions.scrape.constants as const
import wiihacky


class ScrapeUser(wiihacky.actions.Action):
    """This action when given the user will scrape and save the data."""

    def __init__(self, log: lg.Logger):
        """Only the user is needed."""
        super().__init__(log)
        self.action_text = const.TXT_START + ' ' + const.TXT_USER
        self.data = {}

    def execute(self, wh: wiihacky.WiiHacky):
        """Execute Action."""
        # Scrape
        reddit = wh.reddit
        try:
            self.log.info(self.action_text + '.')
            self.data = self.scrape(reddit.user)
        except Exception as e:
            self.log.error(
                const.TXT_ERR_EXCEPT.format(self.action_text + ':', e))

        # Save
        try:
            self.log.info(
                const.TXT_SAVING.format(const.TXT_USER.capitalize()))
            wiihacky.actions.scrape.save_data(self.data)
            self.executed = True
        except Exception as e:
            self.log.error(
                const.TXT_ERR_EXCEPT.format(
                    const.TXT_SAVING.format(const.TXT_USER), e))

        # End of Action
        self.action_concluded()

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
        wiihacky.actions.scrape.prep_dict(output, const.TXT_USER)
        # noinspection PyProtectedMember,PyTypeChecker
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
        return wiihacky.actions.scrape.strip_all(output)
