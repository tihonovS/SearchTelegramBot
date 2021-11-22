from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.kufar.kufar_chain import KufarHandlerChain
from app.scheduler import add_subscribe_keyboard, scheduler_resume
from loader import dp, callback_action


class KufarState(StatesGroup):
    waiting_for_query = State()


@dp.callback_query_handler(callback_action.filter(action=KufarHandlerChain.site_name()))
async def kufar_start(call: types.CallbackQuery, callback_data: dict):
    await call.message.delete_reply_markup()
    await call.message.answer(f"что будем искать на {callback_data['action']}")
    await KufarState.waiting_for_query.set()
    await call.answer()


@dp.message_handler(state=KufarState.waiting_for_query)
async def kufar_query(message: types.Message, state: FSMContext):
    query_id = await KufarHandlerChain.add_query_to_storage(message.text, state)
    await state.reset_state(with_data=False)
    await scheduler_resume(state)
    link = await KufarHandlerChain(None).get_last_query(query_id, message.text, state)
    link_message = "По вашему запросу ничего не найдено"
    if link:
        link_message = f"Это последнее из объявлений, которое я нашёл по Вашему запросу, Для того, чтобы продолжить " \
                       f"получать актуальную информацию об объявлениях по запросу {message.text}, " \
                       f"нажмите подписаться на запрос. \n " \
                       f"{link} "
    await message.answer(link_message,
                         reply_markup=add_subscribe_keyboard({"site": KufarHandlerChain.site_name(),
                                                              'query_id': query_id})
                         )
