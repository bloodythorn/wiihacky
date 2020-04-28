import constants as const
import discord as dis
import discord.ext.commands as dec
import logging as lg

import discord_interactive as di

import cogs.config

# TODO: Move to text constants.
txt_discord = 'discord'
txt_token = 'token'
txt_login_giveup = [
    """Okay, gonna give up trying to login to discord.""",
    """But that means I'll have to shut it down...""",
]
# TODO: Hardcode in : Original Bot ID, Developer ID, original discord ID


# TODO: Testing functions:
@dec.is_owner()
@dec.command()
async def test1(ctx: dec.Context, *args):
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))


@dec.is_owner()
@dec.command()
async def test2(ctx: dec.Context, *args):
    # Define each page
    root = di.Page('Welcome !\n')
    page_1 = di.Page('This is page 1')
    page_2 = di.Page('This is page 2')

    # Link pages together
    page_1.link(page_2, description='Click this icon to access page 2')
    root.link(page_1, description='Click this icon to access page 1')

    # Set the root page as the root of other page (so user can come back
    # with a specific reaction)
    root.root_of([page_1, page_2])

    # Create the Help object
    h = di.Help(ctx.bot, root)
    # And display the help !
    await h.display(ctx.author)


class Wiihacky(dec.Bot):
    """ The core of the bot.

    This is the main body of the bot. All coordination as well as
    initialization and shutdown take place here.

    """

    def __init__(self):
        """ Initialize the bot.

        All pre-async initialization needs to be done here.

        """
        # Logging
        # TODO: lg.INFO needs to be a variable.
        lg.basicConfig(format=const.LOG_FORMAT_STRING, level=lg.INFO)
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.setLevel(lg.DEBUG)
        self.log.info('Logger initialized.')

        # TODO: default prefix needs to be defined somewhere else.
        #   Maybe handled by config?
        super().__init__(command_prefix='/', fetch_offline_members=True)

        # initialize config cog
        # TODO: Filename from argument with full path?
        # NOTE: Since the config involves attaching a cog, super needs to be
        # initted before any inits that perform Bot duties
        self._init_config()
        self.log.info('Config file loaded and initialized.')

        # TODO: Add the system Cog
        # TODO: Bot.description : maybe after DB hookup?
        # TODO : reddit init
        # TODO: Persistent Memory
        # TODO: Personality
        # TODO: Discogs?!?

        # FIXME: Command testing
        self.add_command(test1)
        self.add_command(test2)
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

        # TODO: I need an on_ready listener to initialize other setup routines
        #   as well as output a 'I'm up' message. Some of these can be done
        #   when the cogs are added.

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
            from cogs.personality import txt_negative, txt_positive
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


if __name__ == '__main__':
    wh = Wiihacky()
    wh.run()
