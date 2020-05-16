import discord as discord
import discord.ext.commands as disextc
import discord_interactive as disint
import praw
from constants import paginate, send_paginator

# TODO: Help System... needs to be more than default.


class MenuSys(disextc.Cog):
    """ This cog handles the interactive menuing system. """

    def __init__(self, bot: disextc.Bot):
        super().__init__()
        self.bot = bot

    # Listeners

    @disextc.Cog.listener(name='on_command_error')
    async def command_error(self, ctx: disextc.Context, error):
        """ Error Handler for commands. """
        import cogs.persona
        persona: cogs.persona.Persona = self.bot.get_cog('Persona')
        if persona is not None:
            pag = await paginate(
                f'{await persona.random_error}: ' +
                f'{ctx.message.content} -> {error}')
            await send_paginator(ctx, pag)

    # MenuSys Group Commands

    @disextc.group(name='men', hidden=True)
    @disextc.is_owner()
    async def menusys_grouping(self, ctx: disextc.Context):
        """ The Menusys cog grouping. """
        # TODO: Make this more graceful
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No menusys subcommand given.')

    # TODO:
    #   gj4d4z -> Picture Post
    #   gkh43r -> Self Post
    #   gjmvt8 -> Video Post
    @menusys_grouping.command(hidden=True)
    @disextc.is_owner()
    async def test_pag(self, ctx: disextc.Context):
        """ Test the pagination Command ."""
        from pagination import LinePaginator
        reddit: praw.Reddit = self.bot.get_cog('Reddit').reddit
        sub: praw.reddit.Submission = reddit.submission(id='gkh43r')
        embed = discord.Embed()
        embed.title = sub.title
        embed.url = sub.url
        embed.set_author(
            name=sub.author.name,
            url=f'https://www.reddit.com/u/{sub.author.name}')
        lines = []
        for line in sub.selftext.split('\n'):
            if line.strip() != '':
                max_size = 80

                def split_dis(a: str):
                    if len(a) < max_size:
                        return a, ''
                    else:
                        return a[max_size+1:], a[0:max_size]
                while len(line) > max_size:
                    line, split = split_dis(line)
                    lines.append(split.strip())
                lines.append(line.strip())
        await LinePaginator.paginate(
            lines, ctx, embed,
            max_size=1000,
            max_lines=20,
            restrict_to_user=ctx.author,
            footer_text='/r/WiiHacks/')

    @menusys_grouping.command(hidden=True)
    @disextc.is_owner()
    async def mmenu(self, ctx: disextc.Context) -> None:
        """ Invoke Main Menu.

        This currently holds a menu mock up that will eventually evolve into
        a real menu-ing system.
        """
        back = '⬅️'
        up = '⬆️'
        root_menu = disint.Page('Welcome to the r/WiiHacks Interactive Menu')
        wiihelp = disint.Page('Here is where the interactive help will be')
        reddit = disint.Page('Here you can do reddit searches or browse feeds')
        moderator = disint.Page('This is for reddit and discord moderation')
        admin = disint.Page('Bot administration Menu')
        rmod = disint.Page('Reddit Moderation Tools')
        dmod = disint.Page('Discord Moderation Tools')
        config = disint.Page('Config Cog -> Configuration options in the bot.')
        memory = disint.Page('Memory Cog -> Access bot memory')
        person = disint.Page('Personality Cog -> How the bot behaves')
        secure = disint.Page('Security Cog -> Bot security')
        system = disint.Page('System Cog -> Bot functions')
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
        help_menu = disint.Help(ctx.bot, root_menu)
        await help_menu.display(ctx.author)


# TODO: This will eventually need to be split off into its own module.
#   Currently it's not being used at all.
class CustomHelpCommand(disextc.HelpCommand):
    def __init__(self, **options):
        self.width = options.pop('width', 80)
        self.indent = options.pop('indent', 0)
        self.sort_commands = options.pop('sort_commands', True)
        self.dm_help = options.pop('dm_help', False)
        self.dm_help_threshold = options.pop('dm_help_threshold', 1000)
        self.commands_heading = options.pop('commands_heading', "Commands:")
        self.no_category = options.pop('no_category', 'No Category')
        self.paginator = options.pop('paginator', None)

        if self.paginator is None:
            self.paginator = disextc.Paginator()

        super().__init__(**options)

    def shorten_text(self, text):
        """Shortens text to fit into the :attr:`width`."""
        if len(text) > self.width:
            return text[:self.width - 3] + '...'
        return text

    def get_ending_note(self):
        """Returns help command's ending note.

        This is mainly useful to override for i18n purposes.
        """
        command_name = self.invoked_with
        txt = "Type {0}{1} command for more info on a command.\n" \
            "You can also type {0}{1} category for more info on a category."
        return txt.format(self.clean_prefix, command_name)

    def add_indented_commands(self, commands, *, heading, max_size=None):
        """Indents a list of commands after the specified heading.

        The formatting is added to the :attr:`paginator`.

        The default implementation is the command name indented by
        :attr:`indent` spaces, padded to ``max_size`` followed by
        the command's :attr:`Command.short_doc` and then shortened
        to fit into the :attr:`width`.

        Parameters
        -----------
        commands: Sequence[:class:`Command`]
            A list of commands to indent for output.
        heading: :class:`str`
            The heading to add to the output. This is only added
            if the list of commands is greater than 0.
        max_size: Optional[:class:`int`]
            The max size to use for the gap between indents.
            If unspecified, calls :meth:`get_max_size` on the
            commands parameter.
        """

        if not commands:
            return

        self.paginator.add_line(heading)
        max_size = max_size or self.get_max_size(commands)

        get_width = discord.utils._string_width
        for command in commands:
            name = command.name
            width = max_size - (get_width(name) - len(name))
            entry = '{0}{1:<{width}} {2}'.format(
                self.indent * ' ', name, command.short_doc, width=width)
            self.paginator.add_line(self.shorten_text(entry))

    async def send_pages(self):
        """A helper utility to send the page output from :attr:`paginator`
        to the destination."""
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(page)

    def add_command_formatting(self, command):
        """A utility function to format the non-indented block of commands and groups.

        Parameters
        ------------
        command: :class:`Command`
            The command to format.
        """

        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        self.paginator.add_line(signature, empty=True)

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    def get_destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        elif self.dm_help is None and len(self.paginator) > self.dm_help_threshold:
            return ctx.author
        else:
            return ctx.channel

    async def prepare_help_command(self, ctx, command=None):
        self.paginator.clear()
        await super().prepare_help_command(ctx, command)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            # <description> portion
            self.paginator.add_line(bot.description, empty=True)

        no_category = '\u200b{0.no_category}:'.format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name + ':' if cog is not None else no_category

        filtered = await self.filter_commands(
            bot.commands, sort=True, key=get_category)
        max_size = self.get_max_size(filtered)
        import itertools
        to_iterate = itertools.groupby(filtered, key=get_category)

        # Now we can add the commands to the page.
        for category, commands in to_iterate:
            commands = sorted(
                commands, key=lambda c: c.name) \
                if self.sort_commands else list(commands)
            self.add_indented_commands(
                commands, heading=category, max_size=max_size)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages()

    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)

        if filtered:
            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

        await self.send_pages()

    async def send_cog_help(self, cog):
        if cog.description:
            self.paginator.add_line(cog.description, empty=True)

        filtered = await self.filter_commands(
            cog.get_commands(), sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()


def setup(bot: disextc.Bot) -> None:
    """ Loads menusys cog. """
    bot.add_cog(MenuSys(bot))