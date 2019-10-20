"""Scrapper Module."""

import const
import helpers as hlp
import praw as pr


class Scraper:
    """Scrape data from reddit to dict format."""

    def __init__(self):
        """Initialize the scraper."""

    # Class Helper Functions

    @staticmethod
    def fetch(fetchable):
        if fetchable._fetched is False:
            fetchable._fetch()

    @staticmethod
    def list_of_display_names(lg):
        """TODO: Document me"""
        return lg.__name__, [a.display_name for a in lg()]

    @staticmethod
    def list_of_ids(lg):
        """Scrape list generator to id.

        Given one of praw's list generators, it will return a list of ids
        from the items in the list generator.

        Return
        ------
        a tuple containing a key name and value as a list with scraped data.

        """
        return lg.__name__, [a.id for a in lg()]

    @staticmethod
    def list_of_names(lg):
        """Scrape list generator to name.

        Given one of praw's list generators, it will return a list of names
        from the items in the list generator.

        Return
        ------
        a tuple containing a key name and value as a list with scraped data.

        """
        return lg.__name__, [a.name for a in lg()]

    # Top Level Scrapers

    @staticmethod
    def comment(comment: pr.reddit.models.Comment):
        """Scrape a comment.

        This function will scrape the comment return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        sc = Scraper
        sc.fetch(comment)
        output = dict(vars(comment))
        del output[const.SCRAPE_DEL_REDDIT]
        output[const.SCRAPE_AUTHOR] = output[const.SCRAPE_AUTHOR].name
        output[const.SCRAPE_SUBREDDIT] = output[const.SCRAPE_SUBREDDIT].name
        output.update([
            (const.SCRAPE_TYPE, comment.__class__.__name__),
            hlp.get_timestamp(),
            hlp.get_version_stamp(),
        ])

    @staticmethod
    def inbox(inbox: pr.reddit.models.Inbox):
        """Scrape inbox.

        This function will scrape the inbox return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        sc = Scraper
        output = dict()
        output.update([
            (const.SCRAPE_TYPE, inbox.__class__.__name__),
            sc.list_of_ids(inbox.all),
            sc.list_of_ids(inbox.mentions),
            sc.list_of_ids(inbox.sent),
            sc.list_of_ids(inbox.unread),
            hlp.get_timestamp()])
        return output

    @staticmethod
    def message(message: pr.reddit.models.Message):
        """Scrape a message.

        This function will scrape a message and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        # TODO: Implement me.

    @staticmethod
    def multireddit(multi: pr.reddit.models.Multireddit):
        """Scrape a multi reddit.

        This function will scrape the multiredit return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        sc = Scraper

        sc.fetch(multi)
        output = dict(vars(multi))
        output['author_id'] = output['_author'].id
        del output['_reddit']
        del output['_author']
        output.update([
            ('multireddit', multi.__class__.__name__),
            hlp.get_timestamp(),
            ('comments', [a.id for a in multi.comments()]),
            sc.list_of_ids(multi.controversial),
            sc.list_of_ids(multi.hot),
            sc.list_of_ids(multi.new),
            sc.list_of_ids(multi.rising),
            sc.list_of_ids(multi.top),
        ])
        output['subreddits'] = [a.display_name for a in output['subreddits']]
        return output

    @staticmethod
    def redditor(redditor: pr.reddit.models.Redditor):
        """Scrape a redditor.

        This function will scrape a redditor and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        sc = Scraper
        sc.fetch(redditor)
        output = dict(vars(redditor))
        del output['_reddit']
        output.update([
            hlp.get_timestamp(),
            sc.list_of_names(redditor.trophies),
            sc.list_of_names(redditor.multireddits),
        ])
        output['comments'] = {}
        output['comments'].update([
            sc.list_of_ids(redditor.comments.controversial),
            sc.list_of_ids(redditor.comments.hot),
            sc.list_of_ids(redditor.comments.new),
            sc.list_of_ids(redditor.comments.top),
        ])
        output['submissions'] = {}
        output['submissions'].update([
            sc.list_of_ids(redditor.submissions.controversial),
            sc.list_of_ids(redditor.submissions.hot),
            sc.list_of_ids(redditor.submissions.new),
            sc.list_of_ids(redditor.submissions.top),
        ])
        return output

    @staticmethod
    def submission(submission: pr.reddit.models.Submission):
        """Scrape a submission.

        This function will scrape a submission and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        # TODO: Implement me

    @staticmethod
    def subreddit(subreddit: pr.reddit.models.Subreddit):
        """Scrape a subreddit.

        This function will scrape a subreddit and return a data structure
        reflecting its state.

        Return
        ------
        a dict with scraped data.

        """
        sc = Scraper
        sc.fetch(subreddit)
        output = dict(vars(subreddit))
        del output['_reddit']
        output.update([
            hlp.get_timestamp(),
            ('comments', [a.id for a in subreddit.comments()]),
            sc.list_of_ids(subreddit.controversial),
            sc.list_of_ids(subreddit.hot),
            sc.list_of_ids(subreddit.new),
            sc.list_of_ids(subreddit.rising),
            sc.list_of_ids(subreddit.top)])
        return output

    @staticmethod
    def user(user: pr.reddit.models.User):
        """Scrape user.

        This function will scrape the user return a data structure reflecting
        its state.

        Return
        ------
        a dict with scraped data.

        """
        sc = Scraper
        output = dict()
        output.update([
            hlp.get_timestamp(),
            (const.SCRAPE_TYPE, user.__class__.__name__),
            (const.SCRAPE_ID, user._me.id),
            ('karma', dict(user.karma)),
            (user.preferences.__class__.__name__, dict(user.preferences())),
            sc.list_of_display_names(user.moderator_subreddits),
            sc.list_of_display_names(user.subreddits),
            sc.list_of_names(user.blocked),
            sc.list_of_names(user.friends),
            sc.list_of_names(user.multireddits),
        ])
        return output
