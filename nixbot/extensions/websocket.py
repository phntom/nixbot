# noinspection PyProtectedMember
from mattermostdriver import Websocket


class ExtendedWebsocket(Websocket):
    websocket = None

    async def _authenticate_websocket(self, websocket, event_handler):
        self.websocket = websocket
        await super()._authenticate_websocket(websocket, event_handler)
