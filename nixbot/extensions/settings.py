from dataclasses import dataclass

from mmpy_bot import Settings


@dataclass
class ExtendedSettings(Settings):
    SETTINGS_CHANNEL: str = 'N/A'
    TARGET_USER: str = 'N/A'

