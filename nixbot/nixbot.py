# -*- coding: utf-8 -*-

"""Main module."""
import asyncio

from nixbot.bot import bots

bot_instances = [bot() for bot in bots]


def run():
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(bot.run())
        for bot in bot_instances
    ]
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    run()
