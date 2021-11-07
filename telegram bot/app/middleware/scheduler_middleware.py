from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from ..middleware.scheduler import Scheduler


class SchedulerMiddleware(BaseMiddleware):

    def __init__(self, scheduler: Scheduler):
        super().__init__()
        self.scheduler = scheduler

    async def on_pre_process_message(self, message: Message, data: dict):
        data["scheduler"] = self.scheduler
