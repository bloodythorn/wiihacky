import bitarray
import discord.ext.commands as disextc
import logging as lg
import nltk
import numpy as np
import praw
import typing as typ

log = lg.getLogger(__name__)

lab_id = 706358720111837316

# !lab add fv1ogou 1
# !lab add fv25mdi 3


class Laboratory(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self._needs_training = True
        self._bows = dict()
        self._cats = dict()
        self._ids = list()
        self._text_words = dict()

    @property
    async def word_bag(self):
        output = []
        for b in self._text_words.values():
            for word in b:
                if word not in output:
                    output.append(word)
        return output

    @disextc.group(name='lab', hidden=True)
    @disextc.is_owner()
    async def lab_group(self, ctx: disextc.Context):
        """Group for testing commands/applications."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'```Current Word Bag:{repr(await self.word_bag)}\n'
                           f'Current Categories:{repr(self._cats)}\n'
                           f'Comment List:{self._ids}```')

    @lab_group.command(name='add', hidden=True)
    @disextc.is_owner()
    async def add_data_command(
            self, ctx: disextc.Context, text_id: str, cat: typ.Optional[str]):
        # Adding data requires retrain
        self._needs_training = True
        try:
            # make sure the comment exists, if this throws, nothing gets done.
            text = await self.get_text(text_id)

            # add id?
            if text_id not in self._ids:
                self._ids.append(text_id)

            # add category?
            if cat not in self._cats:
                self._cats[cat] = list()

            # make sure id is recorded under the category.
            if text_id not in self._cats[cat]:
                self._cats[cat].append(text_id)

            # Save bow
            self._text_words[text_id] = await self.process_text(text)

            await ctx.send(f'{text_id} was added to category {cat}.')
        except Exception as e:
            await ctx.send(f'Unable to save id: {text_id}|{e.args}')

    @lab_group.command(name='clr', hidden=True)
    @disextc.is_owner()
    async def clear_data_command(self, ctx: disextc.Context):
        await self.clear_data()
        await ctx.send('All training data has been cleared.')

    # TODO: Implement me
    @lab_group.command(name='trn', hidden=True)
    @disextc.is_owner()
    async def train_command(self, ctx: disextc.Context):
        def sigmoid(x):
            return 1/(1+np.exp(-x))

        def sigmoid_output_to_derivative(output):
            return output*(1-output)

        # Go through each training example
        for txt_id in self._ids:
            # TODO: For each training sample we need:
            #   A tuple (input_bitarray, output_bitarray)
            #   A list of them that is created from the data.
            #   input ba will be text_words vs word_bag
            #   output will be id is in cats[cat] vs cats.keys
            pass

    # TODO: Implement me
    @lab_group.command(name='ann', hidden=True)
    @disextc.is_owner()
    async def analyze_command(self, ctx: disextc.Context):
        if self._needs_training:
            await ctx.send(f"Sorry, we haven't trained yet.")

    # Helpers

    @staticmethod
    async def bow(words: typ.List[str], bag: typ.List[str]
                  ) -> (bitarray.bitarray, typ.Tuple[str]):
        bits = bitarray.bitarray(len(bag)).setall(False)
        key = []

        # Make key, tick present bits
        for idx, word in enumerate(bag):
            key.append(word)
            if word in words:
                bits[idx] = True

        return bits, tuple(key)

    async def clear_data(self):
        self._needs_training = True
        self._ids.clear()
        self._bows.clear()
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


def setup(bot: disextc.Bot) -> None:
    """ Loads discord cog. """
    bot.add_cog(Laboratory(bot))
