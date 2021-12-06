from aiogram import Dispatcher
from aiogram.utils import executor

from app import init_hendlers
from app.chain import call_chain
from app.middleware.query_id_middlervare import QueryIdMiddleware
from loader import bot, dp, async_scheduler
from app.kufar import kufar_hendlers
from app.storage import storage_handler
from app.onliner import onliner_offers_hendlers
from app.kufar import kufar_chain


def register_chain():
    first = kufar_chain.KufarHandlerChain(bot)
    return first


async def on_startup(dispatcher: Dispatcher):
    chain = register_chain()
    for key, value in dispatcher.storage.data.items():
        for key1, value1 in value.items():
            func_args = [key, key1, chain, dispatcher.storage]
            job = async_scheduler.add_job(call_chain, 'interval', minutes=5, args=func_args)
            value1['data']['scheduler_job_id'] = job.id
    dispatcher.setup_middleware(QueryIdMiddleware())
    async_scheduler.start()

    await init_hendlers.set_commands(bot)


async def on_shutdown(dispatcher: Dispatcher):
    for key, value in dispatcher.storage.data.items():
        for key1, value1 in value.items():
            value1['state'] = None
    async_scheduler.shutdown()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, on_shutdown=on_shutdown)
