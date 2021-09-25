import logging
import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message
from aiogram.types import ParseMode
from aiogram.utils.executor import start_webhook

from api_tokens import bot_api_token, on_heroku
from exceptions import ApiException, catch_and_send
from layout import format_output
from models.crypto import (
    CoinMarketApi,
    CryptoApi,
)
from models.stocks import StocksApi


bot = Bot(bot_api_token, parse_mode=ParseMode.HTML)
dispatcher = Dispatcher(bot)
crypto_api = CryptoApi()
stocks_api = StocksApi()
coin_market_api = CoinMarketApi()


@dispatcher.message_handler(commands=['start', 'help'])
async def send_greeting(message: Message):
    """Sends greeting to user with useful tip for life"""
    await bot.send_message(message.chat.id, 'Здарова! Совет дня: инвестируй в крипту')


@dispatcher.message_handler(commands=['crypto'])
@catch_and_send(bot, ApiException)
async def send_crypto(message: Message):
    """Sends crypt price"""
    splitted = message['text'].split()

    if len(splitted) == 1:
        await bot.send_message(message.chat.id, 'Please specify cryptocurrency')
        return

    if len(splitted) > 2:
        raise ApiException('Multiple cryptocurrencies are not supported yet :(')

    crypto_name = splitted[-1]
    crypto_price = await crypto_api.get_price(crypto_name=crypto_name)

    await bot.send_message(message.chat.id, format_output(crypto_price))


@dispatcher.message_handler(commands=['stock'])
@catch_and_send(bot, ApiException)
async def send_stock(message: Message):
    """Sends stock price"""
    splitted = message['text'].split()

    if len(splitted) == 1:
        await bot.send_message(message.chat.id, 'Please specify stock')
        return

    if len(splitted) > 2:
        raise ApiException('Multiple stocks are not supported yet :(')

    stock_name = splitted[-1]
    stock_price = await stocks_api.get_price(stock_name)

    await bot.send_message(message.chat.id, format_output(stock_price))


@dispatcher.message_handler(commands=['coins'])
async def send_few_coins_price(message: Message):
    """Sends stock price"""
    coins = await coin_market_api.few_coins()
    await bot.send_message(message.chat.id, format_output(coins))


# @dispatcher.message_handler(commands=['gl'])
# async def send_crypto_gainers_losers(message: Message):
#    """Sends stock price"""
#    gainers_losers = await coin_market_api.gainers_losers()
#    await bot.send_message(message.chat.id, gainers_losers)


# @dispatcher.message_handler(commands=['allcoins'])
# async def send_all_coins_prices(message: Message):
#     """Sends stock price"""
#     all_coins = await coin_market_api.gainers_losers()
#     await bot.send_message(message.chat.id, gainers_losers)


async def on_startup(dp):
    logging.info('Starting up..')
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logging.info('Lets go!')


async def on_shutdown(dp):
    logging.info('Shutting down..')
    logging.info('Bye!')


if __name__ == '__main__':
    if on_heroku():
        PROJECT_NAME = os.environ['PROJECT_NAME']

        # Domain name or IP addres which your bot is located.
        WEBHOOK_URL = f'https://{PROJECT_NAME}.herokuapp.com/'
        WEBAPP_HOST = '0.0.0.0'
        WEBAPP_PORT = os.environ['PORT']
    else:
        # For local start specify https url from ngrok
        WEBHOOK_URL = 'https://6337-95-25-66-88.ngrok.io'
        WEBAPP_HOST = '0.0.0.0'
        WEBAPP_PORT = 5005

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    WEBHOOK_PATH = ""

    start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
