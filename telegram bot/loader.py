from os import getenv
from sys import exit
import pathlib
import logging

from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram import Bot, Dispatcher

logging.basicConfig(level=logging.INFO)
bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(bot_token)
dp = Dispatcher(bot, storage=JSONStorage(pathlib.Path("app/storage.json")))
