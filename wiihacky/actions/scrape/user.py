import logging as lg

from praw.models import User

from wiihacky.actions import Action


class ScrapeUser(Action):
    """This action when given the user will scrape and save the data."""

    def __init__(self, log: lg.Logger, usr: User):
        """Only the user is needed."""
        Action.__init__(self, log)
        self.user = usr
        self.TXT_USER = self.user.__class__.__name__
        from wiihacky.actions.scrape.constants import TXT_START
        self.ac = TXT_START + ' ' + self.TXT_USER
        self.complete = False
        self.data = {}

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
                TXT_SAVING.format(self.TXT_USER.capitalize()))
            from wiihacky.actions.scrape import save_data
            save_data(self.data)
            self.complete = True
        except Exception as e:
            self.log.error(
                TXT_ERR_EXCEPT.format(TXT_SAVING.format(self.TXT_USER), e))

        # End of Action
        from wiihacky.actions import action_concluded
        action_concluded(self.log, self.ac, self.complete)

    def scrape(self):
        """Scrape user.

        This function will scrape the user return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        from wiihacky.actions.scrape.constants import (TXT_KARMA, TXT_NAME)
        from wiihacky.actions.scrape import (prep_dict, strip_all)

        output = dict()
        prep_dict(output, self.TXT_USER)
        # noinspection PyProtectedMember
        output.update([
            (TXT_NAME, self.user._me.name),
            (TXT_KARMA,
             dict([(a.display_name, b) for a, b in self.user.karma().items()])),
            (self.user.preferences.__class__.__name__,
             dict(self.user.preferences())),
            (self.user.moderator_subreddits.__name__,
             [a.display_name for a in self.user.moderator_subreddits()]),
            (self.user.subreddits.__name__,
             [a.display_name for a in self.user.subreddits()]),
            (self.user.blocked.__name__,
             [a.display_name for a in self.user.blocked()]),
            (self.user.friends.__name__,
             [a.display_name for a in self.user.friends()]),
            (self.user.multireddits.__name__,
             [a.display_name for a in self.user.multireddits()])])
        return strip_all(output)
