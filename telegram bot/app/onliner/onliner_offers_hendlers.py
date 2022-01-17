from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.onliner.onliner_offers_chain import OnlinerOffersHandlerChain
from app.scheduler import add_subscribe_keyboard, scheduler_resume
from loader import dp, callback_action


class OnlinerOffersState(StatesGroup):
    waiting_for_query = State()


@dp.callback_query_handler(callback_action.filter(action=OnlinerOffersHandlerChain.action_name()))
async def onliner_offers_start(call: types.CallbackQuery, callback_data: dict):
    await call.message.delete_reply_markup()
    await call.message.answer(f"что будем искать на {OnlinerOffersHandlerChain.site_name()}. "
                              f"Для поиска нужно скопировать ссылку на товар. Должна быть открыта вкладка "
                              f"'Описание и фото'")
    await OnlinerOffersState.waiting_for_query.set()
    await call.answer()


@dp.message_handler(state=OnlinerOffersState.waiting_for_query)
async def onliner_offers_query(message: types.Message, state: FSMContext):
    onliner = OnlinerOffersHandlerChain(None)
    query_id = await onliner.add_query_to_storage(message.text, state)
    await state.reset_state(with_data=False)
    link = await onliner.get_last_query(query_id, message.text, state)
    link_message = "По вашему запросу ничего не найдено"
    if link:
        link_message = f"Это последнее из объявлений, которое я нашёл по Вашему запросу, Для того, чтобы продолжить " \
                       f"получать актуальную информацию об объявлениях по запросу {message.text}, " \
                       f"нажмите подписаться на запрос. \n " \
                       f"{link} "
    await message.answer(link_message,
                         reply_markup=add_subscribe_keyboard(query_id)
                         )
    await scheduler_resume(state)

