import logging
from os import getenv
from sys import exit
import pathlib

import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram.utils import executor

from app.middleware.scheduler_middleware import SchedulerMiddleware
from app.middleware.scheduler import Scheduler
from app.handlers import init_hendlers
from app.chain import chain

logging.basicConfig(level=logging.INFO)
bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(bot_token)
dispatcher = Dispatcher(bot, storage=JSONStorage(pathlib.Path("app/storage.json")))


async def on_startup(dp: Dispatcher):
    register_chain = chain.register_chain(bot)

    scheduler = Scheduler(bot, register_chain)

    init_hendlers.register_init_handlers(dp)
    await init_hendlers.set_commands(bot)

    dp.middleware.setup(SchedulerMiddleware(scheduler))


async def on_shutdown(dp: Dispatcher):
    for job in dp.middleware.applications[0].scheduler.job_map:
        aioschedule.cancel_job(job)

if __name__ == '__main__':
    executor.start_polling(dispatcher, on_startup=on_startup, skip_updates=True, on_shutdown=on_shutdown)
