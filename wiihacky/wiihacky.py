import discord as discord
import discord.ext.commands as disext
import logging as lg
# Bot Modules
import cogs.config
import cogs.discord
import cogs.memory
import cogs.menusys
import cogs.persona
import cogs.reddit
import cogs.security
import cogs.system

txt_cogs_list = (
    cogs.config.Config.qualified_name,
    cogs.discord.Discord.qualified_name,
    cogs.memory.Memory.qualified_name,
    cogs.menusys.MenuSys.qualified_name,
    cogs.persona.Persona.qualified_name,
    cogs.reddit.Reddit.qualified_name,
    cogs.security.Security.qualified_name,)

# Module Constants
__version__ = 'v0.0.2'
text_wh_version = 'wiihacky_version'
id_bloodythorn = 574629343142346757
id_wiihacks = 582816924359065611
id_wiihacky = 630280409137283085
# TODO: Hardcode in : Original Bot ID
log_format_string = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
reserved_commands = [
    'giphy', 'tenor', 'tts', 'me', 'tableflip',
    'unflip', 'shrug', 'spoiler']
command_chars = ('/', '!', '?')
message_cache = 1000 * 2

# Logging
log_level_wiihacky = lg.DEBUG
log_level_libs = lg.INFO
lg.basicConfig(format=log_format_string, level=log_level_libs)
log = lg.getLogger(__name__)
log.setLevel(log_level_wiihacky)


