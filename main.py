from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from api_tokens import bot_api_token
from models.crypto import (
    CoinMarketApi,
    CryptoApi,
)
from models.stocks import StocksApi


bot = Bot(bot_api_token)
dispatcher = Dispatcher(bot)
crypto_api = CryptoApi()
stocks_api = StocksApi()
coin_market_api = CoinMarketApi()


@dispatcher.message_handler(commands=['start', 'help'])
async def send_greeting(message: types.Message):
    """Sends greeting to user"""
    await bot.send_message(message.chat.id, 'Здарова! Совет дня: инвестируй в крипту')


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


@dispatcher.message_handler(commands=['gl'])
async def send_crypto_gainers_losers(message: types.Message):
    """Sends stock price"""
    gainers_losers = await coin_market_api.gainers_losers()
    await bot.send_message(message.chat.id, gainers_losers)


@dispatcher.message_handler(commands=['coins'])
async def send_few_coins_price(message: types.Message):
    """Sends stock price"""
    coins = await coin_market_api.few_coins()
    await bot.send_message(message.chat.id, coins)


# @dispatcher.message_handler(commands=['allcoins'])
# async def send_all_coins_prices(message: types.Message):
#     """Sends stock price"""
#     all_coins = await coin_market_api.gainers_losers()
#     await bot.send_message(message.chat.id, gainers_losers)


if __name__ == '__main__':
    executor.start_polling(dispatcher)
