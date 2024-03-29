from datetime import datetime
from typing import Optional
import operator
import re

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
        if not date:
            saved_time = datetime.now()
        if isinstance(date, str):
            saved_time = datetime.fromisoformat(date)
        search = re.search(r"/(\w+)$", query)
        if search:
            response = await super().get_request(
                "https://catalog.onliner.by/sdapi/second.api/product/" + search.group(1) + "/offers",
            )
            if response:
                response_elements = response['offers']
                if len(response_elements) > 0:
                    result = []
                    datetime_format = '%Y-%m-%dT%H:%M:%S+03:00'
                    for elem in response_elements:
                        response_time = datetime.strptime(elem.get('last_up_at'), datetime_format)
                        if saved_time < response_time:
                            result.append(self._search_request_object(response_time,
                                                                      query + "/used/" + str(elem.get('id')))
                                          )
                    if len(result) > 0:
                        sorted(result, key=operator.itemgetter('time'), reverse=True)
                        return result
                    elif not date:
                        last_response_elem = response_elements[0]
                        response_time = datetime.strptime(last_response_elem.get('last_up_at'), datetime_format)
                        return [self._search_request_object(response_time,
                                                            query + "/used/" + str(last_response_elem.get('id')))
                                ]
                else:
                    if not date:
                        return [self._search_request_object(saved_time)]
                    return []

    @classmethod
    def _search_request_object(cls, time, url=None):
        return {'time': time.isoformat(), 'link': url}
