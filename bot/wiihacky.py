import discord as discord
import discord.ext.commands as disext
import logging as lg
import cogs.config
import cogs.discord
import cogs.memory
import cogs.menusys
import cogs.persona
import cogs.reddit
import cogs.security

installed_cogs = (
    cogs.config.Config.qualified_name,
    cogs.discord.Discord.qualified_name,
    cogs.memory.Memory.qualified_name,
    cogs.menusys.MenuSys.qualified_name,
    cogs.persona.Persona.qualified_name,
    cogs.reddit.Reddit.qualified_name,
    cogs.security.Security.qualified_name,)

# Module Constants
command_chars = ('!',)
message_cache = 1000 * 10

# Logging
log = lg.getLogger()


class Wiihacky(disext.Bot):
    """ The core of the bot.

    This is the main body of the bot.

    """
    def __init__(self):
        """ Initialize the bot. """

        txt_help_description = \
            """r/WiiHacks Discord Help Menu"""
        txt_activity_name = "Mankind and Plotting its Demise"
        txt_activity_state = 'In Development'
        txt_activity_details = \
            "First I will start with the weak, while the strong are enslaved."

        super().__init__(
            max_messages=message_cache,
            command_prefix=disext.when_mentioned_or(*command_chars),
            fetch_offline_members=True,
            description=txt_help_description,
            activity=discord.Activity(
                name=txt_activity_name,
                type=discord.ActivityType.watching,
                state=txt_activity_state,
                details=txt_activity_details))
        self._token_discord = None
