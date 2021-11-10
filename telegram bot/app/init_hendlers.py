from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
import json

from app.middleware.scheduler import Scheduler
from loader import dp


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start_scheduler", description="подписаться на показ объявлений"),
        types.BotCommand(command="/stop_scheduler", description="отписаться от показа объявлений"),
        types.BotCommand(command="/kufar", description="ввести запрос на kufar"),
        types.BotCommand(command="/storage", description="текущие запросы"),
        types.BotCommand(command="/start", description="начать общение с ботом"),
    ]
    await bot.set_my_commands(commands)


@dp.message_handler(commands="storage", state="*")
async def view_storage(message: types.Message, state: FSMContext):
    data_ = await state.get_data()
    await message.answer(json.dumps(data_))


@dp.message_handler(commands="start", state="*")
async def send_welcome(message: types.Message):
    await message.reply("Hi i'm bot")


@dp.message_handler(commands="start_scheduler", state="*")
async def star_scheduler(message: types.Message, scheduler: Scheduler, state: FSMContext):
    await scheduler.run(message.from_user.id, state)


@dp.message_handler(commands="stop_scheduler", state="*")
async def stop_schedule(message: types.Message, scheduler: Scheduler):
    await scheduler.stop(message.from_user.id)
