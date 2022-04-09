from nixbot.bot.settings import get_settings_for_bot
from nixbot.extensions.bot import ExtendedBot


class X(ExtendedBot):
    name = 'x'

    def __init__(self):
        super().__init__(settings=get_settings_for_bot(self.name), plugins=[])
