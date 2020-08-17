import discord
import discord.ext.commands as disextc
import logging as lg
import typing as typ

import bot.constants as constants
import bot.decorators as decorators

log = lg.getLogger(__name__)


class UserAliases(disextc.Cog):
    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

    async def invoke(
            self,
            ctx: disextc.Context,
            cmd_name: str,
            *args, **kwargs
    ) -> None:
        """Invokes a command with args and kwargs."""
        log.debug(f"{cmd_name} was invoked through an alias")
        cmd = self.bot.get_command(cmd_name)
        if not cmd:
            return log.info(f'Did not find command "{cmd_name}" to invoke.')
        elif not await cmd.can_run(ctx):
            return log.info(
                f'{str(ctx.author)} tried to run the command "{cmd_name}"'
                f' but lacks permission.')

        await ctx.invoke(cmd, *args, **kwargs)

    @disextc.command(name='register')
    @decorators.without_role([constants.reddit_user_role_id])
    async def register_reddit_alias(
            self, ctx: disextc.Context, reddit_name: str) -> None:
        """ Register your Reddit account with r/WiiHacks Discord guild."""
        await self.invoke(ctx, "reg register", reddit_name)

    @disextc.command(name='karma')
    @decorators.with_roles([constants.reddit_user_role_id])
    async def karma_alias(
            self,
            ctx: disextc.Context,
            *, user: typ.Optional[discord.Member]):
        """ Returns given user's karma or the executor's karma. """
        if user is None:
            await self.invoke(ctx, "reg karma", user=ctx.author)
        else:
            await self.invoke(ctx, "reg karma", user=user)

    @disextc.command(name='lastseen', aliases=('last', 'ls'))
    @decorators.with_roles([constants.reddit_user_role_id])
    async def last_seen_alias(
            self, ctx: disextc.Context, *, user: discord.Member) -> None:
        """ Will retrieve when user was last seen. """
        await self.invoke(ctx, "reg last", user=user)


def setup(bot: disextc.Bot) -> None:
    """ Loads register cog. """
    bot.add_cog(UserAliases(bot))
