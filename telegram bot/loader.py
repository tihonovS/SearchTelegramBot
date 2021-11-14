from os import getenv
from sys import exit
import pathlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.utils.callback_data import CallbackData

from app.storage.custom_json_storage import CustomJSONStorage

logging.basicConfig(level=logging.INFO)
bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(bot_token)
dp = Dispatcher(bot, storage=CustomJSONStorage(pathlib.Path("app/storage/storage.json")))

callback_numbers = CallbackData("fabnum", "action")
