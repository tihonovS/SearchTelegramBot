from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class KufarState(StatesGroup):
    waiting_for_query = State()
    view_storage = State()


async def kufar_start(message: types.Message):
    await message.answer("что будем искать на kufar.by")
    await KufarState.waiting_for_query.set()


async def kufar_query(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "kufar" in data:
        data.get("kufar").append({"query": message.text})
    else:
        data = {"kufar": [{"query": message.text}]}

    await state.set_data(data)
    await state.reset_state(with_data=False)


def register_kufar_state(dp: Dispatcher):
    dp.register_message_handler(kufar_start, commands="kufar", state="*")
    dp.register_message_handler(kufar_query, state=KufarState.waiting_for_query)
