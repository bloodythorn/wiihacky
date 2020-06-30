import asyncio
import discord
import discord.ext.commands as disextc
import logging as lg
import math
import nltk
import praw
import prettytable as pt
import re
import torch
import typing as typ

log = lg.getLogger(__name__)

lab_id = 706358720111837316

# !lab add fv1ogou 1
# !lab add fv25mdi 3


class Laboratory(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self._cats = dict()
        self._ids = list()
        self._text_words = dict()
        self._training_data = list()
        self._data_tensor = None
        self._synapse_0 = None
        self._synapse_1 = None

    # Properties Are assured to always be sorted.

    @property
    async def categories(self):
        return list(sorted(self._cats))

    @property
    async def ids(self):
        return list(sorted(self._ids))

    @property
    async def word_bag(self):
        output = []
        for b in self._text_words.values():
            for word in b:
                if word not in output:
                    output.append(word)
        return list(sorted(output))

    @property
    async def trained(self):
        return self._synapse_0 is None and self._synapse_1 is None

    @disextc.group(name='lab', hidden=True)
    @disextc.is_owner()
    async def lab_group(self, ctx: disextc.Context):
        """Group for testing commands/applications."""
        if ctx.invoked_subcommand is None:
            await ctx.send(
                f'```WordBag sz:{len(await self.word_bag)}\n'
                f'Categories:{len(self._cats.keys())}\n'
                f'Comments :{len(self._ids)}```')

    @lab_group.command(name='add', hidden=True)
    @disextc.is_owner()
    async def add_data_command(
            self, ctx: disextc.Context, text_id: str, cat: typ.Optional[str]):
        async with ctx.typing():
            try:
                await self.add_data(text_id, cat)
                await ctx.send(f'{text_id} was added to category {cat}.')
            except Exception as e:
                await ctx.send(f'Unable to save id: {text_id}|{e.args}')

    @lab_group.command(name='clr', hidden=True)
    @disextc.is_owner()
    async def clear_data_command(self, ctx: disextc.Context):
        await self.clear_data()
        await ctx.send('All training data has been cleared.')

    @lab_group.command(name='trn', hidden=True)
    @disextc.is_owner()
    async def train_command(self, ctx: disextc.Context):
        async with ctx.typing():
            time = await self.train()
            await ctx.send(f'training finished in {time} seconds.')

    @lab_group.command(name='thk', hidden=True)
    @disextc.is_owner()
    async def think_command(self, ctx: disextc.Context, text_id: str):
        if self._synapse_0 is None or self._synapse_1 is None:
            raise disextc.CommandError(f"I have no mind.")
        results = await self.think(text_id=text_id)
        await ctx.send(f'think results: ```{results}```')

    @lab_group.command(name='whc', hidden=True)
    @disextc.is_owner()
    async def sift_wiihacks_comments_command(
            self, ctx: disextc.Context, num: int):
        log.debug(f'whc fired')
        reddit: praw.Reddit = await (self.bot.get_cog('Reddit')).reddit
        wiihacks: praw.reddit.models.Subreddit = reddit.subreddit('WiiHacks')
        comments = list(wiihacks.comments(limit=num))
        for comment in comments:
            await self.add_reddit_comment(comment=comment, cat=None)
            await asyncio.sleep(0.1)
        await ctx.send(f'{len(comments)} added to db')

    @lab_group.command(name='uni', hidden=True)
    @disextc.is_owner()
    async def unicode_conversion_command(
            self, ctx: disextc.Context, code: str):
        escape_sequence_re = re.compile(r'\\u[0-9a-fA-F]{4,5}')

        def _escape_sequence_to_char(match):
            return chr(int(match[0][2:], 16))

        def _parse_string_to_unicode(text: str):
            return re.sub(escape_sequence_re, _escape_sequence_to_char, text)

        await ctx.send(f"{_parse_string_to_unicode(code)}")

    # Helpers

    async def add_reddit_comment(
            self, comment: praw.reddit.models.Comment, cat: typ.Optional[str]):
        # Adding data requires retrain
        if await self.trained:
            await self.blank_mind()

        # make sure the comment exists,
        # if this throws, nothing gets done.
        comment._fetch()

        # add id?
        if comment.id not in self._ids:
            self._ids.append(comment.id)

        # Category
        if cat is not None:
            # add category?
            if cat not in self._cats:
                self._cats[cat] = list()
            # make sure id is recorded under the category.
            if comment.id not in self._cats[cat]:
                self._cats[cat].append(comment.id)

        # Save words
        self._text_words[comment.id] = list(sorted(
            await self.process_text(comment.body)))

    async def add_data(self, text_id: str, cat: typ.Optional[str]):
        reddit: praw.Reddit = await (self.bot.get_cog('Reddit')).reddit
        comment = reddit.comment(text_id)
        return await self.add_reddit_comment(comment, cat)

    async def blank_mind(self):
        self._synapse_0 = None
        self._synapse_1 = None

    @staticmethod
    async def bow(words: typ.List[str], bag: typ.List[str]
                  ) -> typ.List[int]:
        log.debug(f'bow fired {words}|{bag}')
        bits = []

        # Make key, tick present bits
        for word in bag:
            if word in words:
                bits.append(1)
            else:
                bits.append(0)
        log.debug(f'bow returning: {bits}')
        return bits

    @property
    async def get_data_matrix_size(self):
        return len(self._ids), len(await self.word_bag)

    @property
    async def get_train_results_matrix_size(self):
        return len(self._ids), len(await self.categories)

    async def get_train_results_data_matrix(self):
        return torch.zeros(
            await self.get_train_results_matrix_size,
            dtype=torch.float64,
            device='cpu')

    async def get_zeroes_data_matrix(self):
        return torch.zeros(await self.get_data_matrix_size)

    async def bow_all(self):
        log.debug(f'bow_all fired')

        # Go through each training example
        self._training_data.clear()
        x_data = await self.get_zeroes_data_matrix()
        y_data = await self.get_train_results_data_matrix()
        for idx, txt_id in enumerate(self._ids):
            # In Data
            in_ba = torch.tensor(await self.bow(
                self._text_words[txt_id], await self.word_bag))
            x_data[idx, ] = in_ba
            # Out Data
            id_cats = []
            cats = await self.categories
            for cat in cats:
                if txt_id in self._cats[cat]:
                    id_cats.append(cat)
            out_ba = torch.tensor(await self.bow(id_cats, cats))
            y_data[idx, ] = out_ba
            self._training_data.append((in_ba, out_ba))
        self._data_tensor = (x_data, y_data)

    async def clear_data(self):
        await self.blank_mind()
        self._ids.clear()
        self._cats.clear()
        self._text_words.clear()

    @staticmethod
    async def process_text(text: str) -> typ.List[str]:
        words = nltk.word_tokenize(text)

        # strip stop words
        from nltk.corpus import stopwords
        words = [w for w in words if w not in stopwords.words('english')]

        # stem and remove duplicates
        words = list(set([
            nltk.stem.lancaster.LancasterStemmer().stem(w) for w in words]))

        # And finally strip out odd symbols and punctuation.
        alpha_regex = r'[^A-Za-z0-9]+'
        # fixme: I feel the conditional is backward. But it WAE.
        words = [a for a in words if re.match(alpha_regex, a) is None]

        return words

    async def get_text(self, target: str) -> str:
        output = ''
        try:
            reddit: praw.Reddit = await (self.bot.get_cog('Reddit')).reddit
            comment = reddit.comment(target)
            output = comment.body
        except Exception as e:
            log.debug(f'Going through the exception:{e.args}')
        return output

    async def think(self, text_id: str):
        log.debug(f'think fired')
        text = await self.get_text(text_id)
        log.debug(f'text: {text}')
        clean_text = await self.process_text(text)
        log.debug(f'cleaned_text: {clean_text}')
        X = torch.zeros(len(self._ids), len(await self.word_bag))
        x = torch.tensor(await self.bow(clean_text, await self.word_bag))
        log.debug(f'tensor\n{X+x}')
        y_pred = (X+x).mm(self._synapse_0).clamp(min=0).mm(self._synapse_1)
        log.debug(f'y_predictions:\n{y_pred[0,]}')
        return y_pred[0,]

    async def train(self):
        # Prep all in-out data
        from time import time
        await self.bow_all()

        # Define some starting params
        dtype = torch.float
        device = torch.device("cpu")
        batch_size = len(self._training_data)
        input_size = len(await self.word_bag)
        output_size = len(await self.categories)
        hidden_size = 1000

        # Make a short alias for our data.
        x = self._data_tensor[0]
        y = self._data_tensor[1]
        log.debug(f'Traning data moved to tensor\n{x}\n{y}')

        start_time = time()

        # randomly generate our starting synapses
        # Create random Tensors for weights.
        # Setting requires_grad=True indicates that we want to compute
        # gradients with respect to these Tensors during the backward pass.
        self._synapse_0 = torch.randn(
            input_size, hidden_size, device=device, dtype=dtype,
            requires_grad=True)
        self._synapse_1 = torch.randn(
            hidden_size, output_size, device=device, dtype=dtype,
            requires_grad=True)
        log.debug(
            f'Synapses initialized to : \n{self._synapse_0}\n{self._synapse_1}')

        learning_rate = 1e-6
        epochs = 500
        for t in range(epochs):
            # Forward pass
            y_pred = x.mm(self._synapse_0).clamp(min=0).mm(self._synapse_1)

            loss = (y_pred - y).pow(2).sum()

            # Use autograd to compute the backward pass.
            loss.backward()

            with torch.no_grad():
                self._synapse_0 -= learning_rate * self._synapse_0.grad
                self._synapse_1 -= learning_rate * self._synapse_1.grad

                # Manually zero the gradients after updating weights
                self._synapse_0.grad.zero_()
                self._synapse_1.grad.zero_()
            # small sleep
            await asyncio.sleep(0.001)
        training_time = time() - start_time
        log.debug(f'Training finished in {training_time} seconds.')
        return training_time

    @lab_group.command(name='inb', hidden=True)
    @disextc.is_owner()
    async def inbox_display_command(self, ctx: disextc.Context):
        reddit: praw.Reddit = await (self.bot.get_cog('Reddit')).reddit
        test = InboxDisplay(ctx.bot, list(reddit.inbox.all(limit=None)))
        await test.run(ctx)


class InboxDisplay:

    EMOJI_PAGE_CONTROLS = [
        u"\u23EE", u"\u2B05", u"\u27A1", u"\u23ED"]

    EMOJI_EJECT = u"\u23cf"  # eject button
    EMOJI_STOP = u"\u23F9"  # [:stop_button:]

    EMOJI_NO_YES = [u"\u274c", u"\u2705"]

    EMOJI_NUMBERS = [u'0️⃣', u'1️⃣', u'2️⃣', u'3️⃣', u'4️⃣',
                     u'5️⃣', u'6️⃣', u'7️⃣', u'8️⃣', u'9️⃣']

    def __init__(
        self,
        bot: disextc.Bot,
        inbox: typ.List[typ.Union[
            praw.reddit.Comment,
            praw.reddit.models.Message]],
        user: typ.Optional[discord.User] = None
    ):
        # TODO: Make some settable at creation time?
        self.bot = bot
        self._inbox = inbox
        self._fields = [
            '#', 'id', 'subject', 'author', 'destination', 'created']
        self._display_table = pt.PrettyTable(field_names=self._fields)
        self.prep_table()
        self._page_number = 0
        self._lines_per_page = 7
        self._max_subject_row_size = 20
        self._max_author_row_size = 13
        self._prefix = "```"
        self._suffix = "```"
        self._eject_button = True
        self._stop_button = True
        # TODO: Lower value for testing
        self._timeout = 30
        self._clear_on_exit = True
        self._restrict_to_user = user
        self.result = None

    def prep_table(self):
        self._display_table.clear_rows()
        from datetime import datetime
        for idx, row in enumerate(self._inbox):
            # Add first items
            to_add = [idx + self._page_number * self._lines_per_page, row.id]

            # Test subject row length
            if len(row.subject) > self._max_subject_row_size:
                to_add.append(
                    row.subject[:self._max_subject_row_size - 3] + '...')
            else:
                to_add.append(row.subject)

            # Test author name length
            if len(row.author.name) > self._max_author_row_size:
                to_add.append(
                    row.author.name[:self._max_author_row_size - 3] + '...')
            else:
                to_add.append(row.author.name)
            to_add.extend([
                row.dest.name,
                str(datetime.utcfromtimestamp(
                    row.created).strftime("%y-%m-%dT%H:%M"))])
            self._display_table.add_row(to_add)

    @property
    async def page_number(self):
        return self._page_number

    @page_number.setter
    async def page_number(self, a):
        if a < 0 or a > await self.last_page_number:
            raise ValueError(f"'{a}' is out of document range.")
        self._page_number = a

    @property
    async def last_page_number(self) -> int:
        return math.ceil(len(self._inbox)/self._lines_per_page) - 1

    @property
    async def upper_index(self) -> int:
        return self._page_number * self._lines_per_page

    @property
    async def lower_index(self) -> int:
        return self._page_number * self._lines_per_page + self._lines_per_page

    @property
    async def display_page_items(self):
        return self._inbox[await self.upper_index:await self.lower_index]

    @property
    async def display_page_text(self):
        return self._prefix + \
            'inbox:\n' + \
            str(self._display_table[
                await self.lower_index:await self.upper_index]) + \
            f'\np({self._page_number}/{await self.last_page_number})' + \
            self._suffix

    async def get_emoji_bar(self) -> typ.List[str]:
        emoji_bar = []
        # Do we need paging controls?
        if await self.last_page_number != 0:
            emoji_bar.extend(self.EMOJI_PAGE_CONTROLS)

        # Eject and or stop?
        if self._eject_button:
            emoji_bar.append(self.EMOJI_EJECT)
        if self._stop_button:
            emoji_bar.append(self.EMOJI_STOP)

        # Finally, number selections.
        for i in range(len(await self.display_page_items)):
            emoji_bar.append(self.EMOJI_NUMBERS[i])
        return emoji_bar

    async def page_control(self, operation: int):
        if operation < 0 or operation > len(self.EMOJI_PAGE_CONTROLS):
            raise ValueError(f'operation index not in range {operation}')
        if operation == 0:  # Beginning of docu
            # Set Page Numer
            self._page_number = 0
        elif operation == 1:  # Previous Page
            if self._page_number > 0:
                self._page_number -= 1
        elif operation == 2:  # Next Page
            if self._page_number < await self.last_page_number:
                self._page_number += 1
        elif operation == 3:  # End of docu
            self._page_number = await self.last_page_number

    async def display_to_message(
            self,
            target: typ.Union[discord.abc.Messageable, discord.Message]
    ) -> discord.Message:
        # Refresh Display
        if isinstance(target, discord.Message):
            await target.clear_reactions()
            await target.edit(content=await self.display_page_text)
            for emoji in await self.get_emoji_bar():
                await target.add_reaction(emoji)
            return target
        else:
            # New message, send and return.
            message = await target.send(await self.display_page_text)
            for emoji in await self.get_emoji_bar():
                await message.add_reaction(emoji)
            return message

    async def run(
            self,
            target: typ.Union[discord.abc.Messageable, discord.Message]
    ) -> typ.Optional[int]:
        log.debug(
            f'{InboxDisplay.__name__}.{InboxDisplay.run.__name__}')

        # First we want to send the initial display
        log.debug(f'Sending display text to target channel. {target}')
        message = await self.display_to_message(target)
        emoji_bar = await self.get_emoji_bar()
        from constants import id_wiihacky
        wiihacky = self.bot.get_user(id_wiihacky)

        # Define user check
        def user_check(_reaction, _user):
            # Conditions for true
            # reaction must be in reaction bar
            log.debug(f'user_check fired {_reaction}{_user}')
            if _user == wiihacky:
                log.debug(f'Bot made reaction')
                return False
            if _reaction.emoji in emoji_bar:
                log.debug(f'valid emoji {_reaction}|{emoji_bar}')
                # Validate user
                if self._restrict_to_user is not None and \
                        self._restrict_to_user == _user:
                    log.debug(
                        f'validated correct user '
                        f'{self._restrict_to_user}|{_user}')
                    return True
                else:
                    log.debug(f'No user restriction set')
                    return True
            log.debug(f'no valid true conditions found.')
            return False

        def user_check2(_reaction, _user):
            return True

        # Main interactivity loop
        while True:
            try:
                # Wait for a reaction
                log.debug(f'Waiting for reaction. {self._timeout}')
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=user_check, timeout=self._timeout)
                log.debug(f'Reaction received: {reaction}|{user}')
            except asyncio.TimeoutError as e:
                log.debug(f'Timed out waiting for reaction.')
                # Kill the message if clear on exit
                if self._clear_on_exit:
                    return await message.delete()
                else:
                    return await message.clear_reactions()

            # Handle Reaction
            if str(reaction.emoji) == self.EMOJI_STOP:
                log.debug("Got stop reaction")
                return await message.delete()

            if str(reaction.emoji) == self.EMOJI_EJECT:
                log.debug("got eject reaction")
                return await message.clear_reactions()

            # Paging reactions here.
            if reaction.emoji in self.EMOJI_PAGE_CONTROLS:
                log.debug(f'page reaction {reaction.emoji}')
                await self.page_control(
                    self.EMOJI_PAGE_CONTROLS.index(reaction.emoji))

            # Selection Reactions here
            if reaction.emoji in self.EMOJI_NUMBERS:
                self.result = self.EMOJI_NUMBERS.index(reaction.emoji)
                comment = (await self.display_page_items)[self.result]
                await self.display_selection(comment, message)

            # refresh display:
            message = await self.display_to_message(message)

    async def display_selection(
            self, cmt: praw.reddit.models.Comment, msg: discord.Message):

        def user_check(_reaction, _user):
            # Conditions for true
            # reaction must be in reaction bar
            log.debug(f'user_check fired {_reaction}{_user}')
            from constants import id_wiihacky
            wiihacky = self.bot.get_user(id_wiihacky)
            if _user == wiihacky:
                log.debug(f'Bot made reaction')
                return False
            if _reaction.emoji in [self.EMOJI_STOP, self.EMOJI_EJECT]:
                log.debug(
                    f'valid emoji {_reaction}|'
                    f'{[self.EMOJI_STOP, self.EMOJI_EJECT]}')
                # Validate user
                if self._restrict_to_user is not None and \
                        self._restrict_to_user == _user:
                    log.debug(
                        f'validated correct user '
                        f'{self._restrict_to_user}|{_user}')
                    return True
                else:
                    log.debug(f'No user restriction set')
                    return True
            log.debug(f'no valid true conditions found.')
            return False

        while True:
            await msg.clear_reactions()
            await msg.edit(content="```"+cmt.body+"```")

            await msg.add_reaction([self.EMOJI_STOP, self.EMOJI_EJECT])
            try:
                # Wait for a reaction
                log.debug(f'Waiting for reaction. {self._timeout}')
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=user_check, timeout=self._timeout)
                log.debug(f'Reaction received: {reaction}|{user}')
            except asyncio.TimeoutError as e:
                log.debug(f'Timed out waiting for reaction.')
                # Kill the message if clear on exit
                if self._clear_on_exit:
                    return await msg.delete()
                else:
                    return await msg.clear_reactions()
            if str(reaction.emoji) == self.EMOJI_STOP:
                log.debug("Got stop reaction")
                return await msg.delete()

            if str(reaction.emoji) == self.EMOJI_EJECT:
                log.debug("got eject reaction")
                return await msg.clear_reactions()


def setup(bot: disextc.Bot) -> None:
    """ Loads discord cog. """
    bot.add_cog(Laboratory(bot))
