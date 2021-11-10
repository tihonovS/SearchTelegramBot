import asyncio

import aioschedule
from aiogram import Bot
from aiogram.dispatcher import FSMContext

from app import chain


class Scheduler:
    def __init__(self, bot: Bot, handler: chain.AbstractHandlerChain):
        self.job_map = {}
        self.bot = bot
        self.handler = handler

    async def run(self, chat_id, state: FSMContext):
        if chat_id not in self.job_map:
            job = aioschedule.every(5).seconds.do(chain.call_chain, chat_id, self.handler, state)
            self.job_map[chat_id] = job
            await self.bot.send_message(chat_id, "you have subscribed")
            while True:
                await aioschedule.run_pending()
                await asyncio.sleep(1)
        else:
            await self.bot.send_message(chat_id, "you have already subscribed")

    async def stop(self, chat_id):
        job_map = self.job_map
        if chat_id in job_map:
            aioschedule.cancel_job(job_map[chat_id])
        await self.bot.send_message(chat_id, "scheduler stopped")
