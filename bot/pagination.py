import asyncio
import contextlib as ctxlib
import discord
import discord.ext.commands as disextc
import logging
import praw
import typing as typ

# Control Emoji
EMOJI_BEGIN = u"\u23EE"  # [:track_previous:]
EMOJI_BACK = u"\u2B05"   # [:arrow_left:]
EMOJI_FORE = u"\u27A1"   # [:arrow_right:]
EMOJI_END = u"\u23ED"    # [:track_next:]
EMOJI_EJECT = u"\u23cf"  # eject button | 1410 | U+23CF
EMOJI_STOP = u"\u23F9"   # [:stop_button:]

log = logging.getLogger(__name__)


class Paginator():

    def __init__(self, data):
        # Check to make sure data is acceptable type
        pass

# What do we need?
# A paginator that can display its information either in an embed or
# descriprtion text
# what is the input?
# Text Blobs and Lists of objects that are text printable.
# what does it need to do? from simple to complex
# Display a paginated blob of text that means:
#   Text is split into chunks that will keep it below the 2000char max


class EmptyPaginatorEmbed(Exception):
    """Raised when attempting to paginate with empty contents."""
    pass


class EmbedPaginator(disextc.Paginator):
    """
    A class that aids in paginating code blocks for Discord messages.

    Available attributes include:
    * prefix: `str`
        The prefix inserted to every page. e.g. three back ticks.
    * suffix: `str`
        The suffix appended at the end of every page. e.g. three back ticks.
    * max_size: `int`
        The maximum amount of code points allowed in a page.
    * max_lines: `int`
        The maximum amount of lines allowed in a page.
    """

    # noinspection PyMissingConstructor
    def __init__(self,
                 prefix: str = "",
                 suffix: str = "",
                 max_size: int = 2000,
                 max_lines: int = None,
                 ) -> None:
        """
        This function overrides the Paginator.__init__ from inside
        discord.ext.commands.

        It overrides in order to allow us to configure the maximum number of
        lines per page.
        """
        self.prefix = prefix
        self.suffix = suffix
        self.max_size = max_size - len(suffix)
        self.max_lines = max_lines
        self._current_page = [prefix]
        self.current_read_page = 0
        self._line_count = 0
        self._count = len(prefix) + 1  # prefix + newline
        self._pages = []

    def add_line(self,
                 line: str = '',
                 *,
                 empty: bool = False
                 ) -> None:
        """
        Adds a line to the current page.

        If the line exceeds the `self.max_size` then an exception is raised.

        This function overrides the `Paginator.add_line` from inside
        `discord.ext.commands`.

        It overrides in order to allow us to configure the maximum number of
        lines per page.
        """
        if len(line) > self.max_size - len(self.prefix) - 2:
            raise RuntimeError('Line exceeds maximum page size %s' %
                               (self.max_size - len(self.prefix) - 2))

        if self.max_lines is not None:
            if self._line_count >= self.max_lines:
                self._line_count = 0
                self.close_page()

            self._line_count += 1
        if self._count + len(line) + 1 > self.max_size:
            self.close_page()

        self._count += len(line) + 1
        self._current_page.append(line)

        if empty:
            self._current_page.append('')
            self._count += 1

    def get_page_number_text(self):
        return f" {self.current_read_page + 1}/{len(self.pages)})"

    def add_lines(self, lines: [str], empty: bool = False):
        """ For adding more than one line at a time. """
        for line in lines:
            try:
                self.add_line(line, empty=empty)
            except Exception:
                log.exception(f"line add failed: '{line}'")
                raise
            # else:
                # log.debug(f"line added: '{line}'")

    def get_page(self):
        if not self.pages:
            return ''
        else:
            return self.pages[self.current_read_page]

    def first_page(self):
        self.current_read_page = 0
        return self.get_page()

    def last_page(self):
        self.current_read_page = len(self.pages) - 1
        return self.get_page()

    def next_page(self):
        if self.current_read_page < len(self.pages) - 1:
            self.current_read_page += 1
        return self.get_page()

    def prev_page(self):
        if self.current_read_page > 0:
            self.current_read_page -= 1
        return self.get_page()

    @classmethod
    async def paginate(
        cls,
        bot: disextc.Bot,
        lines: typ.List[str],
        msgble: discord.abc.Messageable,
        embed: discord.Embed,
        max_lines: typ.Optional[int] = None,
        max_size: int = 500,
        empty: bool = False,
        restrict_to_user: discord.User = None,
        timeout: int = 300,
        clear_on_timeout: bool = True,
        footer_text: str = None,
        stop_button: bool = True,
        eject_button: bool = True
    ) -> typ.Optional[discord.Message]:
        """
        Use a paginator and set of reactions to provide pagination over a set
        of lines.

        The reactions are used to switch page, or to finish with pagination.

        When used, this will send a message using `ctx.send()` and apply a set
        of reactions to it. These reactions may be used to change page, or to
        remove pagination from the message.

        Pagination will also be removed automatically if no reaction is added
        for five minutes (300 seconds).

        Example:
        # >>> embed = discord.Embed()
        # >>> embed.set_author(name="Some Operation", url=url, icon_url=icon)
        # >>> await LinePaginator.paginate([line for line in lines], ctx, embed)
        :param bot: -> Bot mediating pagination
        :param lines: -> Array of strings to output
        :param msgble: -> Invocation Context
        :param embed: -> Embed to use
        :param max_lines: -> Max lines allowed per page.
        :param max_size: -> Max size of a line
        :param empty: -> Add empty line after each line?
        :param restrict_to_user: -> Only let calling user control.
        :param timeout: -> Amount of time to listen for reaction.
        :param clear_on_timeout
        :param footer_text: -> Text to display on the footer.
        :param stop_button
        :param eject_button
        :return: None
        """

        def event_check(
                reaction_: discord.Reaction,
                user_: discord.Member,
        ) -> bool:
            """Make sure that this reaction is what we want to operate on."""
            no_restrictions = (
                # Pagination is not restricted
                not restrict_to_user
                # The reaction was by a whitelisted user
                or user_.id == restrict_to_user.id
            )

            return (
                # Conditions for a successful pagination:
                all((
                    # Reaction is on this message
                    reaction_.message.id == message.id,
                    # Reaction is one of the pagination emotes
                    str(reaction_.emoji) in pagination_emoji,
                    # Reaction was not made by the Bot
                    user_.id != bot.user.id,
                    # There were no restrictions
                    no_restrictions
                ))
            )

        paginator = cls(max_size=max_size, max_lines=max_lines)

        # Add lines
        paginator.add_lines(lines, empty)
        log.debug(f"Paginator created with {len(paginator.pages)} pages")

        embed.description = paginator.get_page()

        # Single Page
        if len(paginator.pages) <= 1:
            if footer_text:
                embed.set_footer(text=get_footer(footer_text))
                log.debug(f"Setting embed footer to '{footer_text}'")
            log.debug(
                "There's less than two pages sending single page on its own")
            return await msgble.send(embed=embed)
        # Multi-Page
        else:
            embed.set_footer(
                text=get_footer(
                     footer_text,
                     paginator.current_read_page + 1,
                     len(paginator.pages)))

            log.debug("Sending first page to channel...")
            message = await msgble.send(embed=embed)

        log.debug("Adding emoji reactions to message...")
        # Add all the applicable emoji to the message
        pagination_emoji = (EMOJI_BEGIN, EMOJI_BACK, EMOJI_FORE, EMOJI_END)
        if stop_button:
            pagination_emoji += (EMOJI_STOP,)
        if eject_button:
            pagination_emoji += (EMOJI_EJECT,)
        for emoji in pagination_emoji:
            log.debug(f"Adding reaction: {repr(emoji)}")
            await message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await bot.wait_for(
                    "reaction_add", timeout=timeout, check=event_check)
                log.debug(f"Got reaction: {reaction}")
            except asyncio.TimeoutError:
                log.debug("Timed out waiting for a reaction")
                if clear_on_timeout:
                    await message.delete(delay=15)
                return await message.clear_reactions()
                # We're done, no reactions for the last 5 minutes

            if str(reaction.emoji) == EMOJI_STOP:
                log.debug("Got delete reaction")
                return await message.delete()

            if str(reaction.emoji) == EMOJI_EJECT:
                log.debug("got eject reaction")
                return await message.clear_reactions()

            if reaction.emoji == EMOJI_BEGIN:
                await message.remove_reaction(reaction.emoji, user)

                embed.description = paginator.first_page()

                footer = "(Page " + paginator.get_page_number_text()+")"
                if footer_text:
                    footer = footer_text + " " + footer
                embed.set_footer(text=footer)

                log.debug(f"begin: " + paginator.get_page_number_text())
                await message.edit(embed=embed)

            if reaction.emoji == EMOJI_END:
                await message.remove_reaction(reaction.emoji, user)

                embed.description = paginator.last_page()

                footer = "(Page " + paginator.get_page_number_text()+")"
                if footer_text:
                    footer = footer_text + " " + footer
                embed.set_footer(text=footer)

                log.debug(f"end: " + paginator.get_page_number_text())
                await message.edit(embed=embed)

            if reaction.emoji == EMOJI_BACK:
                await message.remove_reaction(reaction.emoji, user)

                if paginator.current_read_page <= 0:
                    log.debug("Page->Prev on page 0")
                    continue

                embed.description = paginator.prev_page()

                embed.description = paginator.pages[paginator.current_read_page]

                footer = "(Page " + paginator.get_page_number_text()+")"
                if footer_text:
                    footer = footer_text + " " + footer
                embed.set_footer(text=footer)

                log.debug(f"prev: " + paginator.get_page_number_text())
                await message.edit(embed=embed)

            if reaction.emoji == EMOJI_FORE:
                await message.remove_reaction(reaction.emoji, user)

                if paginator.current_read_page >= len(paginator.pages) - 1:
                    log.debug("Next->Page on last page")
                    continue

                embed.description = paginator.next_page()

                footer = "(Page " + paginator.get_page_number_text()+")"
                if footer_text:
                    footer = footer_text + " " + footer
                embed.set_footer(text=footer)

                log.debug(f"next: " + paginator.get_page_number_text())
                await message.edit(embed=embed)

        log.debug("Ending pagination and clearing reactions.")
        with ctxlib.suppress(discord.NotFound):
            await message.clear_reactions()


