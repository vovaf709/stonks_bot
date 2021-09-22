import logging
import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

from api_tokens import bot_api_token
from models.crypto import (
    CoinMarketApi,
    CryptoApi,
)
from models.stocks import StocksApi


PROJECT_NAME = os.getenv('PROJECT_NAME', 'aiogram-example')  # Set it as you've set TOKEN env var
WEBHOOK_HOST = (
    f'https://{PROJECT_NAME}.herokuapp.com/'  # Domain name or IP addres which your bot is located.
)
WEBHOOK_PATH = ""  # Part of URL

WEBHOOK_URL = WEBHOOK_HOST
# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = os.getenv('PORT')

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


# if __name__ == '__main__':
#     executor.start_polling(dispatcher)


async def on_startup(dp):
    logging.warning('Starting up..')

    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start
    logging.warning('Lets go!')


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
    # Create aiohttp.web.Application with configured route for webhook path
    # app = get_new_configured_app(dispatcher=dispatcher, path=WEBHOOK_URL_PATH)
    # # Setup event handlers.
    # app.on_startup.append(on_startup)
    # app.on_shutdown.append(on_shutdown)
    # dispatcher.loop.set_task_factory(context.task_factory)
    # print('lets go')
    # web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    # Heroku stores port you have to listen in your ap
    # web.run_app(app, host='0.0.0.0', port=os.getenv('PORT'))
    # Heroku stores port you have to listen in your ap