"""Scrapper Module."""

import time as tm

import wiihacky.const as const


class Scraper:
    """Scrape data from reddit to dict format."""

    def __init__(self):
        """Initialize the scraper."""

    @staticmethod
    def get_timestamp():
        """Obtain a timestamp in utc unix."""
        return (const.SCRAPE_UTC_STAMP, int(tm.time()))

    def scrape_inbox(self, inbox):
        """Scrape inbox.

        This function will scrape the inbox return a data structure reflecting
        its state.
        Anything it had to evaluate (make a reddit request for) is returned
        also.

        Return
        ------
        This will return a tuple containing a dictionary with the scraped
        information, as well as a list of all praw objects that had to be
        evaluated to complete the task.

        """
        recv = list(inbox.all())
        sent = list(inbox.sent())
        st_name, st_time = self.get_timestamp()

        output = {
            const.SCRAPE_TYPE: inbox.__class__.__name__,
            st_name: st_time,
            inbox.all.__name__: [a.id for a in recv],
            inbox.sent.__name__: [a.id for a in sent]}

        xtras = recv + sent
        return (output, xtras)

    def scrape_multireddit(self, multi):
        """Scrape a multi reddit.

        This function will scrape the multiredit return a data structure
        reflecting its state.
        Anything it had to evaluate (make a reddit request for) is returned
        also.

        Return
        ------
        This will return a tuple containing a dictionary with the scraped
        information, as well as a list of all praw objects that had to be
        evaluated to complete the task.

        """
        output = dict(vars(multi))
        del output['_reddit']
        subs = output['subreddits']
        del output['subreddits']
        auth = output['_author']
        del output['_author']
        st_name, st_time = self.get_timestamp()
        output[st_name] = st_time

        xtras = subs + [auth]
        return (output, xtras)

    def scrape_user(self, user):
        """Scrape user.

        This function will scrape the user return a data structure reflecting
        its state.
        Anything it had to evaluate (make a reddit request for) is returned
        also.

        Return
        ------
        This will return a tuple containing a dictionary with the scraped
        information, as well as a list of all praw objects that had to be
        evaluated to complete the task.

        """
        # Pull all info
        me = user._me
        blck = list(user.blocked())
        frnd = list(user.friends())
        mods = list(user.moderator_subreddits())
        mult = list(user.multireddits())
        subs = list(user.subreddits())
        st_name, st_time = self.get_timestamp()

        # Put it in data
        output = {
            st_name: st_time,
            const.SCRAPE_TYPE: user.__class__.__name__,
            const.SCRAPE_ID: me.id,
            user.blocked.__name__: [a.id for a in blck],
            user.friends.__name__: [a.id for a in frnd],
            user.karma.__name__: user.karma(),
            user.moderator_subreddits.__name__: [a.id for a in mods],
            user.multireddits.__name__: [a.name for a in mult],
            user.preferences.__class__.__name__: dict(user.preferences()),
            user.subreddits.__name__: [a.id for a in subs]}

        xtras = blck + frnd + mods + mult + subs + [me]
        return (output, xtras)