class Wiihacky(disext.Bot):
    """ The core of the bot.

    This is the main body of the bot. All coordination as well as
    initialization and shutdown take place here. If the bot is not setup,
    all discord setup is done through console via prompts and input.

    Once discord is setup, the rest of the setup is interactive, through
    discord.

    """

    def __init__(self):
        """ Initialize the bot. """

        txt_help_description = \
            """r/WiiHacks Discord Help Menu"""
        txt_activity_name = "Mankind and Plotting its Demise"
        txt_activity_state = 'In Development'
        txt_activity_details = \
            "First I will start with the weak, while the strong are enslaved."

        ac: discord.Activity = discord.Activity(
            name=txt_activity_name,
            type=discord.ActivityType.watching,
            state=txt_activity_state,
            details=txt_activity_details)
        super().__init__(
            max_messages=message_cache,
            command_prefix=disext.when_mentioned_or(*command_chars),
            fetch_offline_members=True,
            description=txt_help_description,
            activity=ac)
        self._token_discord = None

    def _init_cogs(self) -> None:
        """ Initialize all cogs.

        :return None
        """

        txt_config_loaded = 'Config file loaded and initialized.'

        # initialize config cog
        # TODO: Filename from argument with full path?
        self._init_config()
        log.info(txt_config_loaded)

        # Discord Cog
        self.add_cog(cogs.discord.Discord(self))

        # Memory Cog
        self.add_cog(cogs.memory.Memory(self))

        # Menu System Cog
        menusys = cogs.menusys.MenuSys(self)
        self.add_cog(menusys)
        help_com = cogs.menusys.CustomHelpCommand()
        self.help_command = help_com
        help_com.cog = menusys

        # Persona Cog
        self.add_cog(cogs.persona.Persona(self))

        # Reddit Cog
        self.add_cog(cogs.reddit.Reddit(self))

        # Security Cog
        self.add_cog(cogs.security.Security(self))

        # System Cog
        self.add_cog(cogs.system.System(self))

        # TODO : reddit init
        # TODO: Discogs?!?

    def _init_config(self) -> None:
        """ Initializes WiiHacky's Config

        This function initializes and attaches the module that regulates the
        configuration of wiihacky.

        :return None
        """
        txt_failed_to_load = 'Failed to Load Config: {}'
        txt_config_check = 'Checking for config file {}.'
        txt_config_not_found = 'Config file not found in working directory: {}'
        txt_unknown_error = 'Unknown error while loading config: {}'
        cog_config = 'Config'

        try:
            self.add_cog(cogs.config.Config(self))
            config: cogs.config.Config = self.get_cog(cog_config)
            while config.data is None:
                try:
                    log.info(txt_config_check.format(config.file_name))
                    config.load()
                except FileNotFoundError:
                    import os
                    log.error(txt_config_not_found.format(os.getcwd()))
                    if not config.wiz_create_config():
                        exit(-1)
                except Exception as e:
                    log.error(txt_unknown_error.format(e.args))
                    exit(-1)
        except Exception as e:
            log.critical(txt_failed_to_load.format(str(e.args)))
            exit(-1)

    def wiz_discord_login(self, default=False) -> bool:
        """ Discord Login Wizard.

        This is the function that will obtain the only peice of information
        the bot needs to log into discord. Once this wizard is done, each
        additional setup wizard from now on will be async, through discord.

        :param default -> Was the default setting set?
        :return:
        """
        txt_start = """***-> Starting discord wizard..."""
        txt_default_value = \
            """Okay Einstein, default value is still in the config."""
        txt_why_not_work = """No idea why '{}' didn't work...*rolls eyes*"""
        txt_either_way = """Either way, it ain't gonna work."""
        txt_change_token = \
            """You want me to change it? If you can just paste it in.... """
        txt_no_really = """No... really, you can paste it here -> """
        txt_refuse = """Really? We can dump out then..."""
        txt_changed = \
            """Changed to the new value. Let's see if that works..."""
        cog_config = 'Config'
        txt_discord = 'discord'
        txt_token = 'token'

        def check_discord_token(t: str) -> bool:
            """ My check for the discord token.

            This is completely arbitrary as I've only seen one discord token
            and couldn't find any information on what sort of generator they
            use for the tokens to make a regex.
            """
            return len(t) > 50

        log.info(txt_start)
        if default:
            log.warning(txt_default_value)
        else:
            log.info(txt_why_not_work.format(self.token_discord))
        log.info(txt_either_way)
        answer = ''
        while True:
            # Make sure log buffer is clear:
            from time import sleep
            from cogs.persona import convert_to_bool as ctb
            sleep(0.5)
            prompt: str = txt_change_token if ctb(answer.lower()) \
                else txt_no_really
            answer = input(prompt)
            if not ctb(answer.lower()):
                log.critical(txt_refuse)
                return False
            else:
                # possible token
                if check_discord_token(answer):
                    config: cogs.config.Config = self.get_cog(cog_config)
                    config.data[txt_discord][txt_token] = answer
                    config.save()
                    log.info(txt_changed)
                    return True

    def run(self) -> None:
        """Start the wiihacky daemon.

        This will start the wiihacky daemon and run the underlying bot
        async loop. If it cannot connect to discord, it will execute the
        discord connection wizard until the operator can connect, or
        gives up.

        :return: None
        """
        txt_error_def_token = \
            """You still haven't changed the default discord token..."""
        txt_login_failure = "I couldn't log into discord... : {}"
        txt_login_giveup = [
            """Okay, gonna give up trying to login to discord.""",
            """But that means I'll have to shut it down..."""]
        txt_main_loop_term = 'The main loop has been terminated : {}'
        txt_discord = 'discord'
        txt_token = 'token'

        # TODO: Parse Arguments
        # Setup logging defaults

        # Add Cogs
        self._init_cogs()

        # Check to make sure we have a token
        if self.token_discord == \
                cogs.config.default_config[txt_discord][txt_token]:
            log.error(txt_error_def_token)
            if not self.wiz_discord_login(default=True):
                for msg in txt_login_giveup:
                    log.critical(msg)
                exit(-1)

        # Attempt to loin to discord
        # TODO: Re-login retry safe-guard?
        while True:
            try:
                super().run(self.token_discord)
            except discord.errors.LoginFailure as e:
                log.error(txt_login_failure.format(e.args))
                if not self.wiz_discord_login():
                    for msg in txt_login_giveup:
                        log.critical(msg)
                        from time import sleep
                        sleep(0.5)
                    exit(-1)
            except RuntimeError as e:
                log.info(txt_main_loop_term.format(e.args))
                exit(0)

    @property
    def token_discord(self) -> str:
        """ Discord Token.

        This token is read only. It will try to pull the file from the config
        but if it cannot, then it will pull it from the cached local copy.

        :return: A string containing the discord bot token.
        """
        txt_discord = 'discord'
        txt_token = 'token'
        cog_config = 'Config'

        config = self.get_cog(cog_config)
        if config is None:
            return self._token_discord
        if txt_discord in config.data \
                and txt_token in config.data[txt_discord]:
            self._token_discord = config.data[txt_discord][txt_token]
        return self._token_discord


@disext.check
async def is_developer():
    """ Check to see if author id is the developer. """
    async def predicate(ctx):
        return ctx.author.id == id_bloodythorn
    return disext.check(predicate)


@disext.check
async def is_wiihacks():
    """ Check to see if the message came from the official discord. """
    async def predicate(ctx: disext.Context):
        return ctx.guild.id == id_wiihacks
    return disext.check(predicate)


@disext.check
async def is_wiihacky():
    """ Check to see if the message came from the official bot. """
    async def predicate(ctx: disext.Context):
        return ctx.guild.id == id_wiihacky
    return disext.check(predicate)


async def paginate(
        message: str,
        pag: disext.Paginator = disext.Paginator()
        ) -> disext.Paginator:
    """ Helper to use the Paginator.

    TODO: Document
    """
    pag.add_line(message)
    return pag


async def send_paginator(ctx: disext.Context, pag: disext.Paginator):
    """ Helper to send a paginator.

    # TODO: Document
    """
    for page in pag.pages:
        await ctx.send(page)


""" Main entry point."""
if __name__ == '__main__':
    wh = Wiihacky()
    wh.run()
