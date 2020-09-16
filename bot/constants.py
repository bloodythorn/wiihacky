import discord
import discord.ext.commands as disextc

# Constants

reserved_commands = [
    'giphy', 'tenor', 'tts', 'me', 'tableflip',
    'unflip', 'shrug', 'spoiler']

__version__ = 'v0.0.2'
text_wh_version = 'wiihacky_version'
text_wh_name = 'WiiHacks'
id_bloodythorn = 574629343142346757
id_wiihacks = 582816924359065611
id_wiihacky = 630280409137283085

reddit_user_role_id = 708924829679747073


txt_log_format = '%(asctime)s|%(name)s|%(levelname)s|%(message)s'
txt_log_file_name = 'botlog.log'
txt_log_path = 'logs'

max_log_files = 50
max_file_size = 2**16 * 8

command_chars = ('^',)
message_cache = 1000 * 10
retry_pause_secs = 10
moderator_and_up = [
    657740509854302222,
    708923965824827454,
    657743368415215637, ]


confirmation_message_subject = \
    'Associate your Discord r/WiiHacks account with your Reddit account!'
confirmation_message_body = \
    """{},

This private message is to help you associate your r/wiihacks Reddit account
with your r/wiihacks Discord account.

With this association you will gain the Redditor role, and access to
redditor-only areas in the discord.

If you did not request this, please ignore this PM. If you suspect mischief,
please contact the moderators of r/WiiHacks via modmail.

If you did request this confirmation, here are your instructions on what to do
next:

1. In your Discord, click on your username in the lower left. You should see
   a pop-up that says 'Copied!'
2. Now come back to this message and hit 'reply' down at the bottom.
3. When the reply window opens press ctrl-v to paste in your username#number.
4. Hit send.

You should be verified in a few minutes.

Please contact a moderator on
[r/WiiHacks via modmail](https://www.reddit.com/message/compose?to=/r/WiiHacks),
or on the [r/WiiHacks discord](https://discord.com/invite/6fsXnTr) #support
channel if you aren't verified in 24 hours.
"""

health_and_safety_text = """** **
     :warning: WARNING-HEALTH AND SAFETY

BEFORE PLAYING, READ YOUR OPERATIONS
  MANUAL FOR IMPORTANT INFORMATION
      ABOUT YOUR HEALTH AND SAFETY.

                          Also online at
          www.nintendo.com/healthsafety

                     Press Ⓐ to continue.
"""


# Helpers

# TODO: These both need to be replaced by codeblock paginators.
async def paginate(
        message: str,
        pag: disextc.Paginator = None
        ) -> disextc.Paginator:
    """ Helper to use the Paginator.

    Given a line of text it will format it and return the paginator to add
    more lines.

    :param message -> str type with message to send
    :param pag -> Pagenator to add to, or none to create a new.
    :return -> Paginator containing line of text.
    """
    if pag is None:
        pag = disextc.Paginator()
    pag.add_line(message)
    return pag


async def send_paginator(
        to: discord.abc.Messageable,
        pag: disextc.Paginator) -> None:
    """ Helper to send a paginator.

    Given a messageable and a paginator, this function will send the
    paginator the target.

    :param to -> Messageable recipient.
    :param pag -> Pagenator to send.
    :return None
    """
    for page in pag.pages:
        await to.send(page)
