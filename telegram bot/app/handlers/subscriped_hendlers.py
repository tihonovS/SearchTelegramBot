from aiogram import Dispatcher, types
from ..middleware.scheduler import Scheduler


async def star_scheduler(message: types.Message, scheduler: Scheduler):
    await scheduler.run(message.from_user.id)


async def stop_schedule(message: types.Message, scheduler: Scheduler):
    await scheduler.stop(message.from_user.id)


def register_subscribed_handlers(dp: Dispatcher):
    dp.register_message_handler(star_scheduler, commands=['start_scheduler'], state="*")
    dp.register_message_handler(stop_schedule, commands=['stop_scheduler'], state="*")
