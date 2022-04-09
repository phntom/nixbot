from typing import Optional

from mattermostdriver.exceptions import NotEnoughPermissions
from mmpy_bot import Plugin, Message
from mmpy_bot.driver import Driver

from nixbot.extensions.settings import ExtendedSettings


class ExtendedPlugin(Plugin):
    direct_channels = {}
    settings = None

    def __init__(self):
        super().__init__()
        self.bot = None

    def initialize(self, driver: Driver, settings: Optional[ExtendedSettings] = None):
        super().initialize(driver, settings)
        self.settings = settings
        self.on_load(driver)
        return self

    def on_load(self, driver: Driver):
        pass

    async def user_typing(self, channel_id: str, parent_post_id: Optional[str] = None):
        await self.bot.event_handler.user_typing(channel_id, parent_post_id, 1)

    async def direct_reply(self, message: Message, response: str, human=True, *nargs, **kwargs):
        if not message.is_direct_message:
            try:
                return self.driver.reply_to(message, response, ephemeral=True, *nargs, **kwargs)
            except NotEnoughPermissions:
                pass
        direct_channel_id = self.direct_channels.get(message.user_id)
        if not direct_channel_id:
            result = self.driver.channels.create_direct_message_channel([message.user_id, self.driver.user_id])
            direct_channel_id = result['id']
            self.direct_channels[message.user_id] = direct_channel_id
        if message.is_direct_message and human:
            await self.user_typing(direct_channel_id)
        return self.driver.create_post(direct_channel_id, response, *nargs, **kwargs)
