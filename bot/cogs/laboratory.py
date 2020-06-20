import discord.ext.commands as disextc
import logging as lg
import nltk
import numpy as np
import praw
import re
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
            time = await self.train_all()
            await ctx.send(f'training finished in {time} seconds.')

    @lab_group.command(name='thk', hidden=True)
    @disextc.is_owner()
    async def think_command(self, ctx: disextc.Context, text_id: str):
        if self._synapse_0 is None or self._synapse_1 is None:
            raise disextc.CommandError(f"I have no mind.")
        results = await self.think(text_id=text_id)
        await ctx.send(f'think results: ```{results}```')

    # Helpers

    async def add_data(self, text_id: str, cat: typ.Optional[str]):
        # Adding data requires retrain
        if await self.trained:
            await self.blank_mind()

        # make sure the comment exists,
        # if this throws, nothing gets done.
        text = await self.get_text(text_id)

        # add id?
        if text_id not in self._ids:
            self._ids.append(text_id)

        # Category
        if cat is not None:
            # add category?
            if cat not in self._cats:
                self._cats[cat] = list()
            # make sure id is recorded under the category.
            if text_id not in self._cats[cat]:
                self._cats[cat].append(text_id)

        # Save words
        self._text_words[text_id] = list(sorted(
            await self.process_text(text)))

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

    async def bow_all(self):
        log.debug(f'bow_all fired')

        # Go through each training example
        self._training_data.clear()
        for txt_id in self._ids:
            # In Data
            in_ba = await self.bow(
                self._text_words[txt_id], await self.word_bag)
            # Out Data
            id_cats = []
            cats = await self.categories
            for cat in cats:
                if txt_id in self._cats[cat]:
                    id_cats.append(cat)
            out_ba = await self.bow(id_cats, cats)
            self._training_data.append((in_ba, out_ba))

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
        text = await self.get_text(text_id)
        if text is None:
            return None
        text_words = await self.process_text(text)
        l0 = await self.bow(text_words, await self.word_bag)
        l1 = await self.sigmoid(np.dot(l0, self._synapse_0))
        l2 = await self.sigmoid(np.dot(l1, self._synapse_1))
        return l2

    # todo: most likely.
    async def train_all(self):
        # Prep all in-out data
        await self.bow_all()
        for train_set in self._training_data:
            await self.train(
                np.array(train_set[0]),
                np.array(train_set[1]))

    async def train(
            self, X, y,
            hidden_neurons=10,
            alpha=1,
            epochs=50000,
            drop_out=False,
            drop_out_percent=0.5):
        np.random.seed(1)
        last_mean_error = 1

        # Random Init weights
        self._synapse_0 = 2*np.random.random(
            (1, hidden_neurons)) - 1
        self._synapse_1 = 2*np.random.random(
            (hidden_neurons, len(self._cats.keys()))) - 1
        prev_synapse_0_weight_update = np.zeros_like(self._synapse_0)
        prev_synapse_1_weight_update = np.zeros_like(self._synapse_1)
        synapse_0_direction_count = np.zeros_like(self._synapse_0)
        synapse_1_direction_count = np.zeros_like(self._synapse_1)

        for j in iter(range(epochs + 1)):
            # Feed forward through layers 0, 1, and 2
            layer_0 = X
            layer_1 = await self.sigmoid(np.dot(layer_0, self._synapse_0))

            if drop_out:
                layer_1 *= \
                    np.random.binomial([np.ones((len(X), hidden_neurons))],
                    1 - drop_out_percent)[0] * (
                            1.0 / (1 - drop_out_percent))
            layer_2 = await self.sigmoid(np.dot(layer_1, self._synapse_1))

            # how much did we miss the target value?
            layer_2_error = y - layer_2

            if (j % 10000) == 0 and j > 5000:
                # if this 10k iteration's error is greater than the last
                # iteration, break out
                if np.mean(np.abs(layer_2_error)) < last_mean_error:
                    last_mean_error = np.mean(np.abs(layer_2_error))
                else:
                    break

            # in what direction is the target value?
            # were we really sure? if so, don't change too much.
            layer_2_delta = \
                layer_2_error * \
                (await self.sigmoid_output_to_derivative(layer_2))

            # how much did each l1 value contribute to the l2 error
            # (according to the weights)?
            layer_1_error = layer_2_delta.dot(self._synapse_1.T)

            # in what direction is the target l1?
            # were we really sure? if so, don't change too much.
            layer_1_delta = \
                layer_1_error * await self.sigmoid_output_to_derivative(layer_1)

            synapse_1_weight_update = (layer_1.T.dot(layer_2_delta))
            synapse_0_weight_update = (layer_0.T.dot(layer_1_delta))

            if j > 0:
                synapse_0_direction_count += np.abs(
                    ((synapse_0_weight_update > 0) + 0) - (
                                (prev_synapse_0_weight_update > 0) + 0))
            synapse_1_direction_count += np.abs(
                ((synapse_1_weight_update > 0) + 0) - (
                            (prev_synapse_1_weight_update > 0) + 0))

            self._synapse_1 += alpha * synapse_1_weight_update
            self._synapse_0 += alpha * synapse_0_weight_update

            prev_synapse_0_weight_update = synapse_0_weight_update
            prev_synapse_1_weight_update = synapse_1_weight_update

    @staticmethod
    async def sigmoid(x):
        return 1/(1+np.exp(-x))

    @staticmethod
    async def sigmoid_output_to_derivative(output):
        return output*(1-output)


def setup(bot: disextc.Bot) -> None:
    """ Loads discord cog. """
    bot.add_cog(Laboratory(bot))
