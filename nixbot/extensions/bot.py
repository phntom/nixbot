from typing import Optional, Sequence

from mmpy_bot import Bot, Settings, Plugin

from nixbot.extensions import webhook
from ..utils.health import health, ready
from ..utils.websocket import patch_event_handler


class ExtendedBot(Bot):
    def __init__(self,
                 settings: Optional[Settings] = None,
                 plugins: Optional[Sequence[Plugin]] = None,):

        webhook_enabled = settings.WEBHOOK_HOST_ENABLED
        settings.WEBHOOK_HOST_ENABLED = False

        super().__init__(settings=settings, plugins=plugins)

        if webhook_enabled and webhook.WEBHOOK is None:
            self._initialize_webhook_server()
            webhook.WEBHOOK = self.webhook_server
            webhook.WEBHOOK.app.router.add_view('/_healthz', lambda _: health)
            webhook.WEBHOOK.app.router.add_view('/_ready', lambda _: ready)
        else:
            self.webhook_server = webhook.WEBHOOK
            self.driver.register_webhook_server(webhook.WEBHOOK)

        patch_event_handler(self.event_handler)
