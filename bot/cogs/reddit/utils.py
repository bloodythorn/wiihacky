import discord
import discord.ext.commands as disextc
import logging as lg
import praw


log = lg.getLogger(__name__)


# Checks

# TODO: timestamp: in dicscord output of submissions.

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
