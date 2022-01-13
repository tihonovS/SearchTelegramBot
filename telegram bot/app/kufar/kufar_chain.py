import operator
from datetime import datetime
from typing import Optional

from aiogram import Bot

import app.chain as abstract_chain


class KufarHandlerChain(abstract_chain.AbstractHandlerChain):
    @staticmethod
    def action_name():
        return "kuf"

    def __init__(self, bot: Optional[Bot]):
        self.bot = bot

    @staticmethod
    def site_name():
        return "kufar.by"

    async def search_request(self, query, date: datetime = None) -> list:
        saved_time = datetime.now()
        if not date:
            saved_time = datetime.now()
        if isinstance(date, str):
            saved_time = datetime.fromisoformat(date)

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
                    result.append(self._search_request_object(response_time, elem.get('ad_link')))
            if len(result) > 0:
                sorted(result, key=operator.itemgetter('time'), reverse=True)
                return result
            elif not date:
                last_response_elem = sorted(response_elements, key=operator.itemgetter('list_time'), reverse=True)[0]
                response_time = datetime.strptime(last_response_elem.get('list_time'), '%Y-%m-%dT%H:%M:%SZ')
                return [self._search_request_object(response_time, last_response_elem.get('ad_link'))]
        else:
            if not date:
                return [self._search_request_object(saved_time)]
            return []

    @classmethod
    def _search_request_object(cls, time, url=None):
        return {'time': time.isoformat(), 'link': url}
