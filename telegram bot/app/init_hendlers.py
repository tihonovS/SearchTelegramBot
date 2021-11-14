from aiogram import Bot, types
from aiogram.dispatcher import FSMContext

from app.chain import AbstractHandlerChain
from app.middleware.scheduler import Scheduler
from loader import dp, callback_numbers


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="начать общение с ботом"),
        types.BotCommand(command="/add_query", description="добавить запрос на сайт:"),
        types.BotCommand(command="/storage", description="текущие запросы"),
        types.BotCommand(command="/start_scheduler", description="подписаться на показ объявлений"),
        types.BotCommand(command="/stop_scheduler", description="отписаться от показа объявлений")
    ]
    await bot.set_my_commands(commands)


@dp.message_handler(commands="add_query", state="*")
async def add_query(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for clazz in AbstractHandlerChain.__subclasses__():
        inline_button = types.InlineKeyboardButton(
            text=clazz.site_name(),
            callback_data=callback_numbers.new(action=clazz.site_name())
        )
        buttons.append(inline_button)
    keyboard.add(*buttons)
    await message.answer("Выберите сайт", reply_markup=keyboard)


@dp.message_handler(commands="storage", state="*")
async def view_storage(message: types.Message, state: FSMContext):
    data_ = await state.get_data()
    await message.answer(f"{data_}")


@dp.message_handler(commands="start", state="*")
async def send_welcome(message: types.Message):
    await message.reply("Hi i'm bot")


@dp.message_handler(commands="start_scheduler", state="*")
async def star_scheduler(message: types.Message, scheduler: Scheduler, state: FSMContext):
    await scheduler.run(message.from_user.id, state)


@dp.message_handler(commands="stop_scheduler", state="*")
async def stop_schedule(message: types.Message, scheduler: Scheduler):
    await scheduler.stop(message.from_user.id)
