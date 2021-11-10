import operator

from aiogram import Bot

import app.chain as abstract_chain


class KufarHandlerChain(abstract_chain.AbstractHandlerChain):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def handle(self, request: dict, chat_id):
        if "kufar" in request:
            kufar_array = request.get("kufar")
            for kufar in kufar_array:
                link = await self.search_request(kufar.get("query"))
                if link:
                    await self.bot.send_message(chat_id, link)
        await super().handle(request, chat_id)

    async def search_request(self, query):
        response = await super().get_request(
            "https://cre-api-v2.kufar.by/items-search/v1/engine/v1/search/rendered-paginated",
            {'rgn': "7", 'ot': "1", 'query': query, 'size': "42", 'lang': "ru"}
        )
        json_ads_ = response['ads']
        sorted_json = sorted(json_ads_, key=operator.itemgetter('list_time'), reverse=True)
        if len(sorted_json) > 0:
            return sorted_json[0]['ad_link']
        else:
            return ""
