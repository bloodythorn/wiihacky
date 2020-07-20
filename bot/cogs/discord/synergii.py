import abc
import asyncio
import discord
import discord.ext.commands as disextc
import logging as lg
import prettytable as pt
import time
import typing as typ

log = lg.getLogger(__name__)

test_emojis = [u'🤟', u'🤞', u'🙋', u'🎱']
emoji_numbers = [
    u':zero:', u':one:', u':two:', u':three:', u':four:',
    u':five:', u':six:', u':seven:', u':eight:', u':nine:']
emoji_positive = u'\u2705'
emoji_negative = u'\u274c'
emoji_begin = u"\u23EE"  # [:track_previous:]
emoji_back = u"\u2B05"   # [:arrow_left:]
emoji_fore = u"\u27A1"   # [:arrow_right:]
emoji_end = u"\u23ED"    # [:track_next:]
emoji_eject = u"\u23cf"  # eject button | 1410 | u+23cf
emoji_stop = u"\u23F9"   # [:stop_button:]
emoji_list_yn = [emoji_positive, emoji_negative]
emoji_list_page = [emoji_begin, emoji_back, emoji_fore, emoji_end]
emoji_selections = [
    u'0️⃣', u'1️⃣', u'2️⃣', u'3️⃣', u'4️⃣',
    u'5️⃣', u'6️⃣', u'7️⃣', u'8️⃣', u'9️⃣']
max_char_per_send = 2000
max_selectable = 10


def generate_event_check(
    bot: disextc.Bot,
    message: discord.Message,
    restrict_to_reactions: typ.List[str] = None,
    restrict_to_users: typ.List[discord.User] = None,
):
    """This function generates an event check considering the parameters
    given.
    """
    def event_check(reaction, user) -> bool:
        reaction_restrictions = (
                not restrict_to_reactions or
                str(reaction.emoji) in restrict_to_reactions)
        user_restrictions = (
            not restrict_to_users or user in restrict_to_users)
        return all((
            reaction_restrictions, user_restrictions,
            reaction.message.id == message.id,
            user.id != bot.user.id))
    return event_check


async def poll_for_reactions(
        bot: disextc.Bot,
        message: discord.Message,
        number_of_reactions: int = 1,
        timeout: int = 60,
        restrict_to_reactions: typ.List[str] = None,
        restrict_to_users: typ.List[discord.User] = None,
) -> typ.List[typ.Tuple[discord.Reaction, discord.User]]:
    """This command will monitor a message for reactions.

    If given a list of emoji, it will add them as reactions if requested
     and only monitor for those specific emoji and ignore all others.

    If given a list of discord users, then it will only monitor reactions
     from those specific users and ignore all others.

    :param bot: -> discord bot
    :param message: -> message to monitor
    :param number_of_reactions: -> how many reactions to monitor
    :param timeout: -> how long to monitor before timing out
    :param restrict_to_reactions: -> reactions to monitor for
    :param restrict_to_users: -> users to restrict monitoring.
    :return: List of tuples(reaction, user)
    """
    log.debug(f'poll_for_reactions fired:'
              f'{message.content}'
              f'|{number_of_reactions}'
              f'|{timeout}'
              f'|{restrict_to_reactions}'
              f'|{restrict_to_users}')
    results = []
    reaction_count = 0
    start_time = time.time()
    while True:
        try:
            reaction, user = await bot.wait_for(
                event='reaction_add',
                check=generate_event_check(
                    bot=bot,
                    message=message,
                    restrict_to_users=restrict_to_users,
                    restrict_to_reactions=restrict_to_reactions),
                timeout=timeout)
            results.append((reaction, user))
            reaction_count += 1
        except asyncio.TimeoutError:
            pass

        if reaction_count >= number_of_reactions or \
                (time.time() - start_time) >= timeout:
            break
    return results


