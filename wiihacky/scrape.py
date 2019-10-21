"""Scrapper Module.

    A collection of functions to scrape data-items from Reddit.
"""

import const
import helpers as hlp
import praw as pr


# Helper Functions

def strip_underscore(dct: dict):
    """TODO: Doccument Me"""
    if const.SCRAPE_DEL_AUTHOR in dct:
        del dct[const.SCRAPE_DEL_AUTHOR]
    if const.SCRAPE_DEL_AWARDERS in dct:
        del dct[const.SCRAPE_DEL_AWARDERS]
    if const.SCRAPE_DEL_FETCHED in dct:
        del dct[const.SCRAPE_DEL_FETCHED]
    if const.SCRAPE_DEL_REDDIT in dct:
        del dct[const.SCRAPE_DEL_REDDIT]
    if const.SCRAPE_DEL_REPLIES in dct:
        del dct[const.SCRAPE_DEL_REPLIES]
    if const.SCRAPE_DEL_SUBMISSION in dct:
        del dct[const.SCRAPE_DEL_SUBMISSION]
    return dct


def prep_dict(dct: dict, tp: str):
    """TODO: Doccument Me"""
    dct.update([
        (const.SCRAPE_TYPE, tp),
        hlp.get_timestamp(),
        hlp.get_version_stamp(),
    ])
    return dct


def fetch(fetchable):
    if fetchable._fetched is False:
        fetchable._fetch()


# Top Level Scrapers

def comment(cm: pr.reddit.models.Comment):
    """Scrape a comment.

    This function will scrape the comment return a data structure reflecting
    its state.

    Return
    ------
    a dict with scraped data.

    """
    fetch(cm)
    output = dict(vars(cm))
    prep_dict(output, cm.__class__.__name__)
    output[const.SCRAPE_AUTHOR] = output[const.SCRAPE_AUTHOR].name
    output[const.SCRAPE_SUBREDDIT] = output[const.SCRAPE_SUBREDDIT].name
    output[const.SCRAPE_REPLIES] = \
        [a.id for a in output[const.SCRAPE_DEL_REPLIES]]
    return strip_underscore(output)


def inbox(ib: pr.reddit.models.Inbox):
    """Scrape inbox.

    This function will scrape the inbox return a data structure reflecting
    its state.

    Return
    ------
    a dict with scraped data.

    """
    output = dict()
    prep_dict(output, ib.__class__.__name__)
    output.update([
        (ib.all.__name__, [a.id for a in ib.all()]),
        (ib.mentions.__name__, [a.id for a in ib.mentions()]),
        (ib.sent.__name__, [a.id for a in ib.sent()]),
        (ib.unread.__name__, [a.id for a in ib.unread()]),
    ])
    return strip_underscore(output)


def message(msg: pr.reddit.models.Message):
    """Scrape a message.

    This function will scrape a message and return a data structure
    reflecting its state.

    Return
    ------
    a dict with scraped data.
    """
    fetch(msg)
    output = dict(vars(msg))
    prep_dict(output, msg.__class__.__name__)
    output[const.SCRAPE_REPLIES] = [a.id for a in output[const.SCRAPE_REPLIES]]
    output[const.SCRAPE_AUTHOR] = output[const.SCRAPE_AUTHOR].name
    return strip_underscore(output)


def multireddit(mr: pr.reddit.models.Multireddit):
    """Scrape a multi reddit.

    This function will scrape the multiredit return a data structure
    reflecting its state.

    Return
    ------
    a dict with scraped data.

    """
    fetch(mr)
    output = dict(vars(mr))
    prep_dict(output, mr.__class__.__name__)
    output[const.SCRAPE_SUBREDDITS] = \
        [a.display_name for a in output[const.SCRAPE_SUBREDDITS]]
    output.update([
        (const.SCRAPE_COMMENTS, [a.id for a in mr.comments()]),
        (mr.controversial.__name__, [a.id for a in mr.controversial()]),
        (mr.hot.__name__, [a.id for a in mr.hot()]),
        (mr.new.__name__, [a.id for a in mr.new()]),
        (mr.rising.__name__, [a.id for a in mr.rising()]),
        (mr.top.__name__, [a.id for a in mr.top()]),
    ])
    return strip_underscore(output)


