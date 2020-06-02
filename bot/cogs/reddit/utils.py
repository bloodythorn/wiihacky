import discord
import discord.ext.commands as disextc
import logging as lg
import os
import praw
import typing as typ


log = lg.getLogger(__name__)


# Checks
async def reddit_credential_check() -> bool:
    """ Check Reddit config for bot. """
    return all([
        'REDDIT_USER_AGENT' in os.environ,
        'REDDIT_CLIENT_ID' in os.environ,
        'REDDIT_CLIENT_SECRET' in os.environ,
        'REDDIT_USERNAME' in os.environ,
        'REDDIT_PASSWORD' in os.environ
    ])


def red_creds_check():
    # noinspection PyUnusedLocal
    async def predicate(ctx: disextc.Context) -> bool:
        """ Check Reddit config for bot."""
        if await reddit_credential_check():
            return True
        else:
            raise disextc.CommandError(
                r'No reddit credentials set in env')


# Pagination-related
# TODO: Make sure split doesn't happen in the middle of links.
async def display_submission(
        bot: disextc.Bot,
        msgble: discord.abc.Messageable,
        submission: praw.reddit.Submission,
        user: discord.User = None,
        clear: bool = True,
        stop: bool = True,
        eject: bool = True
) -> None:
    lg.getLogger(__name__).debug(f'Display Submission')

    embed = discord.Embed(color=0xff5700)
    embed.title = submission.title if len(submission.title) < 255 else \
        submission.title[:254]
    embed.url = submission.url if submission.is_self else \
        'https://www.reddit.com' + submission.permalink

    preview_image_link = ''
    if not submission.is_self:
        # It's either a video, image or poll post.
        if hasattr(submission, 'preview'):
            if 'images' in submission.preview:
                # noinspection PyTypeChecker
                preview_image_link = \
                    submission.preview['images'][0]['source']['url']
        # FIXME
        # I put this as protection should the line above fail. It's proven
        #   to do nothing.
        if preview_image_link == '':
            embed.set_image(url=submission.url)
        else:
            embed.set_thumbnail(url=preview_image_link)

    embed.set_author(
        name=submission.author.name,
        url=f'https://www.reddit.com/u/{submission.author.name}')

    from pagination import EmbedPaginator, linefy_submission_text
    await EmbedPaginator.paginate(
        bot,
        linefy_submission_text(submission.selftext), msgble, embed,
        max_size=1000,
        restrict_to_user=user,
        footer_text=f'r/{submission.subreddit.display_name} / {submission.id}',
        clear_on_timeout=clear,
        stop_button=stop,
        eject_button=eject)


async def display_comment(
        bot: disextc.Bot,
        msgble: discord.abc.Messageable,
        com: praw.reddit.Comment,
        user: discord.User = None,
        clear: bool = True,
        stop: bool = True,
        eject: bool = True
) -> None:
    lg.getLogger(__name__).debug(f'Display Comment')

    embed = discord.Embed(color=0xff5700)
    embed.title = com.submission.title \
        if len(com.submission.title) < 255 else \
        com.submission.title[:254]
    embed.url = 'https://www.reddit.com' + com.permalink
    embed.set_author(
        name=com.author.name,
        url=f'https://www.reddit.com/u/{com.author.name}')

    from pagination import EmbedPaginator, linefy_submission_text
    await EmbedPaginator.paginate(
        bot,
        linefy_submission_text(com.body), msgble, embed,
        max_size=1000,
        restrict_to_user=user,
        footer_text=f'{com.id}',
        clear_on_timeout=clear,
        stop_button=stop,
        eject_button=eject)


# praw uses tons of protected members we need access to.
# noinspection PyProtectedMember
async def tally_moderator_actions(
        history_limit: int,
        subreddit: praw.reddit.Subreddit = None,
        user_names: typ.List[str] = None,
        actions_names: typ.List[str] = None
):
    """Tally moderator log stats.

    Given a list of user names, and action names the mod log will
    be searched for results matching, and return a tally and a
    tuple containing the oldest entry in utc unix.

    If no user_names or action_names are given, it will return
    filter no entries in that category. (whitelist filter)

    Empty list as well.

    :param history_limit -> Integer with how many entries to search.
    :param subreddit -> The reddit subreddit to search.
    :param user_names -> List of user names to filter to.
    :param actions_names -> List of action names to filter to.
    :return a tuple containing a list of moderator log entries with
        given criteria, and the utc time code of the oldest entry.

    """
    # TODO: I'm sure this needs to check to see if the bot has access to the
    #   moderator log.
    log.debug(f'tally_moderator_actions: {history_limit}' 
              f'{subreddit.display_name} {user_names} {actions_names}')
    return_data = {}
    oldest_entry = None
    for log_entry in subreddit.mod.log(limit=history_limit):
        # Filter
        # A list of users was specified and mod wasn't found.

        if (user_names is not None and len(user_names) > 0) and \
                log_entry._mod not in user_names:
            continue
        # If an action name list was given and it wasn't in it.
        if (actions_names is not None or len(actions_names) > 0) and \
                log_entry.action not in actions_names:
            continue

        # Update Oldest Entry
        if oldest_entry is None or \
                log_entry.created_utc < oldest_entry:
            oldest_entry = log_entry.created_utc

        # Check if actor exists
        if log_entry._mod not in return_data:
            return_data[log_entry._mod] = {}

        # New Action for actor
        if log_entry.action not in return_data[log_entry._mod]:
            return_data[log_entry._mod][log_entry.action] = 1

        # Increment
        return_data[log_entry._mod][log_entry.action] += 1

    log.debug(f'tally_moderator_actions data: {return_data}, {oldest_entry}')
    return return_data, oldest_entry
