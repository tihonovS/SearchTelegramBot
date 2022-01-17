from aiogram import types
from aiogram.dispatcher import FSMContext
import ast
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.chain import AbstractHandlerChain
from loader import dp, callback_action, callback_action_with_data
from app.scheduler import scheduler_pause, scheduler_resume


class StorageState(StatesGroup):
    edit_query_state = State()


@dp.callback_query_handler(callback_action.filter(action="edit_store"))
async def choose_site_from_store(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await scheduler_pause(state)
    data_ = await state.get_data()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, value in data_['site'].items():
        for clazz in AbstractHandlerChain.__subclasses__():
            if clazz.action_name() == key:
                inline_button = types.InlineKeyboardButton(
                    text=clazz.site_name(),
                    #     csc == choose_store_site
                    callback_data=callback_action_with_data.new(action="csc", data={"site": key})
                )
                buttons.append(inline_button)
    keyboard.add(*buttons)
    await call.message.answer("выберите сайт", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(callback_action_with_data.filter(action="csc"))
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
    callback_data_ = ast.literal_eval(callback_data['data'])
    storage = await state.get_data()
    query = get_query_by_site(callback_data_, storage)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    inline_button_edit = types.InlineKeyboardButton(
        text="редактировать запрос",
        callback_data=callback_action_with_data.new(action="edit_store_query", data=callback_data_)
    )
    if 'subscribed' in query and query['subscribed']:
        inline_button_unsubscribe = types.InlineKeyboardButton(
            text="отписаться от запроса",
            callback_data=callback_action_with_data.new(action="edit_store_unsubscribe", data=callback_data_)
        )
        keyboard.add(inline_button_unsubscribe)
    else:
        inline_button_subscribe = types.InlineKeyboardButton(
            text="подписаться на запрос",
            callback_data=callback_action_with_data.new(action="edit_store_subscribe", data=callback_data_)
        )
        keyboard.add(inline_button_subscribe)

    inline_button_delete = types.InlineKeyboardButton(
        text="удалить запрос",
        callback_data=callback_action_with_data.new(action="edit_store_delete", data=callback_data_)
    )
    keyboard.add(inline_button_edit)
    keyboard.add(inline_button_delete)

    await call.message.answer(f"Какие действия Вы хотели бы совершить в отношении запроса \"{query['query']}\" на "
                              f"сайте \"{callback_data_['site']}\"",
                              reply_markup=keyboard)
    await call.answer()


def get_query_by_site(callback_data_, storage):
    query = list(filter(lambda i: i['query_id'] == callback_data_['query_id'], storage['site'][callback_data_['site']]))
    return query[0]


@dp.callback_query_handler(callback_action_with_data.filter(action="edit_store_delete"))
async def edit_store_delete(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete_reply_markup()
    storage: dict = await state.get_data()
    callback_data_ = ast.literal_eval(callback_data['data'])
    query = get_query_by_site(callback_data_, storage)
    site_: list = storage['site'][callback_data_['site']]
    site_.remove(query)
    if len(site_) <= 0:
        del storage['site'][callback_data_['site']]
    await state.set_data(storage)
    await scheduler_resume(state)
    await call.message.answer(f"Запрос \"{query['query']}\" успешно удален")
    await call.answer()


@dp.callback_query_handler(callback_action_with_data.filter(action="edit_store_unsubscribe"))
async def edit_store_unsubscribe(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    storage = await state.get_data()
    callback_data_ = ast.literal_eval(callback_data['data'])
    query = get_query_by_site(callback_data_, storage)
    query['subscribed'] = False
    await state.set_data(storage)
    await scheduler_resume(state)
    await call.message.answer(f"Подписка отменена на запрос \"{query['query']}\" ")
    await call.answer()


@dp.callback_query_handler(callback_action_with_data.filter(action="edit_store_subscribe"))
async def edit_store_subscribe(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    storage = await state.get_data()
    callback_data_ = ast.literal_eval(callback_data['data'])
    query = get_query_by_site(callback_data_, storage)
    query['subscribed'] = True
    await state.set_data(storage)
    await scheduler_resume(state)
    await call.message.answer(f"Вы подписались на запрос \"{query['query']}\" ")
    await call.answer()


@dp.callback_query_handler(callback_action_with_data.filter(action="edit_store_query"))
async def edit_store_query(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()

    storage = await state.get_data()
    callback_data_ = ast.literal_eval(callback_data['data'])
    storage['edit_store_state'] = callback_data_
    await state.set_data(storage)
    await StorageState.edit_query_state.set()

    await call.message.answer(f"Введите новый запрос")

    await call.answer()


@dp.message_handler(state=StorageState.edit_query_state)
async def edit_query_state(message: types.Message, state: FSMContext):
    storage = await state.get_data()
    site_ = storage['site']
    edit_store_state_ = storage['edit_store_state']
    query = get_query_by_site(edit_store_state_, storage)
    query['query'] = message.text
    del storage['edit_store_state']
    await state.set_data(storage)
    await state.reset_state(with_data=False)
    await scheduler_resume(state)
    await message.answer("Запрос отредактирован")
