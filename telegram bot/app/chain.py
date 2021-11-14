from aiogram.dispatcher import FSMContext
from abc import ABC, abstractmethod
from aiogram import Bot
import aiohttp


class AbstractHandlerChain(ABC):
    _next_handler = None
    _session: aiohttp.ClientSession() = aiohttp.ClientSession()

    @abstractmethod
    def __init__(self, bot: Bot):
        self.bot = bot

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, state: FSMContext, chat_id):
        if self._next_handler:
            return await self._next_handler.handle(state, chat_id)

        return None

    @staticmethod
    @abstractmethod
    def site_name():
        pass

    async def get_request(self, query: str, params=None) -> dict:
        if params is None:
            params = {}
        async with self._session.get(query, params=params) as resp:
            if resp.status == 200:
                return await resp.json()


async def call_chain(chat_id, handler: AbstractHandlerChain, state: FSMContext):
    await handler.handle(state, chat_id)
