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
        del output[const.SCRAPE_DEL_AUTHOR]
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


def list_of_display_names(name: str, lg: pr.reddit.models.ListingGenerator):
    """Scrape list generator to display_names.

    Given one of praw's list generators, it will return a list of display_names
    from the items in the list generator.

    Return
    ------
    a tuple containing a key name and value as a list with scraped data.

    """
    return name, [a.display_name for a in lg]


def list_of_ids(name: str, lg: pr.reddit.models.ListingGenerator):
    """Scrape list generator to id.

    Given one of praw's list generators, it will return a list of ids
    from the items in the list generator.

    Return
    ------
    a tuple containing a key name and value as a list with scraped data.

    """
    return name, [a.id for a in lg]


def list_of_names(name: str, lg: pr.reddit.models.ListingGenerator):
    """Scrape list generator to name.

    Given one of praw's list generators, it will return a list of names
    from the items in the list generator.

    Return
    ------
    a tuple containing a key name and value as a list with scraped data.

    """
    return name, [a.name for a in lg]


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
        list_of_ids(ib.all.__name__, ib.all()),
        list_of_ids(ib.mentions.__name__, ib.mentions()),
        list_of_ids(ib.sent.__name__, ib.sent()),
        list_of_ids(ib.unread.__name__, ib.unread()),
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
        list_of_ids(mr.controversial),
        list_of_ids(mr.hot),
        list_of_ids(mr.new),
        list_of_ids(mr.rising),
        list_of_ids(mr.top),
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
        list_of_names(rd.trophies),
        list_of_names(rd.multireddits),
    ])
    output[const.SCRAPE_COMMENTS] = {}
    output[const.SCRAPE_COMMENTS].update([
        list_of_ids(rd.comments.controversial),
        list_of_ids(rd.comments.hot),
        list_of_ids(rd.comments.new),
        list_of_ids(rd.comments.top),
    ])
    output[const.SCRAPE_SUBMISSIONS] = {}
    output[const.SCRAPE_SUBMISSIONS].update([
        list_of_ids(rd.submissions.controversial),
        list_of_ids(rd.submissions.hot),
        list_of_ids(rd.submissions.new),
        list_of_ids(rd.submissions.top),
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
    del output[const.SCRAPE_DEL_REDDIT]
    output.update([
        hlp.get_timestamp(),
        (const.SCRAPE_COMMENTS, [a.id for a in sr.comments()]),
        list_of_ids(sr.controversial),
        list_of_ids(sr.hot),
        list_of_ids(sr.new),
        list_of_ids(sr.rising),
        list_of_ids(sr.top)])
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
    output.update([
        hlp.get_timestamp(),
        (const.SCRAPE_TYPE, us.__class__.__name__),
        (const.SCRAPE_ID, us._me.id),
        (const.SCRAPE_KARMA, us.karma),
        (us.preferences.__class__.__name__, dict(us.preferences())),
        list_of_display_names(us.moderator_subreddits),
        list_of_display_names(us.subreddits),
        list_of_names(us.blocked),
        list_of_names(us.friends),
        list_of_names(us.multireddits),
    ])
    return output
