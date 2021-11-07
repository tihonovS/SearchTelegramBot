import asyncio

import aioschedule
from aiogram import Bot
from app.chain.chain import AbstractHandlerChain
from app.chain.chain import call_chain


class Scheduler:
    def __init__(self, bot: Bot, handler: AbstractHandlerChain):
        self.job_map = {}
        self.bot = bot
        self.handler = handler

    async def run(self, chat_id):
        if chat_id not in self.job_map:
            job = aioschedule.every(5).seconds.do(call_chain, chat_id, self.handler)
            self.job_map[chat_id] = job
            await self.bot.send_message(chat_id, "you have subscribed")
            while True:
                await aioschedule.run_pending()
                await asyncio.sleep(1)
        else:
            await self.bot.send_message(chat_id, "you have already subscribed")

    async def stop(self, chat_id):
        await self.bot.send_message(chat_id, "scheduler stopped")
        aioschedule.cancel_job(self.job_map[chat_id])
