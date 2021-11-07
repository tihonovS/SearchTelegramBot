from aiogram import Dispatcher, types


async def send_welcome(message: types.Message):
    # kufar_requests.search_request()
    await message.reply("Hi i'm bot")


def register_init_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'], state="*")
