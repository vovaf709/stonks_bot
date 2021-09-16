import aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor 

import os


bot = Bot(os.environ['BOT_TOKEN'])
dispatcher = Dispatcher(bot)

@dispatcher.message_handler(commands=['start', 'help'])
async def send_greeting(message: types.Message):
    """Sends greeting to user"""
    await bot.send_message(message.chat.id, 'Здарова! Совет дня: инвестируй в крипту')

if __name__ == '__main__':
    executor.start_polling(dispatcher)