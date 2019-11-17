"""Scraper Module.

    A collection of functions to scrape data-items from Reddit. And actions
    that use them.
"""

import logging as lg
from pathlib import Path
import time as tm
import yaml as yl

import praw as pr

from actions import Action
import const


# TODO: Remove STRING const
# TODO: Docu
# TODO: Some of these functions need to move up a level.

AC_SCRAPE = 'Scraping'
AC_SAVE = 'Saving {} data'
OB_INBOX = 'Inbox'
OB_USER = 'User'
ER_FILESAVE = 'Could not save file: {}'
ER_VERDIREC = 'Could not verify directory: {}'


# Helper Functions

def fetch(fetchable):
    """This function will make sure the given praw item has been fetched.
    This does so by accessing restricted data members.
    """
    if const.SCRAPE_DEL_FETCHED in fetchable.__dict__ \
            and not fetchable._fetched:
        fetchable._fetch()


def gen_filename(scrape: dict):
    """When given a properly processed dict, it returns an appropriate
        filename.
    """
    tp = scrape[const.SCRAPE_TYPE]
    st = scrape[const.UTC_STAMP]

    file_name = ""

    # Dir or file?
    dir_name = tp

    if tp == const.TYPE_COMMENT or tp == const.TYPE_MESSAGE or \
            tp == const.TYPE_SUBMISSION:
        file_name = file_name + const.FILE_DELIM + scrape[const.KEY_ID]
    elif tp == const.TYPE_REDDITOR or tp == const.TYPE_SUBREDDIT:
        file_name = file_name + const.FILE_DELIM + scrape[const.KEY_NAME]
    elif tp == const.TYPE_MULTIREDDIT:
        file_name = file_name \
                   + const.FILE_DELIM \
                   + scrape[const.KEY_OWNER] \
                   + const.FILE_DELIM \
                   + scrape[const.KEY_NAME]

    file_name = file_name + str(st)

    file_name = file_name + const.FILE_SUFFIX

    return dir_name, file_name


def gen_timestamp():
    """Obtain a timestamp in utc unix."""
    return const.UTC_STAMP, int(tm.time())


def gen_version_stamp():
    """Obtain a stamp containing software version."""
    return const.VERSION_TEXT, const.__version__


def prep_dict(dct: dict, tp: str):
    """This function will prep a dict with all required information for
    storage.
    """
    dct.update(
        [(const.SCRAPE_TYPE, tp), gen_timestamp(), gen_version_stamp()])
    return dct


def save_file(file: str, data):
    """Given a filename/path and encodable data, this function will write
        that file.
    """
    with open(file, 'w') as f:
        f.write(yl.safe_dump(data))
    return True


def strip_all(dct: dict):
    """This function combines all strip functions to make sure a dictionary is
        encodable.
    """
    return strip_empty_string(strip_none(strip_underscore(dct)))


def strip_empty_string(dct: dict):
    """Strips all data containing an empty string."""
    return {i: dct[i] for i in dct if dct[i] != ''}


def strip_none(dct: dict):
    """Strips all keys who's data type is None."""
    return {i: dct[i] for i in dct if dct[i] is not None}


def strip_underscore(dct: dict):
    """Remove's praw's underscore members from the given dict."""
    return {i: dct[i] for i in dct if i[0] != '_'}


def verify_dir(ls: str):
    """Given a directory name, this function will verify that it exists,
        and if not, create it."""
    p = Path(ls)
    if not p.exists():
        p.mkdir()
    return p.exists()


# Scraper Functions

def sc_comment(cm: pr.reddit.models.Comment):
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
    output[const.SCRAPE_SUBMISSION] = output[const.SCRAPE_DEL_SUBMISSION]
    output[const.SCRAPE_REPLIES] = \
        [a.id for a in output[const.SCRAPE_DEL_REPLIES]]
    return strip_all(output)


def sc_inbox(ib: pr.reddit.models.Inbox):
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
    return strip_all(output)


def sc_message(msg: pr.reddit.models.Message):
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
    output[const.SCRAPE_DEST] = output[const.SCRAPE_DEST].name
    return strip_all(output)


def sc_multireddit(mr: pr.reddit.models.Multireddit):
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
    output[const.SCRAPE_PATH] = output[const.SCRAPE_DEL_PATH]
    output[const.SCRAPE_AUTHOR] = output[const.SCRAPE_DEL_AUTHOR].name
    output.update([
        (const.SCRAPE_COMMENTS, [a.id for a in mr.comments()]),
        (mr.controversial.__name__, [a.id for a in mr.controversial()]),
        (mr.hot.__name__, [a.id for a in mr.hot()]),
        (mr.new.__name__, [a.id for a in mr.new()]),
        (mr.rising.__name__, [a.id for a in mr.rising()]),
        (mr.top.__name__, [a.id for a in mr.top()]),
    ])
    return strip_all(output)


def sc_redditor(rd: pr.reddit.models.Redditor):
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
    output[const.SCRAPE_PATH] = output[const.SCRAPE_DEL_PATH]
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
    return strip_all(output)


