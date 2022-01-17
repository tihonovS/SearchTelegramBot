from aiogram import Dispatcher
from aiogram.utils import executor
import logging

from app import init_hendlers
from app.chain import call_chain
from app.middleware.query_id_middlervare import QueryIdMiddleware
from app.scheduler import add_scheduler_job
from loader import bot, dp, async_scheduler
from app.kufar import kufar_hendlers
from app.storage import storage_handler
from app.onliner import onliner_offers_hendlers


async def on_startup(dispatcher: Dispatcher):
    for chat_id, value in dispatcher.storage.data.items():
        for user_id, value1 in value.items():
            scheduler_job_id = await add_scheduler_job(user_id, chat_id, dispatcher.storage)
            value1['data']['scheduler_job_id'] = scheduler_job_id
    dispatcher.setup_middleware(QueryIdMiddleware())
    async_scheduler.start()

    await init_hendlers.set_commands(bot)


async def on_shutdown(dispatcher: Dispatcher):
    logging.info("shutdown app")
    for key, value in dispatcher.storage.data.items():
        for key1, value1 in value.items():
            value1['state'] = None
    async_scheduler.shutdown()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, on_shutdown=on_shutdown)
