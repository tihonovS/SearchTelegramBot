from aiogram import Bot, types
from aiogram.dispatcher import FSMContext

from app.chain import AbstractHandlerChain
from loader import dp, callback_numbers


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/add_query", description="добавить запрос на сайт:"),
        types.BotCommand(command="/storage", description="текущие запросы")
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
    await message.answer("Привет, я покажу последние объявления о необходимых тебе товарах." +
                         " Для начала ввода первого запроса нажмите /add_query")