def sc_submission(sm: pr.reddit.models.Submission):
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
    output[const.SCRAPE_SUBREDDIT] = \
        output[const.SCRAPE_SUBREDDIT].display_name
    output[const.SCRAPE_AUTHOR] = output[const.SCRAPE_AUTHOR].name
    sm.comments.replace_more(limit=0)
    output[const.SCRAPE_COMMENTS] = \
        [a.id for a in sm.comments.list()]
    return strip_all(output)


def sc_subreddit(sr: pr.reddit.models.Subreddit):
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
    output[const.SCRAPE_PATH] = output[const.SCRAPE_DEL_PATH]
    output.update([
        (const.SCRAPE_COMMENTS, [a.id for a in sr.comments()]),
        (sr.controversial.__name__, [a.id for a in sr.controversial()]),
        (sr.hot.__name__, [a.id for a in sr.hot()]),
        (sr.new.__name__, [a.id for a in sr.new()]),
        (sr.rising.__name__, [a.id for a in sr.rising()]),
        (sr.top.__name__, [a.id for a in sr.top()]),
    ])
    return strip_all(output)


def sc_user(us: pr.reddit.models.User):
    """Scrape user.

    This function will scrape the user return a data structure reflecting
    its state.

    Return
    ------
    a dict with scraped data.

    """
    output = dict()
    prep_dict(output, us.__class__.__name__)
    # noinspection PyProtectedMember
    output.update([
        (const.SCRAPE_NAME, us._me.name),
        (const.SCRAPE_KARMA,
         dict([(a.display_name, b) for a, b in us.karma().items()])),
        (us.preferences.__class__.__name__, dict(us.preferences())),
        (us.moderator_subreddits.__name__,
         [a.display_name for a in us.moderator_subreddits()]),
        (us.subreddits.__name__, [a.display_name for a in us.subreddits()]),
        (us.blocked.__name__, [a.display_name for a in us.blocked()]),
        (us.friends.__name__, [a.display_name for a in us.friends()]),
        (us.multireddits.__name__, [a.display_name for a in us.multireddits()]),
    ])
    return strip_all(output)


def action_concluded(log: lg.Logger, ac: str, complete: bool):
    """This will log the conclusion of the action."""
    log.info(
        '{} action concluded with{} issues.'.format(
            ac,
            "out" if complete else ""))


def ex_occurred(log: lg.Logger, tp: str, e: Exception):
    """Will log exceptions."""
    err = 'An exception occurred while {}: {}'
    log.error(err.format(tp, e))


# Scraper Actions

class ScrapeInbox(Action):
    """This action when given the inbox will scrape and save the data."""

    def __init__(self, log: lg.Logger, inbox: pr.reddit.models.Inbox):
        """Only the inbox is needed."""
        Action.__init__(self, log)
        self.inbox = inbox

    def execute(self):
        """Execute Action."""
        # Prep
        ac = AC_SCRAPE + ' ' + OB_INBOX
        complete = False
        result = {}
        # Scrape
        try:
            self.log.info(ac + '.')
            result = sc_inbox(self.inbox)
        except Exception as e:
            ex_occurred(self.log, ac + ':', e)
        # Save
        try:
            self.log.info(AC_SAVE.format(OB_INBOX))
            pfn = gen_filename(result)
            fn = pfn[0] + const.FILE_PATH + pfn[1]
            if verify_dir(pfn[0]):
                if save_file(fn, result):
                    complete = True
                else:
                    self.log.error(ER_FILESAVE.format(fn))
            else:
                self.log.error(ER_VERDIREC.format(pfn[0]))
        except Exception as e:
            ex_occurred(self.log, AC_SAVE.format(OB_INBOX), e)
        # End of Action
        action_concluded(self.log, ac, complete)


class ScrapeUser(Action):
    """This action when given the user will scrape and save the data."""

    def __init__(self, log: lg.Logger, user: pr.reddit.models.User):
        """Only the user is needed."""
        Action.__init__(self, log)
        self.user = user

    def execute(self):
        """Execute Action."""
        # Prep
        ac = AC_SCRAPE + ' ' + OB_USER
        complete = False
        result = {}
        # Scrape
        try:
            self.log.info(ac + '.')
            result = sc_user(self.user)
        except Exception as e:
            ex_occurred(self.log, ac + ':', e)
        # Save
        try:
            self.log.info(AC_SAVE.format(OB_USER))
            pfn = gen_filename(result)
            fn = pfn[0] + const.FILE_PATH + pfn[1]
            if verify_dir(pfn[0]):
                if save_file(fn, result):
                    complete = True
                else:
                    self.log.error(ER_FILESAVE.format(fn))
            else:
                self.log.error(ER_VERDIREC.format(pfn[0]))
        except Exception as e:
            ex_occurred(self.log, AC_SAVE.format(OB_USER), e)
        # End of Action
        action_concluded(self.log, ac, complete)


class ScrapeComment(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass


class ScrapeMessage(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass


class ScrapeSubmission(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass


class ScrapeMultireddit(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass


class ScrapeRedditor(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass


class ScrapeSubreddit(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass


class ScrapeWiki(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass


class ScrapeWikiPage(Action):

    def __init__(self, log: lg.Logger):
        Action.__init__(self, log)
        pass

    def execute(self):
        pass
