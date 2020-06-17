import discord.ext.commands as disextc
import logging as lg
import typing as typ

log = lg.getLogger(__name__)


class ModAliases(disextc.Cog):
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

    @disextc.command(name="modstats", aliases=("mstats",))
    async def mod_stats_alias(
            self,
            ctx: disextc.Context,
            count: int = 500,
            key: bool = True
    ) -> None:
        """ Retrieve the stats for mod actions. """
        await self.invoke(
            ctx, "red mod stats", count=count, display_key=key)

    @disextc.command(name='reg_reset', aliases=("ureset",))
    async def reset_registration_alias(
            self, ctx: disextc.Context, user_id: int
    ) -> None:
        """ Reset user's verification. User ID required. """
        await self.invoke(ctx, "reg reset", user_id)


def setup(bot: disextc.Bot) -> None:
    """ Loads register cog. """
    bot.add_cog(ModAliases(bot))
