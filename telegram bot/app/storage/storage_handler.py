from aiogram import types
from aiogram.dispatcher import FSMContext
import ast

from loader import dp, callback_action, callback_action_with_data


@dp.callback_query_handler(callback_action.filter(action="edit_store"))
async def choose_site_from_store(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    data_ = await state.get_data()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, value in data_['site'].items():
        inline_button = types.InlineKeyboardButton(
            text=key,
            callback_data=callback_action_with_data.new(action="choose_store_site", data={"site": key})
        )
        buttons.append(inline_button)
    keyboard.add(*buttons)
    await call.message.answer("выберите сайт", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(callback_action_with_data.filter(action="choose_store_site"))
async def choose_query_from_store(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    storage = await state.get_data()

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    callback_data_ = ast.literal_eval(callback_data['data'])
    for item in storage['site'][callback_data_['site']]:
        callback_data_['query_id'] = item['query_id']
        inline_button = types.InlineKeyboardButton(
            text=item['query'],
            callback_data=callback_action_with_data.new(action="choose_store_query", data=callback_data_)
        )
        buttons.append(inline_button)
    keyboard.add(*buttons)

    await call.message.answer("выберите запрос", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(callback_action_with_data.filter(action="choose_store_query"))
async def select_action(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    data_ = ast.literal_eval(callback_data['data'])

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    inline_button_edit = types.InlineKeyboardButton(
            text="редактировать запрос",
            callback_data=callback_action_with_data.new(action="edit_store_query", data=data_)
    )
    inline_button_subscribe = types.InlineKeyboardButton(
            text="подписаться на запрос",
            callback_data=callback_action_with_data.new(action="edit_store_subscribe", data=data_)
    )
    inline_button_unsubscribe = types.InlineKeyboardButton(
            text="отписаться от запроса",
            callback_data=callback_action_with_data.new(action="edit_store_unsubscribe", data=data_)
    )
    inline_button_delete = types.InlineKeyboardButton(
            text="удалить запрос",
            callback_data=callback_action_with_data.new(action="edit_store_delete", data=data_)
    )
    keyboard.add(inline_button_edit)
    keyboard.add(inline_button_subscribe)
    keyboard.add(inline_button_unsubscribe)
    keyboard.add(inline_button_delete)

    storage = await state.get_data()
    query = list(filter(lambda i: i['query_id'] == data_['query_id'], storage['site'][data_['site']]))[0]
    await call.message.answer(f"Выбранные параметры сайт-\"{data_['site']}\" запрос-\"{query['query']}\"",
                              reply_markup=keyboard)
    await call.answer()
