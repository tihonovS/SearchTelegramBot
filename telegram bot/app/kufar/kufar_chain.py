import operator
from datetime import datetime
from typing import Optional

from aiogram import Bot
from aiogram.dispatcher import FSMContext

import app.chain as abstract_chain
from app.storage.custom_json_storage import CustomJSONStorage
from app.utils.util import get_query


class KufarHandlerChain(abstract_chain.AbstractHandlerChain):
    def __init__(self, bot: Optional[Bot]):
        self.bot = bot

    @staticmethod
    def site_name():
        return "kufar.by"

    async def handle(self, storage: CustomJSONStorage, chat_id, user_id):
        request = await storage.get_data(chat=chat_id, user=user_id)
        site_ = request['site']
        if KufarHandlerChain.site_name() in site_:
            kufar_array = site_.get(KufarHandlerChain.site_name())
            for kufar in kufar_array:
                if "subscribed" in kufar:
                    kufar_request = await self.search_request(kufar.get("query"), kufar.get('last_request_time'))
                    if kufar_request:
                        kufar['last_request_time'] = kufar_request[0].get('time')
                        for item in kufar_request:
                            if 'link' in item:
                                await self.bot.send_message(chat_id, item.get('link'))

            await storage.set_data(chat=chat_id, user=user_id, data=request)
        await super().handle(storage, chat_id, user_id)

    @staticmethod
    async def add_query_to_storage(query: str, state: FSMContext) -> str:
        data = await state.get_data()
        site_ = data['site']
        query_id = data['last_query_id']
        # нужно добавить обязательный параметр query и query_id
        if KufarHandlerChain.site_name() in site_:
            site_.get(KufarHandlerChain.site_name()).append({"query": query, "query_id": query_id})
        else:
            site_.update({KufarHandlerChain.site_name(): [{"query": query, "query_id": query_id}]})

        await state.set_data(data)
        return query_id

    async def get_last_query(self, query_id, query, state: FSMContext):
        storage = await state.get_data()
        request = await self.search_request(query)
        if request:
            query = get_query(storage, query_id)
            last_request = request[0]
            query['last_request_time'] = last_request.get('time')
            await state.set_data(storage)
            if 'link' in last_request:
                return last_request.get('link')

    async def search_request(self, query, date: datetime = None) -> list:
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
                    result.append({'time': response_time.isoformat(), 'link': elem.get('ad_link')})
            if len(result) > 0:
                sorted(result, key=operator.itemgetter('time'), reverse=True)
                return result
            elif not date:
                last_response_elem = sorted(response_elements, key=operator.itemgetter('list_time'), reverse=True)[0]
                response_time = datetime.strptime(last_response_elem.get('list_time'), '%Y-%m-%dT%H:%M:%SZ')
                return [{'time': response_time.isoformat(), 'link': last_response_elem.get('ad_link')}]
        else:
            if not date:
                return [{'time': saved_time.isoformat()}]
            return []
