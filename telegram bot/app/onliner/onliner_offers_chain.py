from datetime import datetime
from typing import Optional
import operator

from aiogram import Bot

import app.chain as abstract_chain


class OnlinerOffersHandlerChain(abstract_chain.AbstractHandlerChain):

    @staticmethod
    def action_name():
        return "onl_o"

    def __init__(self, bot: Optional[Bot]):
        self.bot = bot

    @staticmethod
    def site_name():
        return "onliner.by объявления"

    async def search_request(self, query, date: datetime = None) -> list:
        saved_time = datetime.now()
        datetime_format = '%Y-%m-%dT%H:%M:%S+03:00'
        if not date:
            saved_time = datetime.now()
        if isinstance(date, str):
            saved_time = datetime.strptime(date, datetime_format)

        response = await super().get_request(
            "https://catalog.onliner.by/sdapi/catalog.api/search/mobile/second-offers",
            {'mfr[0]': query, 'segment': "second", 'group': 1}
        )
        response_elements = response['offers']
        if len(response_elements) > 0:
            result = []
            for elem in response_elements:
                response_time = datetime.strptime(elem.get('last_up_at'), datetime_format)
                if saved_time < response_time:
                    result.append(self._search_request_object(response_time, elem.get('html_url')))
            if len(result) > 0:
                sorted(result, key=operator.itemgetter('time'), reverse=True)
                return result
            elif not date:
                last_response_elem = response_elements[0]
                response_time = datetime.strptime(last_response_elem.get('last_up_at'), datetime_format)
                return [self._search_request_object(response_time, last_response_elem.get('html_url'))]
        else:
            if not date:
                return [self._search_request_object(saved_time)]
            return []

    @classmethod
    def _search_request_object(cls, time, url=None):
        return {'time': time.isoformat(), 'link': url}
