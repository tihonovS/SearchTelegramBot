import aioschedule
from aiogram import Dispatcher
from aiogram.utils import executor

from app.middleware.scheduler_middleware import SchedulerMiddleware
from app.middleware.scheduler import Scheduler
from app import init_hendlers
from loader import bot, dp
from app.kufar import kufar_hendlers
from app.kufar import kufar_chain


def register_chain():
    first = kufar_chain.KufarHandlerChain(bot)
    return first


async def on_startup(dispatcher: Dispatcher):
    chain = register_chain()

    scheduler = Scheduler(bot, chain)

    await init_hendlers.set_commands(bot)

    dispatcher.middleware.setup(SchedulerMiddleware(scheduler))


async def on_shutdown(dispatcher: Dispatcher):
    for job in dispatcher.middleware.applications[0].scheduler.job_map:
        aioschedule.cancel_job(job)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, on_shutdown=on_shutdown)
