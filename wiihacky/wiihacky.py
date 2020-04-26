"""WiiHacky Module."""

import asyncio
import constants
import discord
import logging as lg
# import mod_discord
import mod_multilog
# import mod_reddit
import config

# TODO: Uhhh, this. These are 'defaults' and should be in .config
bloody_id = 574629343142346757
log_config_load_failed = 'failed to load config: {}'
reddit_update_frequency = 5


class WiiHacky(discord.Client):
    """WiiHacky's direct interface."""

    def _init_config(self):
        """
        Initializes WiiHacky's Config

        This function initializes and attaches the module that regulates the
        configuration of wiihacky.

        :return: None
        """
        # TODO: New Config, Wizard, argparser(config from arg)
        self.config = None
        try:
            self.config = config.Config(constants.FILE_DEFAULT_CONFIG)
        except Exception as e:
            self.log.critical(log_config_load_failed.format(str(e)))
            exit(-1)

    def _init_logger(self):
        """
        Attaches logging facilities and sets levels.

        :return: None
        """
        # TODO: Move level defaults to config.
        lg.basicConfig(level=lg.INFO)
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.setLevel(lg.DEBUG)

    def _init_reddit(self):
        """
        Initializes Reddit.

        This function attaches the reddit submodule, and logs it in as the
        configured user.

        :return: None
        """
        import praw as pr
        self.reddit = pr.Reddit(
            user_agent=self.config.data['reddit']['user_agent'],
            client_id=self.config.data['reddit']['client_id'],
            client_secret=self.config.data['reddit']['client_secret'],
            username=self.config.data['reddit']['username'],
            password=self.config.data['reddit']['password'])
        # TODO: Register reddit event loop.

    def __init__(self):
        """
        Initialize WiiHacky

        Any initialization routine that fails will be a critical error as
        the bot cannot run without all of them.
        """
        # super init
        super().__init__()

        # init logger
        self._init_logger()
        self.log.info(constants.TXT_LOGGER_SUCC)

        # init config
        self._init_config()
        self.log.info(constants.TXT_CONFIG_LOADED)

        # init reddit
        self._init_reddit()
        self.log.info(constants.TXT_REDDIT_SUCC)

        # set interactive
        self.running = False

    # Discord.py over-rides.

    # General Overrides

    async def on_connect(self):
        """
        Connect Message.

        Output to log only, due to lack of mod_discord connectivity.
        """
        await mod_multilog.send_to_log(
            self.log, self,
            constants.TXT_DISCORD_CONNECT.format(self.user),
            lg.INFO)

    async def on_disconnect(self):
        """
        Disconnect Message.

        Output to log only, due to lack of mod_discord connectivity.
        """
        await mod_multilog.send_to_log(
            self.log, self,
            constants.TXT_DISCORD_DISCON.format(self.user), lg.INFO)

    async def on_ready(self):
        """
        Discord Ready Message

        Output to both console and mod_discord logs.
        """
        import praw
        await mod_multilog.send_to_log(
            self.log, self,
            constants.TXT_BOT_READY.format(
                self.user,
                constants.__version__,
                praw.__version__,
                discord.__version__),
            lg.INFO)
        await mod_multilog.send_to_log(
            self.log, self,
            constants.TXT_BOT_USERS.format(
                self.user.name + '#' + self.user.discriminator,
                'u/' + self.reddit.user.me().name),
            lg.INFO)

    # FIXME: The default error handler was better than the one I wrote.
    # async def on_error(self, event, *args, **kwargs):

    async def on_typing(self, channel, user, when):
        await mod_multilog.send_to_log(
            self.log, self,
            'React To Typing: {} {} {}'.format(channel, user, when),
            lg.DEBUG)

    async def on_webhooks_update(self, channel):
        await mod_multilog.send_to_log(
            self.log, self,
            'webhooks_update: {}'.format(channel),
            lg.DEBUG)

    async def on_user_update(self, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'user_update: {} {}'.format(before, after),
            lg.DEBUG)

    async def on_voice_state_update(self, member, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'voice_state_update: {} {} {}'.format(
                member, before, after),
            lg.DEBUG)

    async def on_invite_create(self, invite):
        await mod_multilog.send_to_log(
            self.log, self,
            'invite_create: {}'.format(invite),
            lg.DEBUG)

    async def on_invite_delete(self, invite):
        await mod_multilog.send_to_log(
            self.log, self,
            'invite_delete: {}'.format(invite),
            lg.DEBUG)

    async def on_group_join(self, channel, user):
        await mod_multilog.send_to_log(
            self.log, self,
            'group_join: {} {}'.format(channel, user),
            lg.DEBUG)

    async def on_group_remove(self, channel, user):
        await mod_multilog.send_to_log(
            self.log, self,
            'group_remove: {} {}'.format(channel, user),
            lg.DEBUG)

    async def on_relationship_add(self, relationship):
        await mod_multilog.send_to_log(
            self.log, self,
            'relationship_add: {}'.format(relationship),
            lg.DEBUG)

    async def on_relationship_update(self, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'relationship_update: {} {}'.format(before, after),
            lg.DEBUG)

    # Messaging

    async def on_message(self, message: discord.message.Message):
        # Echo Protection
        if message.author == self.user:
            return

    async def on_message_delete(self, message):
        await mod_multilog.send_to_log(
            self.log, self,
            'message_delete: {}'.format(message),
            lg.DEBUG)

    async def on_bulk_message_delete(self, messages):
        await mod_multilog.send_to_log(
            self.log, self,
            'bulk_message_delete: {}'.format(messages),
            lg.DEBUG)

    # FIXME
    # For some reason this function exceptions everytime I sent an embed
    async def on_message_edit(self, message):
        await mod_multilog.send_to_log(
            self.log, self,
            'on message edit: {}'.format(message),
            lg.DEBUG)

    # Reactions

    async def on_reaction_add(self, reaction, user):
        await mod_multilog.send_to_log(
            self.log, self,
            'reaction add: {} {}'.format(reaction, user),
            lg.DEBUG)

    async def on_reaction_remove(self, reaction, user):
        await mod_multilog.send_to_log(
            self.log, self,
            'reaction remove: {} {}'.format(reaction, user),
            lg.DEBUG)

    async def on_reaction_clear(self, reaction, user):
        await mod_multilog.send_to_log(
            self.log, self,
            'reaction clear: {} {}'.format(reaction, user),
            lg.DEBUG)

    async def on_reaction_clear_emoji(self, reaction):
        await mod_multilog.send_to_log(
            self.log, self,
            'reaction clear emoji: {}'.format(reaction),
            lg.DEBUG)

    # Private Channels

    async def on_private_channel_delete(self, channel):
        await mod_multilog.send_to_log(
            self.log, self,
            'private channel delete: {}'.format(channel),
            lg.DEBUG)

    async def on_private_channel_create(self, channel):
        await mod_multilog.send_to_log(
            self.log, self,
            'private channel create: {}'.format(channel),
            lg.DEBUG)

    async def on_private_channel_update(self, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'private channel update: {} {}'.format(before, after),
            lg.DEBUG)

    async def on_private_channel_pins_update(self, channel, last_pin):
        await mod_multilog.send_to_log(
            self.log, self,
            'private channel pins update: {} {}'.format(channel, last_pin),
            lg.DEBUG)

    # Member

    async def on_member_join(self, member):
        await mod_multilog.send_to_log(
            self.log, self,
            'member_join: {}'.format(member),
            lg.DEBUG)

    async def on_member_remove(self, member):
        await mod_multilog.send_to_log(
            self.log, self,
            'member_remove: {}'.format(member),
            lg.DEBUG)

    async def on_member_update(self, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'React to Member Update: {}->{}'.format(
                before, after),
            lg.DEBUG)

    async def on_member_ban(self, guild, user):
        await mod_multilog.send_to_log(
            self.log, self,
            'member_ban: {} {}'.format(guild, user),
            lg.DEBUG)

    async def on_member_unban(self, guild, user):
        await mod_multilog.send_to_log(
            self.log, self,
            'member_unban: {} {}'.format(guild, user),
            lg.DEBUG)

    # Guild

    async def on_guild_channel_delete(self, channel):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_channel_delete: {}'.format(channel),
            lg.DEBUG)

    async def on_guild_channel_create(self, channel):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_channel_create: {}'.format(channel),
            lg.DEBUG)

    async def on_guild_channel_update(self, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_channel_update: {} {}'.format(before, after),
            lg.DEBUG)

    async def on_guild_channel_pins_update(self, channel, last_pin):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_channel_pins_update: {} {}'.format(channel, last_pin),
            lg.DEBUG)

    async def on_guild_integrations_update(self, guild):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_integrations_update: {}'.format(guild),
            lg.DEBUG)

    async def on_guild_join(self, guild):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_join: {}'.format(guild),
            lg.DEBUG)

    async def on_guild_remove(self, guild):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_remove: {}'.format(guild),
            lg.DEBUG)

    async def on_guild_update(self, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_update: {} {}'.format(before, after),
            lg.DEBUG)

    async def on_guild_role_create(self, role):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_role_create: {}'.format(role),
            lg.DEBUG)

    async def on_guild_role_delete(self, role):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_role_delete: {}'.format(role),
            lg.DEBUG)

    async def on_guild_role_update(self, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_role_update: {} {}'.format(before, after),
            lg.DEBUG)

    async def on_guild_emojis_update(self, guild, before, after):
        await mod_multilog.send_to_log(
            self.log, self,
            'on_guild_emojis_update: {} {} {}'.format(guild, before, after),
            lg.DEBUG)

    async def on_guild_available(self, guild):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_available: {} {}'.format(guild, self.guilds),
            lg.DEBUG)

    async def on_guild_unavailable(self, guild):
        await mod_multilog.send_to_log(
            self.log, self,
            'guild_unavailable: {} {}'.format(guild, self.guilds),
            lg.DEBUG)

    async def update_bot_state(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                # TODO; Period tasks/classes go here.
                await asyncio.sleep(reddit_update_frequency)
            except Exception as e:
                await mod_multilog.send_to_log(
                    self.log, self, str(e.args), lg.ERROR)

    def start_daemon(self):
        self.log.info('Starting WiiHacky Daemon...')
        self.running = True
        self.run(self.config.data['discord']['token'])
        self.log.info('WiiHacky Daemon has shut down...')


if __name__ == "__main__":
    wh = WiiHacky()
    wh.start_daemon()
