from datetime import datetime
from typing import Optional

from aiogram import Bot

import app.chain as abstract_chain


class OnlinerCatalogHandlerChain(abstract_chain.AbstractHandlerChain):

    def __init__(self, bot: Optional[Bot]):
        self.bot = bot

    @staticmethod
    def site_name():
        return "catalog.onliner.by"

    async def search_request(self, query, date: datetime = None) -> list:
        pass