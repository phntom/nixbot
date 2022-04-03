from .linkedin import LinkedIn
from ..settings import SETTINGS
from ...extensions.bot import ExtendedBot


class Chad(ExtendedBot):
    def __init__(self):
        self.linkedin = LinkedIn()
        super().__init__(settings=SETTINGS, plugins=[self.linkedin])
