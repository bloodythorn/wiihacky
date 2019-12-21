import logging as lg

from praw.models import User

from actions import (Action, action_concluded)
import actions.scrape.constants as const
import actions.scrape as scrape


class ScrapeUser(Action):
    """This action when given the user will scrape and save the data."""

    def __init__(self, log: lg.Logger, usr: User):
        """Only the user is needed."""
        Action.__init__(self, log)
        self.user = usr
        self.TXT_USER = self.user.__class__.__name__

    def execute(self):
        """Execute Action."""
        # Prep
        ac = const.TXT_START + ' ' + self.TXT_USER
        complete = False
        data = {}
        # Scrape
        try:
            self.log.info(ac + '.')
            data = self.scrape()
        except Exception as e:
            scrape.ex_occurred(self.log, ac + ':', e)
        # Save
        try:
            self.log.info(
                const.TXT_SAVING.format(self.TXT_USER.capitalize()))
            # Assemble filename and path
            fn = data[const.TXT_TYPE].lower() + '-' + \
                str(data[const.TXT_UTC_STAMP])
            from pathlib import Path
            pth = Path(const.DATA_DIR) / data[const.TXT_TYPE].lower() / fn
            # Confirm directories
            from os import makedirs
            makedirs(pth.parent, exist_ok=True)
            # Save File
            with open(pth.with_suffix(const.FILE_SUFFIX), 'w') as f:
                from yaml import safe_dump
                f.write(safe_dump(data))
            complete = True
        except Exception as e:
            scrape.ex_occurred(
                self.log, const.TXT_SAVING.format(self.TXT_USER), e)
        # End of Action
        action_concluded(self.log, ac, complete)

    def scrape(self):
        """Scrape user.

        This function will scrape the user return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        output = dict()
        scrape.prep_dict(output, self.TXT_USER)
        # noinspection PyProtectedMember
        output.update([
            (const.TXT_NAME, self.user._me.name),
            (const.TXT_KARMA,
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
        return scrape.strip_all(output)
