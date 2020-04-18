"""WiiHacky Module."""

import asyncio
import constants
import discord
import logging as lg

bloody_id = 574629343142346757


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

    def __init__(self):
        """Initialize WiiHacky."""
        discord.Client.__init__(self)

        # init logger
        lg.basicConfig(
            level=lg.INFO, format=constants.LOG_FORMAT_STRING)
        self.log = lg.getLogger(self.__class__.__name__)
        self.log.setLevel(lg.DEBUG)
        self.log.info(constants.TXT_LOGGER_SUCC)

        # register reddit update routine.
        self.reddit_update_frequency = 5
        self.reddit_comment_index = None
        self.reddit_submission_index = None
        self.loop.create_task(self.update_bot_state())
        # TODO:make this configurable
        self.bot_cli_channel = ('WiiHacks', 'bot_cli')
        self.subreddit_relay = 'WiiHacks'

        # store configuration
        try:
            self.config = load_config()
        except Exception as e:
            # TODO : Move to constants
            log_config_load_failed = 'failed to load config: {}'
            self.log.critical(log_config_load_failed.format(e))
            exit(-1)

        # init reddit instance
        import praw as pr
        self.reddit = pr.Reddit(
            user_agent=self.config['reddit']['user_agent'],
            client_id=self.config['reddit']['client_id'],
            client_secret=self.config['reddit']['client_secret'],
            username=self.config['reddit']['username'],
            password=self.config['reddit']['password'])
        self.log.info(constants.TXT_REDDIT_SUCC)
        self.log.info(constants.TXT_LOGGED_IN, self.reddit.user.me())

        # set interactive
        self.running = False

    # Utilities

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
        output = \
            '{} is ready, version {}. Praw version {}. Discord.py version {}.'

        ch = discord.utils.get(
            self.get_all_channels(),
            guild__name=self.bot_cli_channel[0],
            name=self.bot_cli_channel[1])

        import praw
        output = output.format(
            self.user,
            constants.__version__,
            praw.__version__,
            discord.__version__)
        self.log.info(output)
        await ch.send(output)

    async def on_error(self, event, *args, **kwargs):
        """
        Error handler.

        When an error message occurs, this function formats it and outputs it.
        """
        self.log.error('on_error: {} {} {}'.format(event, args, kwargs))

    async def on_typing(self, channel, user, when):
        """
        On Typing reaction.
        :param channel:
        :param user:
        :param when:
        :return: None
        """
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
        if message.author.name == self.user.name:
            return
        
        # There are only three classes of messages we respond to.
        # Anything in the bot_cli channel.
        # TODO : Command char should eventually be a property of the aliases.
        command_char = '!'
        if message.guild == self.bot_cli_channel[0] and \
           message.channel == self.bot_cli_channel[1]:
            self.log.debug('TODO:Respond to CLI Message {}'.format(message))
        # Anything that is a registered alias.
        if message.content[0:1] == command_char:
            self.log.debug('TODO:Respond to Alias {}'.format(message))
        # andthing with @WiiHacky in it
        if message.content.find(self.user.id) != -1:
            self.log.debug('Respond to @Mentions {}'.format(message))
        # TODO: Good Question? Is it beneficial for the bot to respond to
        # more than one of these conditions? Make a truth table.

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

    async def on_member_update(self,
                               before: discord.member.Member,
                               after: discord.member.Member):
        self.log.debug('TODO: React to Member Update{}->{}'.format(
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
                await asyncio.sleep(self.reddit_update_frequency)
            except Exception as e:
                self.log.error(e)
                await asyncio.sleep(self.reddit_update_frequency)

    def start_daemon(self):
        self.log.info('Starting WiiHacky Daemon...')
        self.running = True
        self.run(self.config['discord']['token'])
        self.log.info('WiiHacky Daemon has shut down...')


if __name__ == "__main__":
    wh = WiiHacky()
    wh.start_daemon()
