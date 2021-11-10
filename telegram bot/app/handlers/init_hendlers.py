from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand
import json

from .subscriped_hendlers import register_subscribed_handlers
from .kufar_hendlers import register_kufar_state


async def send_welcome(message: types.Message):
    await message.reply("Hi i'm bot")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start_scheduler", description="подписаться на показ объявлений"),
        BotCommand(command="/stop_scheduler", description="отписаться от показа объявлений"),
        BotCommand(command="/kufar", description="ввести запрос на kufar"),
        BotCommand(command="/storage", description="текущие запросы"),
    ]
    await bot.set_my_commands(commands)


async def view_storage(message: types.Message, state: FSMContext):
    data_ = await state.get_data()
    await message.answer(json.dumps(data_))


def register_init_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'], state="*")
    dp.register_message_handler(view_storage, commands=['storage'], state="*")

    register_subscribed_handlers(dp)
    register_kufar_state(dp)
