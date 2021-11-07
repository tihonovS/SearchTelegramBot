# import kufar_requests
import asyncio
import logging
from os import getenv
from sys import exit

from aiogram import Bot, Dispatcher

from app.middleware.scheduler_middleware import SchedulerMiddleware
from app.middleware.scheduler import Scheduler
from app.handlers.init_henplers import register_init_handlers
from app.handlers.subscriped_hendlers import register_subscribed_handlers
from app.chain import chain


async def main():
    logging.basicConfig(level=logging.INFO)
    bot_token = getenv("BOT_TOKEN")
    if not bot_token:
        exit("Error: no token provided")

    bot = Bot(bot_token)
    dispatcher = Dispatcher(bot)

    register_chain = chain.register_chain(bot)

    scheduler = Scheduler(bot, register_chain)

    register_init_handlers(dispatcher)
    register_subscribed_handlers(dispatcher)

    dispatcher.middleware.setup(SchedulerMiddleware(scheduler))
    await dispatcher.skip_updates()
    await dispatcher.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