def redditor(rd: pr.reddit.models.Redditor):
    """Scrape a redditor.

    This function will scrape a redditor and return a data structure
    reflecting its state.

    Return
    ------
    a dict with scraped data.

    """
    fetch(rd)
    output = dict(vars(rd))
    prep_dict(output, rd.__class__.__name__)
    output.update([
        (rd.trophies.__name__, [a.name for a in rd.trophies()]),
        (rd.multireddits.__name__, [a.name for a in rd.multireddits()]),
    ])
    output[const.SCRAPE_COMMENTS] = {}
    output[const.SCRAPE_COMMENTS].update([
        (rd.comments.controversial.__name__,
         [a.id for a in rd.comments.controversial()]),
        (rd.comments.hot.__name__, [a.id for a in rd.comments.hot()]),
        (rd.comments.new.__name__, [a.id for a in rd.comments.new()]),
        (rd.comments.top.__name__, [a.id for a in rd.comments.top()]),
    ])
    output[const.SCRAPE_SUBMISSIONS] = {}
    output[const.SCRAPE_SUBMISSIONS].update([
        (rd.submissions.controversial.__name__,
         [a.id for a in rd.submissions.controversial()]),
        (rd.submissions.hot.__name__, [a.id for a in rd.submissions.hot()]),
        (rd.submissions.new.__name__, [a.id for a in rd.submissions.new()]),
        (rd.submissions.top.__name__, [a.id for a in rd.submissions.top()]),
    ])
    return strip_underscore(output)


def submission(sm: pr.reddit.models.Submission):
    """Scrape a submission.

    This function will scrape a submission and return a data structure
    reflecting its state.

    Return
    ------
    a dict with scraped data.

    """
    fetch(sm)
    output = dict(vars(sm))
    prep_dict(output, sm.__class__.__name__)
    del output[const.SCRAPE_DEL_REDDIT]
    output[const.SCRAPE_SUBREDDIT] = \
        output[const.SCRAPE_SUBREDDIT].display_name
    output[const.SCRAPE_AUTHOR] = output[const.SCRAPE_AUTHOR].name
    return strip_underscore(output)
    # TODO: Implement me


def subreddit(sr: pr.reddit.models.Subreddit):
    """Scrape a subreddit.

    This function will scrape a subreddit and return a data structure
    reflecting its state.

    Return
    ------
    a dict with scraped data.

    """
    fetch(sr)
    output = dict(vars(sr))
    prep_dict(output, sr.__class__.__name__)
    del output[const.SCRAPE_DEL_REDDIT]
    output.update([
        (const.SCRAPE_COMMENTS, [a.id for a in sr.comments()]),
        (sr.controversial.__name__, [a.id for a in sr.controversial()]),
        (sr.hot.__name__, [a.id for a in sr.hot()]),
        (sr.new.__name__, [a.id for a in sr.new()]),
        (sr.rising.__name__, [a.id for a in sr.rising()]),
        (sr.top.__name__, [a.id for a in sr.top()]),
    ])
    return output


def user(us: pr.reddit.models.User):
    """Scrape user.

    This function will scrape the user return a data structure reflecting
    its state.

    Return
    ------
    a dict with scraped data.

    """
    output = dict()
    prep_dict(output, us.__class__.__name__)
    output.update([
        (const.SCRAPE_NAME, us._me.name),
        (const.SCRAPE_KARMA, us.karma),
        (us.preferences.__class__.__name__, dict(us.preferences())),
        (us.moderator_subreddits.__name__,
         [a.display_name for a in us.moderator_subreddits()]),
        (us.subreddits.__name__, [a.display_name for a in us.subreddits()]),
        (us.blocked.__name__, [a.display_name for a in us.blocked()]),
        (us.friends.__name__, [a.display_name for a in us.friends()]),
        (us.multireddits.__name__, [a.display_name for a in us.multireddits()]),
    ])
    return output
