import discord.ext.commands as disextc
import logging as lg
import typing as typ

import cogs

log = lg.getLogger(__name__)


class Security(disextc.Cog):

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot
        self._filters = dict()
        self._whitelist = list()

    @disextc.group(name='sec', hidden=True)
    @disextc.is_owner()
    async def security_group(self, ctx: disextc.Context):
        """Security group."""
        if ctx.invoked_subcommand is None:
            # TODO: Make invoking this with no sub give security status.
            #   Filters
            #   Whitelist
            #   watchdogs
            #   filer stats?
            await ctx.send(f'No sub command given for sec.')

    # Alerts

    @security_group.group(name='alt', hidden=True)
    @disextc.is_owner()
    async def alerts_group(self, ctx: disextc.Context):
        """Alerts Group"""
        if ctx.invoked_subcommand is None:
            # TODO: List Alerts when you get here.
            await ctx.send(f'No sub command given for alt.')

    # Filters

    @security_group.group(name='flt', hidden=True)
    @disextc.is_owner()
    async def filters_group(self, ctx: disextc.Context) -> None:
        """Filters Group, no subcommand lists configured filters."""
        if ctx.invoked_subcommand is None:
            if len(self._filters) == 0:
                await ctx.send(f'No filters configured.')
                return
            out_txt = 'filters:\n```'
            for idx, flt in enumerate(self._filters.values()):
                out_txt += str(idx) + ":" + repr(flt) + '\n'
            out_txt += '```'
            await ctx.send(out_txt)

    @filters_group.command(name='new', hidden=True)
    @disextc.is_owner()
    async def new_filter_command(
            self, ctx: disextc.Context,
            filter_name: str,
            category: str = '',
            expression: str = '',
            action: str = ''
    ) -> None:
        """Creates a new, blank filter with the name given."""
        # Test Name
        if len(filter_name) < 3:
            raise disextc.BadArgument(
                f"Too few characters.")
        if not filter_name.isalnum():
            raise disextc.BadArgument(
                f"Alpha numerics only, please.")
        if filter_name in self._filters.keys():
            raise disextc.BadArgument(
                f"A filter with the name '{filter_name}' already exits")

        # Create new entry
        text_filter = dict()
        text_filter['filter_name'] = filter_name
        text_filter['category'] = category
        text_filter['expression'] = expression
        text_filter['action'] = action
        text_filter['enabled'] = False  # All filters start disabled.

        # Put filter in memory.
        self._filters[filter_name] = text_filter
        # Notify user.
        await ctx.send(f"Saved filter: ```{text_filter}```")
        await ctx.send(
            f"Please make sure you thoroughly test it before enabling it.")

    @filters_group.command(name='del', hidden=True)
    @disextc.is_owner()
    async def delete_filter_command(
            self, ctx: disextc.Context, filter_name: str) -> None:
        """Removes filter permanently. Reloading will reload last save state."""
        # Confirm
        if filter_name not in self._filters:
            raise disextc.BadArgument(
                f"Filter '{filter_name}' does not exist.")
        message = await ctx.send(
            f'Please confirm that you would like to delete the following'
            f' filter:\n```{self._filters[filter_name]}```')

        result = await cogs.discord.Synergii.yes_no_prompt(
            ctx.bot, message, ctx.message.author)
        # Remove
        if result:
            self._filters.pop(filter_name)
            await ctx.send(f"Filter '{filter_name}' deleted")
        else:
            await message.edit(content='Canceled.')

    @filters_group.command(name='exp', hidden=True)
    @disextc.is_owner()
    async def replace_expression_command(
            self, ctx: disextc.Context, filter_name: str, exp: str) -> None:
        """Replaces expression for filter."""
        # expression -> regex to detect
        #  Filters take a regex expression like the auto-moderator
        # Disable Filter
        # Change regex
        # notify user
        pass

    @filters_group.command(name='cat', hidden=True)
    @disextc.is_owner()
    async def replace_category_command(
            self, ctx: disextc.Context,
            filter_name: str,
            *, categories: str
    ) -> None:
        """Replaces category for filter."""
        # category -> comment / submission / message / all
        #  Filters distinguish between effecting Posts, Comments, or discord
        #   messages (or all)
        # Disable Filter
        # change categories
        # notify user
        await ctx.send(categories + "|" + filter_name)

    async def replace_categories(
            self,
            filter_name: str,
            cats: typ.Optional[typ.Union[str, typ.List[str]]]):
        """sets filter to categories given."""
        if filter_name not in self._filters.keys():
            raise disextc.BadArgument(
                f"'{filter_name}' not found in filter list.")

        # validate categories
        # set them in the dict

    @filters_group.command(name='act', hidden=True)
    @disextc.is_owner()
    async def replace_action_command(self, ctx: disextc.Context) -> None:
        """Replaces action for filter."""
        # action -> remove / alert
        #  filers should have actions, remove, report, etc.
        # Disable filter
        # change action
        # notify user

    @filters_group.command(name='ena', hidden=True)
    @disextc.is_owner()
    async def enable_disable_filter(self, ctx: disextc.Context) -> None:
        """Enables or disables filter."""
        # TODO: Figger out a way to enable/disable all.
        pass

    @filters_group.group(name='wht', hidden=True)
    @disextc.is_owner()
    async def whitelist_group(self, ctx: disextc.Context) -> None:
        """Group for filter whitelist commands"""
        # TODO: Make this list whitelisted items with no params.
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No subcommand given for wht.')

    @whitelist_group.command(name='add', hidden=True)
    @disextc.is_owner()
    async def add_whitelisted_item_command(self, ctx: disextc.Context):
        """Adds item to whitelist."""
        pass

    @whitelist_group.command(name='rem', hidden=True)
    @disextc.is_owner()
    async def remove_whitelisted_item_command(self, ctx: disextc.Context):
        """Removes item from whitelist."""
        pass

    @filters_group.command(name='tst', hidden=True)
    @disextc.is_owner()
    async def test_string_command(self, ctx: disextc.Context):
        """This command tells if a string triggers a certain filter."""
        pass

    @filters_group.command(name='sav', hidden=True)
    @disextc.is_owner()
    async def save_filters_command(self, ctx: disextc.Context):
        """Saves filters to Redis so they are reloaded on reboot."""
        pass

    @filters_group.command(name='lod', hidden=True)
    @disextc.is_owner()
    async def load_filters_command(self, ctx: disextc.Context):
        """Loads filters from redis."""
        pass

    # Reports

    @security_group.group(name='rep', hidden=True)
    @disextc.is_owner()
    async def reports_group(self, ctx: disextc.Context):
        """Filters Group"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No sub command given for alt.')

    # Watchdog

    @security_group.group(name='wdg', hidden=True)
    @disextc.is_owner()
    async def watchdog_group(self, ctx: disextc.Context):
        """Watchdog Group"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No sub command given for alt.')


def setup(bot: disextc.Bot) -> None:
    """ Loads config cog. """
    bot.add_cog(Security(bot))
