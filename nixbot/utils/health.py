from aiohttp import web


def health():
    return web.Response(text="Hello")


def ready():
    return web.Response(text="Ready")
