import logging as lg
from ..action import Action


class SendMessage(Action):

    def __init(self, log: lg.Logger, *args, **kwargs):
        super().__init__(log)
        self.guild = kwargs['guild']
        self.channel = kwargs['channel']
        self.text = kwargs['message']

    async def execute(self, *args, **kwargs):
        import discord
        txtch: discord.TextChannel = wh.discord.utils.get(
            wh.get_all_channels(),
            guild__name=self.guild,
            name=self.channel)

        await txtch.send(self.text)
        #log = 'Message sent: {} -> {} -> {}'.format(
        #    self.guild,
        #    self.channel,
        #    self.message)
        #self.log.debug(log)
        #if self.log.level == lg.DEBUG:
        #    logch: discord.TextChannel = wh.discord.utils.get(
        #        wh.get_all_channels(),
        #        guild__name=wh.bot_cli_channel[0],
        #        name=wh.bot_cli_channel[1])
        #    await logch.send(log)
        return