# FIXME: make sure this works.
async def yes_no_prompt(
        bot: disextc.Bot, message: discord.Message,
        restrict_to_users: typ.List[discord.User] = None,
        timeout: int = 300
) -> typ.Optional[typ.Tuple[bool, discord.User]]:
    emoji, user = await poll_for_reactions(
        bot=bot,
        message=message,
        restrict_to_reactions=emoji_list_yn,
        restrict_to_users=restrict_to_users,
        timeout=timeout)
    if emoji is None:
        return
    if emoji == emoji_positive:
        return True, user
    return False, user


class Pager(abc.ABC):
    """This abstract class designates an interface for a 'controller' to
    work on.
    """
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def goto_beginning(self):
        pass

    @abc.abstractmethod
    def goto_ending(self):
        pass

    @abc.abstractmethod
    def goto_next(self):
        pass

    @abc.abstractmethod
    def goto_last(self):
        pass

    @abc.abstractmethod
    def goto_page(self, p: int):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def eject(self):
        pass

    @abc.abstractmethod
    def select(self, n: int):
        pass

    @abc.abstractmethod
    async def monitor(self, ctx: disextc.Context):
        pass


class TablePager(Pager):

    def __init__(
            self,
            data: typ.List,
            stoppable: bool = True, ejectable: bool = True,
            selectable: bool = True,
            embed: discord.Embed = None):
        super().__init__()
        self._data = data
        self._embed = embed
        self._stoppable = stoppable,
        self._ejectable = ejectable,
        self._selectable = selectable
        self._display_data = None
        self._page_selected = 0
        self._items_per_page = None

    def goto_beginning(self):
        pass

    def goto_ending(self):
        pass

    def goto_next(self):
        pass

    def goto_last(self):
        pass

    def goto_page(self, p: int):
        pass

    def stop(self):
        pass

    def eject(self):
        pass

    def select(self, n: int):
        pass

    async def monitor(self, ctx: disextc.Context):

        # format data
        await self.prep_display()

        # display data
        # interactive loop until terminating condition
        pass

    async def prep_display(self):
        # Add items
        self._display_data = pt.PrettyTable()
        self._display_data.field_names = ['idx', 'item']
        for idx, item in enumerate(self._data):
            self._display_data.add_row([idx, repr(item)])

        await self.determine_display_size()

    async def determine_display_size(self):
        """This function sets the table to only as many items as can be
        displayed in under the discord limit or <= 10 if selectable.
        """
        # determine the displayable range
        # if selectable then 10 rows max.
        # if not, under 2k char
        self.end = len(self._rows) if not selectable else \
            min(max_selectable, len(self._rows))
        while True:
            if self.char_length() < max_char_per_send:
                break
            self.end -= 1
        self._items_per_page = self.end

        # Redo a proper index if paged
        if selectable:
            self.clear_rows()
            for idx, item in enumerate(self._data):
                self.add_row([idx % self._items_per_page, str(item)])


class TextPager(Pager):

    def __init__(
            self,
            data: str,
            stoppable: bool = True,
            ejectable: bool = True,
            selectable: bool = False,
            embed: discord.Embed = None):
        super().__init__()
        self._data = data
        self._embed = embed
        self._stoppable = stoppable,
        self._ejectable = ejectable,
        self._selectable = selectable

    def goto_beginning(self):
        pass

    def goto_ending(self):
        pass

    def goto_next(self):
        pass

    def goto_last(self):
        pass

    def goto_page(self, p: int):
        pass

    def stop(self):
        pass

    def eject(self):
        pass

    def select(self, n: int):
        pass

    async def monitor(self, ctx: disextc.Context):
        # prep data
        # display data
        # interactive loop until terminating condition
        pass


