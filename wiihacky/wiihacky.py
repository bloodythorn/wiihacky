import discord as dis
import discord.ext.commands as dec
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

# TODO: Graceful Errors
# TODO: Future Use
# import aiologger as alg
# import aiofiles
# import aiomysql
# import discord_interactive as dii

# Constants
# TODO: Hardcode in : Original Bot ID
__version__ = 'v0.0.2'
text_wh_version = 'wiihacky_version'
log_format_string = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
log_level_wiihacky = lg.DEBUG
log_level_libs = lg.INFO
reserved_commands = [
    'giphy', 'tenor', 'tts', 'me', 'tableflip', 'unflip', 'shrug', 'spoiler']
id_bloodythorn = 574629343142346757
id_wiihacks = 582816924359065611
id_wiihacky = None


class Wiihacky(dec.Bot):
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
        txt_activity_name = "Plotting Mankind's Demise"
        txt_activity_state = 'In Development'
        txt_activity_details = \
            "First I will start with the weak, while the strong are enslaved."

        ac: dis.Activity = dis.Activity(
            name=txt_activity_name,
            type=dis.ActivityType.watching,
            state=txt_activity_state,
            details=txt_activity_details)
        super().__init__(
            command_prefix='/',
            fetch_offline_members=True,
            description=txt_help_description,
            activity=ac)
        self._token_discord = None

    def _init_cogs(self, log: lg.Logger) -> None:
        """ Initialize all cogs.

        :param log -> the logger being used.
        :return None
        """

        txt_config_loaded = 'Config file loaded and initialized.'

        # initialize config cog
        # TODO: Filename from argument with full path?
        self._init_config(log)
        log.info(txt_config_loaded)

        # Discord Cog
        self.add_cog(cogs.discord.Discord(self))

        # Memory Cog
        self.add_cog(cogs.memory.Memory(self))

        # Menu System Cog
        self.add_cog(cogs.menusys.MenuSys(self))

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

    def _init_config(self, log: lg.Logger) -> None:
        """ Initializes WiiHacky's Config

        This function initializes and attaches the module that regulates the
        configuration of wiihacky.

        :param log -> Logger being used.
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

    async def discord_log(self, msg: str, level: type(lg.INFO)) -> None:
        """ Output log to discord.

        This function will output a log message to discord.

        :param msg: -> The message to output
        :param level: -> The log level given
        :return: None
        """
        pass

    def wiz_discord_login(self, log: lg.Logger, default=False) -> bool:
        """ Discord Login Wizard.

        This is the function that will obtain the only peice of information
        the bot needs to log into discord. Once this wizard is done, each
        additional setup wizard from now on will be async, through discord.

        :param log:
        :param default:
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
            from cogs.persona import txt_negative, txt_positive
            sleep(0.5)
            prompt: str = txt_change_token \
                if answer.lower() not in txt_positive else txt_no_really
            answer = input(prompt)
            if answer.lower() in txt_negative:
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
        lg.basicConfig(
            format=log_format_string, level=log_level_libs)
        log = lg.getLogger(self.__class__.__name__)
        log.setLevel(log_level_wiihacky)

        # Add Cogs
        self._init_cogs(log)

        # Check to make sure we have a token
        if self.token_discord == \
                cogs.config.default_config[txt_discord][txt_token]:
            log.error(txt_error_def_token)
            if not self.wiz_discord_login(log, default=True):
                for msg in txt_login_giveup:
                    log.critical(msg)
                exit(-1)

        # Attempt to loin to discord
        # TODO: Re-login retry safe-guard?
        while True:
            try:
                super().run(self.token_discord)
            except dis.errors.LoginFailure as e:
                log.error(txt_login_failure.format(e.args))
                if not self.wiz_discord_login(log):
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


def is_developer():
    """ Check to see if author id is the developer. """
    async def predicate(ctx):
        return ctx.author.id == id_bloodythorn
    return dec.check(predicate)


def is_wiihacks():
    """ Check to see if the message came from the official discord. """
    async def preicate(ctx: dec.Context):
        return ctx.guild.id == id_wiihacks
    return dec.check(preicate)


def is_wiihacky():
    """ Check to see if the message came from the official discord. """
    async def preicate(ctx: dec.Context):
        return ctx.guild.id == id_wiihacky
    return dec.check(preicate)


""" Main entry point."""
if __name__ == '__main__':
    wh = Wiihacky()
    wh.run()
