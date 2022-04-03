from nixbot.extensions.websocket import ExtendedWebsocket


def patch_event_handler(event_handler):
    # noinspection PyProtectedMember
    event_handler.start = lambda: event_handler.driver.init_websocket(event_handler._handle_event, ExtendedWebsocket)