class PagedListTable(pt.PrettyTable):

    def __init__(self, data: typ.List, selectable: bool = False):
        super().__init__()
        self._data = data
        self._page_selected = 0
        self._items_per_page = None
        self._selectable = selectable

        # insert data with index
        self.field_names = ['index', 'item']
        for idx, item in enumerate(self._data):
            self.add_row([idx, repr(item)])

        # determine the displayable range
        # if selectable then 10 rows max.
        # if not, under 2k char
        self.end = len(self._rows) if not selectable else \
            min(max_selectable, len(self._rows))
        while True:
            if self.char_length() < max_char_per_send:
                break
            self.end -= 1
        self._items_per_page = self.end

        # Redo a proper index if paged
        if selectable:
            self.clear_rows()
            for idx, item in enumerate(self._data):
                self.add_row([idx % self._items_per_page, str(item)])

    def __len__(self):
        return len(self._rows)

    def __str__(self):
        return str(super()) + \
               f'\n{self.page_selected}/{self.last_page_number()}'

    def get_reaction_list(self) -> typ.List[str]:
        """Returns a list of reactions that would control this paged list."""
        reaction_list = []
        # > 1 page needs paging controls.
        if self.last_page_number() != 0:
            reaction_list += emoji_list_page
        # selectable needs selection controls
        if self._selectable:
            for i in range(len(self._rows[self.start:self.end])):
                reaction_list.append(emoji_selections[i])
        return reaction_list

    def last_page_number(self):
        if self._items_per_page is not None:
            return len(self._data) // self._items_per_page
    
    @property
    def page_selected(self):
        return self._page_selected

    def char_length(self):
        return len(str(self))

    def last(self):
        if self.page_selected > 0:
            self.goto_page(self.page_selected - 1)

    def next(self):
        if self.page_selected < self.last_page_number():
            self.goto_page(self._page_selected + 1)

    def goto_beginning(self):
        self.goto_page(0)

    def goto_end(self):
        self.goto_page(self.last_page_number())

    def goto_page(self, page_number: int = 0):
        self._page_selected = page_number
        self.start = self._page_selected * self._items_per_page
        self.end = self._page_selected * \
            self._items_per_page + \
            self._items_per_page

    async def get_selection(self, ctx: disextc.Context):
        """This runs the selection routine until exit or selection is made."""
        log.debug(f'{self.__class__.__name__}:get_selection fired')
        # send display list
        message = await ctx.send(f'```{str(self)}```')

        # populate reactions
        for react in self.get_reaction_list():
            await message.add_reaction(react)

        # poll/react for/to reactions
        running = True
        results = None
        while running:
            results = await poll_for_reactions(
                bot=ctx.bot,
                message=message,
                restrict_to_reactions=self.get_reaction_list())
            # There should only ever be one result returned.
            running = await self.react(str(results[0][0].emoji))
            if running:
                # If we're still going, refresh the display.
                await results[0][0].remove(results[0][1])
                await message.edit(content=f'```{str(self)}```')
        # return/save reaction or none
        await message.clear_reactions()
        # TODO: Make the results return a selection instead.
        return await self.get_item(results[0][0].emoji)

    async def react(self, reaction: str) -> bool:
        """Reacts to the action given."""
        log.debug(f'{self.__class__.__name__}: react fired: {reaction}')
        # We only need to react to paging reactions. Anything else stops the
        # display.
        if reaction == emoji_begin:
            self.goto_beginning()
            return True
        elif reaction == emoji_end:
            self.goto_end()
            return True
        elif reaction == emoji_back:
            self.last()
            return True
        elif reaction == emoji_fore:
            self.next()
            return True
        else:
            return False

    async def get_item(self, reaction: str):
        log.debug(f'get_item fired: {reaction}')
        for idx, item in enumerate(self._data[self.start:self.end]):
            log.debug(f'{idx}|{item}|{emoji_numbers[idx]}|{reaction}')
            if emoji_numbers[idx] == reaction:
                return item


