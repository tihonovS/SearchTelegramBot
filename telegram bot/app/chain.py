from abc import ABC, abstractmethod
from aiogram import Bot
import aiohttp
from aiogram.dispatcher import FSMContext
from datetime import datetime
from app.utils.util import get_query_from_storage

from app.storage.custom_json_storage import CustomJSONStorage
from loader import bot


class AbstractHandlerChain(ABC):

    @abstractmethod
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    @abstractmethod
    def site_name():
        pass

    @staticmethod
    @abstractmethod
    def action_name():
        """короткое имя для колбэков 5 символов"""
        pass

    @abstractmethod
    async def search_request(self, query, date: datetime = None) -> list:
        """
        :param query:
        :param date:
        :return: {"time": ***, "link": ***}
        """
        pass

    async def add_query_to_storage(self, query: str, state: FSMContext) -> str:
        data = await state.get_data()
        site_ = data['site']
        query_id = data['last_query_id']
        # нужно добавить обязательный параметр query и query_id
        if self.site_name() in site_:
            site_.get(self.site_name()).append({"query": query, "query_id": query_id})
        else:
            site_.update({self.site_name(): [{"query": query, "query_id": query_id}]})

        await state.set_data(data)
        return query_id

    async def get_request(self, query: str, params=None) -> dict:
        if params is None:
            params = {}
        async with aiohttp.ClientSession() as session:
            resp = await session.get(query, params=params)
            if resp.status == 200:
                return await resp.json()

    async def handle(self, storage: CustomJSONStorage, chat_id, user_id):
        request = await storage.get_data(chat=chat_id, user=user_id)
        site_ = request['site']
        if self.site_name() in site_:
            site_array = site_.get(self.site_name())
            for kufar in site_array:
                if "subscribed" in kufar:
                    site_request = await self.search_request(kufar.get("query"), kufar.get('last_request_time'))
                    if site_request:
                        kufar['last_request_time'] = site_request[0].get('time')
                        for item in site_request:
                            if 'link' in item:
                                await self.bot.send_message(chat_id, item.get('link'))

            await storage.set_data(chat=chat_id, user=user_id, data=request)
        return None

    async def get_last_query(self, query_id, query, state: FSMContext):
        storage = await state.get_data()
        request = await self.search_request(query)
        if request:
            query = get_query_from_storage(storage, query_id)
            last_request = request[0]
            query['last_request_time'] = last_request.get('time')
            await state.set_data(storage)
            if 'link' in last_request:
                return last_request.get('link')


async def call_chain(chat_id, user_id, storage: CustomJSONStorage):
    for clazz in AbstractHandlerChain.__subclasses__():
        await clazz(bot).handle(storage, chat_id, user_id)

