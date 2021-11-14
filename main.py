import logging
import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message
from aiogram.types import ParseMode
from aiogram.utils.executor import start_webhook

from api_tokens import bot_api_token, on_heroku, DATABASE_URL
from exceptions import ApiException, catch_and_send
from layout import format_output
from models.crypto import (
    CoinMarketApi,
    CryptoApi,
)
from models.stocks import StocksApi

import psycopg2
from psycopg2 import Error
from db_work import insert_stock, select_stocks, select_stocks_filter


logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    # Connect to an existing database
    connection = psycopg2.connect(DATABASE_URL)

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    logging.info("Successful connecting to PostgreSQL")
except (Exception, Error) as error:
    logging.info("Error while connecting to PostgreSQL", error)

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


@dispatcher.message_handler(commands=['wallet'])
@catch_and_send(bot, ApiException)
async def wallet(message: Message):
    """Sends stock price"""
    splitted = message['text'].split()

    # Return all wallet
    if len(splitted) == 1:
        # await bot.send_message(message.chat.id, 'Please specify stock ticker to add in wallet')
        records = select_stocks(cursor)
        await bot.send_message(message.chat.id, records) 

    elif len(splitted) > 2:
        raise ApiException('Multiple stock tickers are not supported yet :(')

   
    elif len(splitted) == 2:
         # Add new ticker in wallet
        stock_ticker = splitted[-1]
        result = insert_stock(connection, cursor, stock_ticker)
        if result:
            await bot.send_message(message.chat.id, "New ticker saved in wallet")
        else:
            logging.info("Something happened during inserting")
            await bot.send_message(message.chat.id, "Something happened during inserting")


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
    await bot.set_webhook(WEBHOOK_URL)#, drop_pending_updates=True)
    logging.info('Lets go!')


async def on_shutdown(dp):
    logging.info('Shutting down..')
    if (connection):
        cursor.close()
        connection.close()
        logging.info("PostgreSQL connection is closed")
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
        WEBHOOK_URL = 'https://e346-109-252-81-136.ngrok.io'
        WEBAPP_HOST = '0.0.0.0'
        WEBAPP_PORT = 5000

        # logger.setLevel(logging.DEBUG)

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