class RedditItemPaginator(disextc.Paginator):

    # TODO: This should return the selected message for another paginator.
    # Note: This should take a list of reddit.Message or reddit.Comment,
    #   or reddit.Submission
    @classmethod
    async def paginate(
        cls,
        bot: disextc.Bot,
        lines: typ.List[typ.Union[
            praw.reddit.Submission,
            praw.reddit.Comment,
            praw.reddit.models.Message]],
        msgble: discord.abc.Messageable,
        restrict_to_user: discord.User = None,
        timeout: int = 300,
        clear_on_timeout: bool = True,
        header_text: str = None,
        stop_button: bool = True,
        eject_button: bool = True
    ) -> typ.Tuple[discord.Message, typ.Union[
            praw.reddit.Submission,
            praw.reddit.Comment,
            praw.reddit.models.Message]]:
        """Given a list of reddit items this will paginate it into a
        navigable list.
        """
        pass


def linefy_submission_text(text: str, max_size: int = 975):
    # &#x200B;
    strip_dis = '&#x200B;'

    def split_dis(a: str):
        if len(a) < max_size:
            return a, ''
        else:
            return a[max_size + 1:], a[0:max_size]
    lines = []
    for line in text.split('\n'):
        if line.strip().replace(strip_dis, '') != '':
            while len(line) > max_size:
                line, split = split_dis(line)
                lines.append(split.strip().replace(strip_dis, ''))
            lines.append(line.strip().replace(strip_dis, ''))
    return lines


def get_footer(txt: str = '', page=None, last=None):
    output = txt
    if txt != '' and page is not None:
        output += f' (Page {page}'
        if last:
            output += f'/{last}'
        output += ')'
    return output
