import constants as const
import discord as dis
import discord.ext.commands as dec
import discord_interactive as dii
import logging as lg

import cogs.config
import cogs.discord
import cogs.memory
import cogs.persona
import cogs.reddit
import cogs.security
import cogs.system

# TODO: Move to text constants.
txt_discord = 'discord'
txt_token = 'token'
txt_login_giveup = [
    """Okay, gonna give up trying to login to discord.""",
    """But that means I'll have to shut it down...""",
]
# TODO: Hardcode in : Original Bot ID, Developer ID, original discord ID


class Wiihacky(dec.Bot):
    """ The core of the bot.

    This is the main body of the bot. All coordination as well as
    initialization and shutdown take place here.

    """

    def __init__(self):
        """ Initialize the bot.

        All pre-async initialization needs to be done here.

        """
        # Logging # TODO: lg.INFO needs to be a variable.
        lg.basicConfig(format=const.LOG_FORMAT_STRING, level=lg.INFO)
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.setLevel(lg.DEBUG)
        self.log.info('Logger initialized.')

        # Initialize the Bot class.
        # TODO: default prefix needs to be defined somewhere else.
        #   Maybe handled by config?
        # NOTE: Bot needs to be initialized before we before add cogs.
        super().__init__(command_prefix='/', fetch_offline_members=True)

        # Add Cogs
        self._init_cogs()

        # Add Interactive Menu Root
        self.add_command(menu)

        # Get discord started.
        self._token_discord = None

        if self.token_discord == \
                cogs.config.default_config[txt_discord][txt_token]:
            self.log.error(
                """You still haven't changed the default discord token...""")
            if not self.wiz_discord_login(default=True):
                for msg in txt_login_giveup:
                    self.log.critical(msg)
                exit(-1)

    def _init_cogs(self):
        # initialize config cog
        # TODO: Filename from argument with full path?
        self._init_config()
        self.log.info('Config file loaded and initialized.')

        # Discord Cog
        self.add_cog(cogs.discord.Discord())

        # Memory Cog
        self.add_cog(cogs.memory.Memory())

        # Persona Cog
        self.add_cog(cogs.persona.Persona())

        # Reddit Cog
        self.add_cog(cogs.reddit.Reddit())

        # Security Cog
        self.add_cog(cogs.security.Security())

        # System Cog
        self.add_cog(cogs.system.System())

        # TODO : reddit init
        # TODO: Discogs?!?

    def _init_config(self):
        """
        Initializes WiiHacky's Config

        This function initializes and attaches the module that regulates the
        configuration of wiihacky.

        :return: None
        """
        # TODO: argparser(config from arg)
        txt_failed_to_load = 'Failed to Load Config: {}'
        txt_config_check = 'Checking for config file {}.'
        txt_config_not_found = 'Config file not found in working directory: {}'
        txt_unknown_error = 'Unknown error while loading config: {}'
        try:
            self.add_cog(cogs.config.Config(self))
            config: cogs.config.Config = self.get_cog('Config')
            while config.data is None:
                try:
                    config.file_name = const.FILE_NAME_DEFAULT_CONFIG
                    self.log.info(txt_config_check.format(config.file_name))
                    config.load()
                except FileNotFoundError:
                    import os
                    self.log.error(txt_config_not_found.format(os.getcwd()))
                    if not config.wiz_create_config():
                        exit(-1)
                except Exception as e:
                    self.log.error(txt_unknown_error.format(e.args))
                    exit(-1)
        except Exception as e:
            self.log.critical(txt_failed_to_load.format(str(e.args)))
            exit(-1)

    def wiz_discord_login(self, default=False) -> bool:
        txt_start = \
            """***-> Starting discord wizard..."""
        txt_default_value = \
            """Okay Einstein, default value is still in the config."""
        txt_why_not_work = \
            """No idea why '{}' didn't work...*rolls eyes*"""
        txt_either_way = \
            """Either way, it ain't gonna work."""
        txt_change_token = \
            """You want me to change it? If you can just paste it in.... """
        txt_no_really = \
            """No... really, you can paste it here -> """
        txt_refuse = \
            """Really? We can dump out then..."""
        txt_changed = \
            """Changed to the new value. Let's see if that works..."""

        def check_discord_token(t):
            """ My check for the discord token.

            This is completely arbitrary as I've only seen one discord token
            and couldn't find any information on what sort of generator they
            use for the tokens.
            """
            return len(t) > 50

        self.log.info(txt_start)
        if default:
            self.log.warning(txt_default_value)
        else:
            self.log.info(txt_why_not_work.format(self.token_discord))
        self.log.info(txt_either_way)
        answer = ''
        while True:
            # Make sure log buffer is clear:
            from time import sleep
            from cogs.persona import txt_negative, txt_positive
            sleep(0.5)
            prompt: str = txt_change_token \
                if answer.lower() not in txt_positive else txt_no_really
            answer = input(prompt)
            if answer.lower() in txt_negative:
                self.log.critical(txt_refuse)
                return False
            else:
                # possible token
                if check_discord_token(answer):
                    config: cogs.config.Config = self.get_cog('Config')
                    config.data[txt_discord][txt_token] = answer
                    config.save()
                    self.log.info(txt_changed)
                    return True

    def run(self):
        """Start the wiihacky daemon.

        This will start the wiihacky daemon and run the underlying bot
        async loop. If it cannot connect to discord, it will execute the
        discord connection wizard until the operator can connect, or
        gives up.

        :return: None
        """
        while True:
            try:
                super().run(self.token_discord)
            except dis.errors.LoginFailure as e:
                self.log.error(f"I couldn't log into discord... : {e.args}")
                if not self.wiz_discord_login():
                    for msg in txt_login_giveup:
                        self.log.critical(msg)
                    exit(-1)
            except RuntimeError as e:
                self.log.info(
                    'The root loop has been terminated : {}'.format(e.args))
                exit(0)

    @property
    def token_discord(self):
        """ Discord Token.

        This token is read only.
        """
        config = self.get_cog('Config')
        if config is None:
            return self._token_discord
        if txt_discord in config.data \
                and txt_token in config.data[txt_discord]:
            self._token_discord = config.data[txt_discord][txt_token]
        return self._token_discord


@dec.command()
async def menu(ctx: dec.Context) -> None:
    """Invoke Main Menu.

    This function will invoke the main WiiHacks Menuing system.
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
    root_menu.link(wiihelp, description='Help System', parent_reaction=back)
    root_menu.link(reddit, description='Reddit Menu', parent_reaction=back)
    root_menu.link(moderator, description='Moderator Menus', parent_reaction=back)
    root_menu.link(admin, description='Admin Menu *KEEP OUT*', parent_reaction=back)
    moderator.link(rmod, description='Reddit Moderation', parent_reaction=back)
    moderator.link(dmod, description='Discord Moderation', parent_reaction=back)
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


if __name__ == '__main__':
    wh = Wiihacky()
    wh.run()
