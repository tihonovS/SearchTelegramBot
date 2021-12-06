from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold

from app.chain import AbstractHandlerChain
from loader import dp, callback_action
from .scheduler import scheduler_resume, scheduler_pause


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/add_query", description="добавить запрос на сайт:"),
        types.BotCommand(command="/storage", description="текущие запросы"),
        types.BotCommand(command="/cancel", description="прерывает действие и возобновляет планировщик заданий")
    ]
    await bot.set_my_commands(commands)


@dp.message_handler(commands="cancel", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.set_state(None)
    await scheduler_resume(state)
    await message.answer("Действие прервано")


@dp.message_handler(commands="add_query", state="*")
async def add_query(message: types.Message, state: FSMContext):
    await scheduler_pause(state)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for clazz in AbstractHandlerChain.__subclasses__():
        inline_button = types.InlineKeyboardButton(
            text=clazz.site_name(),
            callback_data=callback_action.new(action=clazz.action_name())
        )
        buttons.append(inline_button)
    keyboard.add(*buttons)
    await message.answer("Выберите сайт", reply_markup=keyboard)


@dp.message_handler(commands="storage", state="*")
async def view_storage(message: types.Message, state: FSMContext):
    data_: dict = await state.get_data()
    msg = "Ваши запросы: \n"
    has_query = False
    for site_key, site_value in data_['site'].items():
        if isinstance(site_value, list):
            value_text = ""
            for value in site_value:
                has_query = True
                subscribed_text = "не подписаны на запрос"
                if 'subscribed' in value and value['subscribed']:
                    subscribed_text = "подписаны на запрос"
                value_text += f"       {value['query']} \-\- {subscribed_text}\n"
            msg += text(f" {bold(site_key)}", value_text, sep="\n")
    if has_query:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_button = types.InlineKeyboardButton(
            text="Редактировать",
            callback_data=callback_action.new(action="edit_store")
        )
        keyboard.add(inline_button)
        await message.answer(msg, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)
    else:
        await message.answer("У вас нету новых запросов. \n"
                             "Их можно добавить коммандой /add_query")


@dp.message_handler(commands="start", state="*")
async def send_welcome(message: types.Message, state: FSMContext):
    storage = await state.get_data()
    if "last_query_id" not in storage:
        storage['last_query_id'] = 0
    if "site" not in storage:
        storage['site'] = {}
    await state.set_data(storage)
    await message.answer("Привет, я покажу последние объявления о необходимых тебе товарах. "
                         "Для начала ввода первого запроса нажмите /add_query")
