import operator
from datetime import datetime
from aiogram import Bot

import app.chain as abstract_chain
from app.storage.custom_json_storage import CustomJSONStorage


class KufarHandlerChain(abstract_chain.AbstractHandlerChain):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def site_name():
        return "kufar.by"

    async def handle(self, storage: CustomJSONStorage, chat_id, user_id):
        request = await storage.get_data(chat=chat_id, user=user_id)
        if "kufar" in request:
            kufar_array = request.get("kufar")
            for kufar in kufar_array:
                if "subscribed" in kufar:
                    kufar_request = await self.search_request(kufar.get("query"), kufar.get('last_request_time'))
                    if kufar_request:
                        kufar['last_request_time'] = kufar_request[0].get('time')
                        for item in kufar_request:
                            await self.bot.send_message(chat_id, item.get('link'))

            await storage.set_data(chat=chat_id, user=user_id, data=request)
        await super().handle(storage, chat_id, user_id)

    async def search_request(self, query, date: datetime) -> list:
        saved_time = datetime.now()
        if not date:
            saved_time = datetime.now()
        if isinstance(date, str):
            saved_time = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

        response = await super().get_request(
            "https://cre-api-v2.kufar.by/items-search/v1/engine/v1/search/rendered-paginated",
            {'rgn': "7", 'ot': "1", 'query': query, 'size': "42", 'lang': "ru"}
        )
        response_elements = response['ads']
        if len(response_elements) > 0:
            result = []
            for elem in response_elements:
                response_time = datetime.strptime(elem.get('list_time'), '%Y-%m-%dT%H:%M:%SZ')
                if saved_time < response_time:
                    result.append({'time': response_time, 'link': elem.get('ad_link')})
            if len(result) > 0:
                sorted(result, key=operator.itemgetter('time'), reverse=True)
                return result
            elif not date:
                last_response_elem = sorted(response_elements, key=operator.itemgetter('list_time'), reverse=True)[0]
                return [{'time': last_response_elem.get('list_time'), 'link': last_response_elem.get('ad_link')}]
        else:
            return []
