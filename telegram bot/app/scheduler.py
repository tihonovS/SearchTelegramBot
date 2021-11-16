from aiogram import types
from aiogram.dispatcher import FSMContext
import ast

from loader import callback_scheduler, dp


def add_subscribe_keyboard(query_data: dict):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    inline_button = types.InlineKeyboardButton(
        text="подписаться на запрос",
        callback_data=callback_scheduler.new(action='subscribe', data=query_data)
    )
    keyboard.add(inline_button)
    return keyboard


@dp.callback_query_handler(callback_scheduler.filter(action='subscribe'))
async def subscribe_on_query(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    data_ = ast.literal_eval(callback_data['data'])
    await add_scheduler_to_store(data_, state)
    await call.message.answer("вы подписались на запрос")
    await call.answer()


async def add_scheduler_to_store(callback_data: dict, state: FSMContext):
    storage: dict = await state.get_data()
    site: list = storage.get(callback_data.get('site'))
    for item in site:
        if item.get('query') == callback_data.get('query'):
            item['subscribed'] = True
    await state.set_data(storage)
