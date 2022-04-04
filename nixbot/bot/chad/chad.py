from .linkedin import LinkedIn
from ..settings import get_settings_for_bot
from ...extensions.bot import ExtendedBot


class Chad(ExtendedBot):
    name = 'chad'

    def __init__(self):
        self.linkedin = LinkedIn()
        super().__init__(settings=get_settings_for_bot(self.name), plugins=[self.linkedin])
