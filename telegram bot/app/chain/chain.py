import operator
from abc import ABC, abstractmethod
from aiogram import Bot
import requests


class AbstractHandlerChain(ABC):
    _next_handler = None

    @abstractmethod
    def __init__(self, bot: Bot):
        self.bot = bot

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, request: dict, chat_id):
        if self._next_handler:
            return await self._next_handler.handle(request, chat_id)

        return None


class KufarHandlerChain(AbstractHandlerChain):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def handle(self, request: dict, chat_id):
        if "kufar" in request:
            kufar_array = request.get("kufar")
            for kufar in kufar_array:
                link = self.search_request(kufar.get("query"))
                if link:
                    await self.bot.send_message(chat_id, link)
        await super().handle(request, chat_id)

    @staticmethod
    def search_request(query):
        response = requests.get("https://cre-api-v2.kufar.by/items-search/v1/engine/v1/search/rendered-paginated",
                                params={'rgn': "7", 'ot': "1", 'query': query, 'size': "42", 'lang': "ru"}
                                )
        json_ads_ = response.json()['ads']
        sorted_json = sorted(json_ads_, key=operator.itemgetter('list_id'))
        if len(sorted_json) > 0:
            return sorted_json[0]['ad_link']
        else:
            return ""


class OnlinerHandlerChain(AbstractHandlerChain):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def handle(self, request: dict, chat_id):
        if "onliner" in request:
            await self.bot.send_message(chat_id, "i'm onliner logic")
        await super().handle(request, chat_id)


def register_chain(bot: Bot):
    first = KufarHandlerChain(bot)
    second = OnlinerHandlerChain(bot)
    first.set_next(second)

    return first


async def call_chain(chat_id, handler: AbstractHandlerChain):
    dictionary = {"932954788": {"kufar": [{"query": "ываы"}, ]}}
    await handler.handle(dictionary.get(str(chat_id)), chat_id)

