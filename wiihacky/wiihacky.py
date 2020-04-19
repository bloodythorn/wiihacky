"""WiiHacky Module."""

import actions
import asyncio
import constants
import discord
import logging as lg

# TODO: Uhhh, this. These are 'defaults' and should be in .config
bloody_id = 574629343142346757
def_log_level_all = lg.INFO
def_log_level_wh = lg.DEBUG
def_discord_out_level = lg.INFO
def_reddit_out_level = lg.CRITICAL
log_config_load_failed = 'failed to load config: {}'
bot_cli_channel = ('WiiHacks', 'bot_cli')
subreddit_relay = 'WiiHacks'
reddit_update_frequency = 5


# TODO: This function should also be moved to .config.
def load_config():
    """Get Configuration.

    This function will retrieve the configuration dict from yaml file.

    Returns
    -------
    A dictionary containing all configuration options.

    """
    import os
    file_np = os.getcwd() + '/' + constants.FILE_DEFAULT_CONFIG
    with open(file_np, 'r') as config_file:
        import yaml as yl
        return yl.safe_load(config_file)


class WiiHacky(discord.Client):
    """WiiHacky's direct interface."""

    def _init_config(self):
        """
        Initializes WiiHacky's Config

        This function initializes and attaches the module that regulates the
        configuration of wiihacky.

        :return: None
        """
        # TODO: Replace with config module.
        self.config = None
        try:
            self.config = load_config()
        except Exception as e:
            self.log.critical(log_config_load_failed.format(e))
            exit(-1)
        # from .config import Config
        # self.config = Config()

    def _init_logger(self, lvl_all=lg.INFO, lvl_wh=lg.INFO):
        """
        Attaches logging facilities and sets levels.

        :param lvl_all: This sets the global level. Discord.py and praw will be
            effected.
        :param lvl_wh:  This sets the logging level for WiiHacky only.
        :return: None
        """
        # FIXME: Instead of passing this(lvl),
        #  it should draw from default config
        lg.basicConfig(level=lvl_all, format=constants.LOG_FORMAT_STRING)
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.level = lvl_wh

    def _init_reddit(self):
        """
        Initializes Reddit.

        This function attaches the reddit submodule, and logs it in as the
        configured user.

        :return: None
        """
        import praw as pr
        self.reddit = pr.Reddit(
            user_agent=self.config['reddit']['user_agent'],
            client_id=self.config['reddit']['client_id'],
            client_secret=self.config['reddit']['client_secret'],
            username=self.config['reddit']['username'],
            password=self.config['reddit']['password'])

    def _init_discord(self):
        """
        Initialize Discord.py

        This function initializes discord.py as well as registering reddit
        update functions since I haven't learned the nuances of discord.py's
        interactive loop, I will just utilize custom loops for anything I need
        done periodically.

        :return: None
        """
        # register reddit update routine.
        self.loop.create_task(self.update_bot_state())

    async def send_txt_to_discord_channel(self, guild, channel, text):
        ch = discord.utils.get(
            self.get_all_channels(),
            guild__name=guild,
            name=channel)
        await ch.send(text)

    async def send_to_log(self, msg: str, lvl=lg.DEBUG):
        """
        Outputs a log message.

        Sends to the logging facilities to be printed in all manners
        demanded. The default level is debug, for quicker coding.

        Sending to logging is determined by the log level.
        Sending to discord has to be checked against a setting.
        Sending to reddit also has to be checked against a setting but should
            never be set beyond critical, as you don't want to spam reddit
            log messages.

        :param msg: The message to be output.
        :param lvl: The log level the message is intended for.
        :return: None
        """
        self.log.log(lvl, msg)
        # Check for discord output
        if lvl >= def_discord_out_level:
            await self.send_txt_to_discord_channel(
                bot_cli_channel[0],
                bot_cli_channel[1],
                msg)
        if lvl >= def_reddit_out_level:
            self.log.debug("TODO: Implement me.")

    def __init__(self):
        """
        Initialize WiiHacky

        Any initialization routine that fails will be a critical error as
        the bot cannot run without all of them.
        """
        # super init
        super().__init__()

        # init logger
        # FIXME: I currently have this first as everything else uses it.
        #   I really want what it is initially set to rely on the config
        #   so it should go first. Figger it oot.
        self._init_logger(def_log_level_all, def_log_level_wh)
        self.log.info(constants.TXT_LOGGER_SUCC)

        # init config
        self._init_config()
        self.log.info(constants.TXT_CONFIG_LOADED)

        # init reddit
        self._init_reddit()
        self.log.info(constants.TXT_REDDIT_SUCC)
        self.log.info(constants.TXT_LOGGED_IN, self.reddit.user.me())

        # init discord
        self._init_discord()
        self.log.info(constants.TXT_DISCORD_INIT)

        # Init the action factory.
        from actions import ActionFactory
        self.actions = ActionFactory(self.log)

        # set interactive
        self.running = False

    # Discord.py over-rides.

    # General Overrides

    async def on_connect(self):
        """
        Connect Message.

        Output to log only.
        """
        self.log.info('{} connected to Discord.'.format(self.user))

    async def on_disconnect(self):
        """
        Disconnect Message.

        Outputs to log only
        """
        self.log.info('{} disconnected from Discord.'.format(self.user))

    async def on_ready(self):
        """
        Discord Ready Message

        Output to both console and discord logs.
        """
        # TODO: this should be moved to
        #  wiihacky.actions.wiihacky.version(discord=true)
        output1 = \
            '{} is ready, version {}. Praw version {}. Discord.py version {}.'
        output2 = \
            'Discord User: {} | Reddit User: {}'
        import praw
        output1 = output1.format(
            self.user,
            constants.__version__,
            praw.__version__,
            discord.__version__)
        output2 = output2.format(
            self.user.name + '#' + self.user.discriminator,
            'u/' + self.reddit.user.me().name)
        await self.send_to_log(output1, lg.INFO)
        await self.send_to_log(output2, lg.INFO)

    # FIXME: The default error handler was better than the one I wrote.
    # async def on_error(self, event, *args, **kwargs):

    async def on_typing(self, channel, user, when):
        self.log.debug('typing: {} {} {}'.format(channel, user, when))

    async def on_webhooks_update(self, channel):
        self.log.debug('webhooks_update: {}'.format(channel))

    async def on_user_update(self, before, after):
        self.log.debug('user_update: {} {}'.format(before, after))

    async def on_voice_state_update(self, member, before, after):
        self.log.debug('voice_state_update: {} {} {}'.format(
            member, before, after))

    async def on_invite_create(self, invite):
        self.log.debug('invite_create: {}'.format(invite))

    async def on_invite_delete(self, invite):
        self.log.debug('invite_delete: {}'.format(invite))

    async def on_group_join(self, channel, user):
        self.log.debug('group_join: {} {}'.format(channel, user))

    async def on_group_remove(self, channel, user):
        self.log.debug('group_remove: {} {}'.format(channel, user))

    async def on_relationship_add(self, relationship):
        self.log.debug('relationship_add: {}'.format(relationship))

    async def on_relationship_update(self, before, after):
        self.log.debug('relationship_update: {} {}'.format(before, after))

    # Messaging

    async def on_message(self, message: discord.message.Message):
        # Echo Protection
        # Only messages of the bot that the bot would need to respond to.
        # This probably won't be used for anything but echo protection.
        if message.author == self.user:
            return

        # TODO: These conditions and even the echo protection above should be
        #   moved to their respective classes/modules.
        # There are only three classes of messages we respond to.
        # Anything with @WiiHacky in it, first priority
        # if message.content.find(str(self.user.id)) != -1 and \
        #   message.author.id == bloody_id:
        #    self.log.debug('Respond to @Mentions {}'.format(message))
        #    # By then end of this if, there should be nothing left to do.
        #    return

        # Anything that is a registered alias, second priority
        # TODO : Command char should eventually be a property of the aliases.
        # temp_command_char = '!'
        # if message.content[0:1] == temp_command_char and \
        #   message.author.id == bloody_id:
        #    self.log.debug('TODO:Respond to Alias {}'.format(message))
        #    # By then end of this if, there should be nothing left to do.
        #    return

        # Anything in the bot_cli channel, last priority.
        if message.guild.name == bot_cli_channel[0] and \
           message.channel.name == bot_cli_channel[1] and \
           message.author.id == bloody_id:
            self.log.debug('TODO:Respond to CLI Message {}'.format(message))
            try:
                ac: actions.Action = self.actions.parse_action(message.content)
                ac.execute()
            except Exception as e:
                self.log.error(e)
            # By then end of this if, there should be nothing left to do.
            return

        self.log.debug("on_message unhandled: {}".format(message))

    async def on_message_delete(self, message):
        self.log.debug('message_delete: {}'.format(message))

    async def on_bulk_message_delete(self, messages):
        self.log.debug('bulk_message_delete: {}'.format(messages))

    # FIXME
    # For some reason this function exceptions everytime I sent an embed
    # async def on_message_edit(self, message):
    #   pass

    # Reactions

    async def on_reaction_add(self, reaction, user):
        self.log.debug('reaction add: {} {}'.format(reaction, user))

    async def on_reaction_remove(self, reaction, user):
        self.log.debug('reaction remove: {} {}'.format(reaction, user))

    async def on_reaction_clear(self, reaction, user):
        self.log.debug('reaction clear: {} {}'.format(reaction, user))

    async def on_reaction_clear_emoji(self, reaction):
        self.log.debug('reaction clear emoji: {}'.format(reaction))

    # Private Channels

    async def on_private_channel_delete(self, channel):
        self.log.debug('private channel delete: {}'.format(channel))

    async def on_private_channel_create(self, channel):
        self.log.debug('private channel create: {}'.format(channel))

    async def on_private_channel_update(self, before, after):
        self.log.debug('private channel update: {} {}'.format(before, after))

    async def on_private_channel_pins_update(self, channel, last_pin):
        self.log.debug('private channel pins update: {} {}'.format(
            channel, last_pin))

    # Member

    async def on_member_join(self, member):
        self.log.debug('member_join: {}'.format(member))

    async def on_member_remove(self, member):
        self.log.debug('member_remove: {}'.format(member))

    async def on_member_update(self, before, after):
        self.log.debug('TODO: React to Member Update: {}->{}'.format(
            before, after))

    async def on_member_ban(self, guild, user):
        self.log.debug('member_ban: {} {}'.format(guild, user))

    async def on_member_unban(self, guild, user):
        self.log.debug('member_unban: {} {}'.format(guild, user))

    # Guild

    async def on_guild_channel_delete(self, channel):
        self.log.debug('guild_channel_delete: {}'.format(channel))

    async def on_guild_channel_create(self, channel):
        self.log.debug('guild_channel_create: {}'.format(channel))

    async def on_guild_channel_update(self, before, after):
        self.log.debug('guild_channel_update: {} {}'.format(before, after))

    async def on_guild_channel_pins_update(self, channel, last_pin):
        self.log.debug('guild_channel_pins_update: {} {}'.format(
            channel, last_pin))

    async def on_guild_integrations_update(self, guild):
        self.log.debug('guild_integrations_update: {}'.format(guild))

    async def on_guild_join(self, guild):
        self.log.debug('guild_join: {}'.format(guild))

    async def on_guild_remove(self, guild):
        self.log.debug('guild_remove: {}'.format(guild))

    async def on_guild_update(self, before, after):
        self.log.debug('guild_update: {} {}'.format(before, after))

    async def on_guild_role_create(self, role):
        self.log.debug('guild_role_create: {}'.format(role))

    async def on_guild_role_delete(self, role):
        self.log.debug('guild_role_delete: {}'.format(role))

    async def on_guild_role_update(self, before, after):
        self.log.debug('guild_role_update: {} {}'.format(before, after))

    async def on_guild_emojis_update(self, guild, before, after):
        self.log.debug('on_guild_emojis_update: {} {} {}'.format(
            guild, before, after))

    async def on_guild_available(self, guild):
        self.log.debug('guild_available: {} {}'.format(guild, self.guilds))

    async def on_guild_unavailable(self, guild):
        self.log.debug('guild_unavailable: {} {}'.format(guild, self.guilds))

    async def update_bot_state(self):
        await self.wait_until_ready()

        while not self.is_closed():
            try:
                # TODO; Period tasks/classes go here.
                await asyncio.sleep(reddit_update_frequency)
            except Exception as e:
                self.log.error(e)

    def start_daemon(self):
        self.log.info('Starting WiiHacky Daemon...')
        self.running = True
        self.run(self.config['discord']['token'])
        self.log.info('WiiHacky Daemon has shut down...')


if __name__ == "__main__":
    wh = WiiHacky()
    wh.start_daemon()
