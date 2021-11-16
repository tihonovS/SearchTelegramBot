from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.kufar.kufar_chain import KufarHandlerChain
from app.scheduler import add_subscribe_keyboard
from loader import dp, callback_numbers


class KufarState(StatesGroup):
    waiting_for_query = State()


@dp.callback_query_handler(callback_numbers.filter(action=KufarHandlerChain.site_name()))
async def kufar_start(call: types.CallbackQuery, callback_data: dict):
    await call.message.delete_reply_markup()
    await call.message.answer(f"что будем искать на {callback_data['action']}")
    await KufarState.waiting_for_query.set()
    await call.answer()


@dp.message_handler(state=KufarState.waiting_for_query)
async def kufar_query(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "kufar" in data:
        data.get("kufar").append({"query": message.text})
    else:
        data = {"kufar": [{"query": message.text}]}

    await state.set_data(data)
    await state.reset_state(with_data=False)
    await message.answer(f"ваш запрос {message.text}",
                         reply_markup=add_subscribe_keyboard({"site": 'kufar', 'query': message.text}))
