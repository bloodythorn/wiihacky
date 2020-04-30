import discord.ext.commands as dec
import discord_interactive as dii


class MenuSys(dec.Cog):

    def __init__(self, bot: dec.Bot):
        super().__init__()
        self.bot = bot

    # TODO: MOve to menusys
    @dec.command()
    async def mmenu(self, ctx: dec.Context) -> None:
        """Invoke Main Menu.

        This currently holds a menu moch up that will eventually evolve into
        a real menu-ing system.
        """
        back = '⬅️'
        up = '⬆️'
        # TODO: Logging
        root_menu = dii.Page('Welcome to the r/WiiHacks Interactive Menu')
        wiihelp = dii.Page('Here is where the interactive help will be')
        reddit = dii.Page('Here you can do reddit searches or browse feeds')
        moderator = dii.Page('This is for reddit and discord moderation')
        admin = dii.Page('Bot administration Menu')
        rmod = dii.Page('Reddit Moderation Tools')
        dmod = dii.Page('Discord Moderation Tools')
        config = dii.Page('Config Cog -> Configuration options in the bot.')
        memory = dii.Page('Memory Cog -> Access bot memory')
        person = dii.Page('Personality Cog -> How the bot behaves')
        secure = dii.Page('Security Cog -> Bot security')
        system = dii.Page('System Cog -> Bot functions')
        root_menu.link(
            wiihelp, description='Help System', parent_reaction=back)
        root_menu.link(reddit, description='Reddit Menu', parent_reaction=back)
        root_menu.link(
            moderator, description='Moderator Menus', parent_reaction=back)
        root_menu.link(
            admin, description='Admin Menu *KEEP OUT*', parent_reaction=back)
        moderator.link(
            rmod, description='Reddit Moderation', parent_reaction=back)
        moderator.link(
            dmod, description='Discord Moderation', parent_reaction=back)
        admin.link(config, description='Config Cog', parent_reaction=back)
        admin.link(memory, description='Memory Cog', parent_reaction=back)
        admin.link(person, description='Personality Cog', parent_reaction=back)
        admin.link(secure, description='Security Cog', parent_reaction=back)
        admin.link(system, description='System Cog', parent_reaction=back)
        root_menu.root_of(wiihelp, root_reaction=up)
        root_menu.root_of(reddit, root_reaction=up)
        root_menu.root_of(moderator, root_reaction=up)
        root_menu.root_of(admin, root_reaction=up)
        root_menu.root_of(rmod, root_reaction=up)
        root_menu.root_of(dmod, root_reaction=up)
        root_menu.root_of(config, root_reaction=up)
        root_menu.root_of(memory, root_reaction=up)
        root_menu.root_of(person, root_reaction=up)
        root_menu.root_of(secure, root_reaction=up)
        help_menu = dii.Help(ctx.bot, root_menu)
        await help_menu.display(ctx.author)
