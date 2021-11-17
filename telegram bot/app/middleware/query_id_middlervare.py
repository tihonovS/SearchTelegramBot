from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware


class QueryIdMiddleware(BaseMiddleware):
    def __init__(self):
        super(QueryIdMiddleware, self).__init__()

    @classmethod
    async def on_post_process_message(cls, message: types.Message, results, data: dict):
        if 'command' in data and data['command'].command == 'add_query':
            state_: FSMContext = data['state']
            storage = await state_.get_data()
            storage['last_query_id'] += 1
            await state_.set_data(storage)
