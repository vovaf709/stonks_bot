from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from api_tokens import bot_api_token
from models.crypto import CryptoApi  # noqa TODO: fix flake8 configuration
from models.stocks import StocksApi  # noqa TODO: fix flake8 configuration


bot = Bot(bot_api_token)
dispatcher = Dispatcher(bot)
crypto_api = CryptoApi()
stocks_api = StocksApi()


@dispatcher.message_handler(commands=['start', 'help'])
async def send_greeting(message: types.Message):
    """Sends greeting to user"""
    await bot.send_message(
        message.chat.id, 'Здарова! Совет дня: инвестируй в крипту'
    )


@dispatcher.message_handler(commands=['crypt'])
async def send_crypt(message: types.Message):
    """Sends crypt price"""
    crypt_price = await crypto_api.get_price()
    await bot.send_message(message.chat.id, crypt_price)


@dispatcher.message_handler(commands=['stock'])
async def send_stock(message: types.Message):
    """Sends stock price"""
    stock_price = await stocks_api.get_price()
    await bot.send_message(message.chat.id, stock_price)


if __name__ == '__main__':
    executor.start_polling(dispatcher)
