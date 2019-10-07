"""Scrapper Module."""

import const
import helpers as hlp


class Scraper:
    """Scrape data from reddit to dict format."""

    def __init__(self):
        """Initialize the scraper."""

    def scrape_inbox(self, inbox):
        """Scrape inbox.

        This function will scrape the inbox return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        recv = list(inbox.all())
        sent = list(inbox.sent())
        st_name, st_time = hlp.get_timestamp()

        return {
            const.SCRAPE_TYPE: inbox.__class__.__name__,
            st_name: st_time,
            inbox.all.__name__: [a.id for a in recv],
            inbox.sent.__name__: [a.id for a in sent]}

    def scrape_multireddit(self, multi):
        """Scrape a multi reddit.

        This function will scrape the multiredit return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        output = dict(vars(multi))
        del output['_reddit']
        output['subreddits'] = [a.id for a in output['subreddits']]
        auth = output['_author']
        del output['_author']
        output['author_id'] = auth.id
        st_name, st_time = hlp.get_timestamp()
        output[st_name] = st_time

        return output

    def scrape_redditor(self, redditor):
        """Scrape a redditor.

        This function will scrape a redditor and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        if not redditor._fetched:
            redditor._fetch()
        output = dict(vars(redditor))
        del output['_reddit']
        st_name, st_time = hlp.get_timestamp()
        output[st_name] = st_time
        return output

    def scrape_user(self, user):
        """Scrape user.

        This function will scrape the user return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        st_name, st_time = hlp.get_timestamp()

        return {
            st_name: st_time,
            const.SCRAPE_TYPE: user.__class__.__name__,
            const.SCRAPE_ID: user._me.id,
            user.blocked.__name__: [a.id for a in list(user.blocked())],
            user.friends.__name__: [a.id for a in list(user.friends())],
            user.karma.__name__: user.karma(),
            user.moderator_subreddits.__name__:
                [a.id for a in list(user.moderator_subreddits())],
            user.multireddits.__name__:
                [a.name for a in list(user.multireddits())],
            user.preferences.__class__.__name__: dict(user.preferences()),
            user.subreddits.__name__: [a.id for a in list(user.subreddits())]}