class Synergii(disextc.Cog):
    """Module containing interactive functionality between the bot,
    Reddit, and Discord.

    This has taken over for the pagination module.
    """
    # TODO: Make the above not a lie.

    def __init__(self, bot: disextc.Bot):
        super(Synergii,).__init__()
        self.bot = bot

    # Helpers

    @staticmethod
    async def find_max_lines_for_ptable(
            table: pt.PrettyTable, selectable: bool = False
    ) -> pt.PrettyTable:
        """Given a ptable this will find the max displayable rows."""
        # If selectable we can only display 0-9 items at a time.
        # if selectable=False, you can display under the 2k limit.
        table.end = 1
        while True:
            if len(str(table)) > max_char_per_send:
                table.end -= 1
                break
            if table.end >= len(table._rows):
                table.end = None
                break
            if selectable and table.end >= max_selectable:
                table.end = max_selectable
                break
        return table

    @staticmethod
    async def paginate_list(
            bot: disextc.Bot, message: discord.Message,
            restrict_to_users: typ.List[discord.User] = None,
            data: typ.List = None,
            selectable: bool = True,
            stop: bool = True,
            eject: bool = True):
        """This takes any python list of items, and as long as they are string
        representable, it will put them in a paginated list.
        """
        # Prep Control Bar
        controls = emoji_list_page
        if stop:
            controls.append(emoji_stop)
        if eject:
            controls.append(emoji_eject)

        # Prep PTable
        display_table = pt.PrettyTable()
        display_table.field_names = ['index', 'item']
        for idx, item in enumerate(data):
            display_table.add_row([idx, repr(item)])

        # find max displayable
        display_table = await Synergii.find_max_lines_for_ptable(
            display_table, selectable)

        # poll_for_reactions
        await message.edit(content=f'```{str(display_table)}```')
        result = await poll_for_reactions(
            bot=bot, message=message,
            restrict_to_reactions=controls, timeout=300,
            restrict_to_users=restrict_to_users,
            )
        # handle reaction
        # repeat
        pass

    # Commands

    @disextc.group(name='syn', hidden=False)
    @disextc.is_owner()
    async def synergii_group(self, ctx: disextc.Context) -> None:
        """Group for synergii module commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"No subcommand given for syn group.")

    @synergii_group.command(name='test_sr', hidden=False)
    @disextc.is_owner()
    async def test_choose_single_reaction_command(
            self, ctx: disextc.Context) -> None:
        """Testing choosing a single reaction out of a set."""
        message = await ctx.send(
            f"This is a test of single reactions selection over 20 seconds.")

        results = await poll_for_reactions(
            bot=ctx.bot,
            message=message,
            restrict_to_reactions=test_emojis,
            number_of_reactions=1,
            timeout=20)

        await message.edit(content=f'results:```{results}```')

    @synergii_group.command(name='test_par', hidden=False)
    @disextc.is_owner()
    async def test_poll_all_reactions_command(
            self, ctx: disextc.Context) -> None:
        """Polls all reactions for 30 seconds without having a limit."""
        message = await ctx.send(
            f'This is a test of polling for all reactions for 30 seconds.')

        results = await poll_for_reactions(
            bot=ctx.bot,
            message=message,
            timeout=30)

        await message.edit(content=f'results:```{results}```')

    @synergii_group.command(name='test_yn', hidden=False)
    @disextc.is_owner()
    async def test_yes_no_prompt_command(self, ctx: disextc.Context) -> None:
        """For testing the yes/no interactive helper."""
        message = await ctx.send(f'This is a test of the SRE.')

        results = await yes_no_prompt(
            bot=ctx.bot,
            message=message,
            timeout=20)

        await message.edit(content=f'results:```{results}```')

    @synergii_group.command(name='test_dl', hidden=False)
    @disextc.is_owner()
    async def test_display_list_command(self, ctx: disextc.Context) -> None:
        """This tests the list display by displaying a list of loggers."""
        loggers = [lg.getLogger()]  # get the root logger
        # noinspection PyUnresolvedReferences
        loggers = loggers + [
            lg.getLogger(name) for name in lg.root.manager.loggerDict]
        test = TablePager(
            data=loggers,
            selectable=True,
            stoppable=True,
            ejectable=True)
        selection = await test.monitor()

        # test = PagedListTable(data=loggers, selectable=True)
        # select = await test.get_selection(ctx)
        # await ctx.send(f'Your selection was: {select}')
        # message = await ctx.send(f'```{str(test)}```')
        # results = await poll_for_reactions(
        #    bot=ctx.bot,
        #    message=message,
        #    timeout=300,
        #    restrict_to_reactions=test.get_reaction_list(),
        #    restrict_to_users=[ctx.message.author])
        await ctx.send(f'```selection:{selection}```')


def setup(bot: disextc.Bot) -> None:
    """ Loads synergism cog. """
    bot.add_cog(Synergii(bot))
