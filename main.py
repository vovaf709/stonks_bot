import logging
import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message
from aiogram.types import ParseMode
from aiogram.utils.executor import start_webhook

from api_tokens import bot_api_token, on_heroku, DATABASE_URL, REDIS_URL
from exceptions import ApiException, catch_and_send
from layout import format_output
from models.crypto import (
    CoinMarketApi,
    CryptoApi,
)
from models.stocks import StocksApi

# import psycopg2
# from psycopg2 import Error
# from db_work import insert_stock, select_stocks, select_stocks_filter, delete_stock
# import websocket
from api_tokens import stock_api_token
import redis
import asyncio
from websockets import connect
import json
# import redis_work
from websockets.exceptions import ConnectionClosedOK
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# try:
#     # Connect to an existing database
#     connection = psycopg2.connect(DATABASE_URL)

#     # Create a cursor to perform database operations
#     cursor = connection.cursor()
#     logging.info("Successful connecting to PostgreSQL")
# except (Exception, Error) as error:
#     logging.info("Error while connecting to PostgreSQL", error)

try:
    redis = redis.from_url(REDIS_URL)
except (Exception, Error) as error:
    logging.info("Error while connecting to Redis", error)



bot = Bot(bot_api_token, parse_mode=ParseMode.HTML)
dispatcher = Dispatcher(bot)
crypto_api = CryptoApi()
stocks_api = StocksApi()
coin_market_api = CoinMarketApi()

# def on_message(ws, message):
#     print(message)

# def on_error(ws, error):
#     print(error)

# def on_close(ws):
#     print("### closed ###")

# def on_open(ws):
#     ws.send('{"type":"subscribe","symbol":"AAPL"}')
#     # ws.send('{"type":"subscribe","symbol":"AMZN"}')
#     # ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
#     # ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')

# websocket.enableTrace(True)
# ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={stock_api_token}",
#                           on_message = on_message,
#                           on_error = on_error,
#                           on_close = on_close)
# ws.on_open = on_open



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

# Add remove alert 
@dispatcher.message_handler(commands=['alert'])
@catch_and_send(bot, ApiException)
async def create_alert(message: Message):
    """Sends stock price"""
    splitted = message['text'].split()

    if len(splitted) == 3:
        stock_name = splitted[1]
        info = await stocks_api.get_lookup(stock_name)
        if info:
            if redis.sismember('stocks', info['ticker']) and not redis.sismember('alerts', info['ticker']):
                some = redis.get(info['ticker'] + "_price")
                if not some:
                    await bot.send_message(message.chat.id, "For some reason we dont have price and cant set alert")
                    return 
                price = float(some)
                if price:
                    alert_price = float(splitted[2])
                    if float(price) < alert_price:
                        redis.rpush(info['ticker'] + "_alert", 1) # Alert more than current price
                        redis.rpush(info['ticker'] + "_alert", alert_price)

                    else:
                        redis.rpush(info['ticker'] + "_alert", 0) # Alert less than current price
                        redis.rpush(info['ticker'] + "_alert", alert_price)
                    redis.sadd('alerts', info['ticker'])
                    await bot.send_message(message.chat.id, f"Allert: {info}, price: {price}, alert: {alert_price}")

                else:
                    await bot.send_message(message.chat.id, "For some reason we dont have price and cant set alert")
            else:
                await bot.send_message(message.chat.id, f"We didnt find this stock: {info} in wallet or it already in alerts")
        else:
            await bot.send_message(message.chat.id, "We didnt find something close to this name")

    else:
        await bot.send_message(message.chat.id, 'Please specify stock and alert price')
        # raise ApiException('Multiple stocks are not supported yet :(')


# Add remove alert 
@dispatcher.message_handler(commands=['alert_r'])
@catch_and_send(bot, ApiException)
async def remove_alert(message: Message):
    """Sends stock price"""
    splitted = message['text'].split()

    if len(splitted) == 2:
        stock_name = splitted[1]
        info = await stocks_api.get_lookup(stock_name)
        if info:
            if redis.sismember('alerts', info['ticker']):
                redis.srem('alerts', info['ticker'])
                redis.delete(info['ticker'] + "_alert")
                await bot.send_message(message.chat.id, f"Allert: {info} deleted")

            else:
                await bot.send_message(message.chat.id, f"We didnt find this stock: {info} in alerts")
      
        else:
            await bot.send_message(message.chat.id, "We didnt find something close to this name")
                
    else:
        await bot.send_message(message.chat.id, 'Please specify stock in alerts to remove it')


@dispatcher.message_handler(commands=['alerts'])
@catch_and_send(bot, ApiException)
async def alerts(message: Message):
    """Sends stock price"""
    splitted = message['text'].split()
    # print(echo)
    # Return all wallet
    if len(splitted) == 1:
        # await bot.send_message(message.chat.id, 'Please specify stock ticker to add in wallet')

        # via redis
        response = []
        for key in redis.smembers('alerts'):
            key_utf = key.decode("utf-8")
            response.append(key_utf)
            
        await bot.send_message(message.chat.id, response) 

    elif len(splitted) > 1:
        raise ApiException('No no')


@dispatcher.message_handler(commands=['wallet'])
@catch_and_send(bot, ApiException)
async def wallet(message: Message):
    """Sends stock price"""
    splitted = message['text'].split()
    # print(echo)
    # Return all wallet
    if len(splitted) == 1:
        # await bot.send_message(message.chat.id, 'Please specify stock ticker to add in wallet')

        # via redis
        records = redis.smembers('stocks')
        data = dict()
        for key in records:
            key = key.decode("utf-8")
            data[key] = redis.get(key + "_price")
        #via postgres
        # records = select_stocks(cursor) # more info then set of tickers in redis
        await bot.send_message(message.chat.id, data) 

    elif len(splitted) > 2:
        raise ApiException('Multiple stock tickers are not supported yet :(')

   
    elif len(splitted) == 2:
         # Add new stock in wallet
        stock_name = splitted[-1]
        info = await stocks_api.get_lookup(stock_name)
        if info:
            # postgres insert
            # result = insert_stock(connection, cursor, name=info['name'], ticker=info['ticker'])
            # redis insert
            result = redis.sadd('stocks', info['ticker'])

            if result:
                req = '{"type":"subscribe","symbol":"' + info['ticker'].upper() + '"}'
                # print(req)
                await echo.send(req)
                await bot.send_message(message.chat.id, f"{info['name']} with ticker: {info['ticker']} saved in wallet")
            else:
                logging.info("Something happened during inserting")
                await bot.send_message(message.chat.id, "Something happened during inserting")
        else:
            await bot.send_message(message.chat.id, "We didnt find something close to this name")

@dispatcher.message_handler(commands=['wallet_r'])
@catch_and_send(bot, ApiException)
async def wallet_r(message: Message):
    """Sends stock price"""
    splitted = message['text'].split()

    # Remove one stock from wallet
   
    if len(splitted) == 2:
         # Remove stock from wallet
        stock_name = splitted[-1]
        info = await stocks_api.get_lookup(stock_name)
        if info:
            # postgres delete
            # result = delete_stock(connection, cursor, name=info['name'], ticker=info['ticker'], count=1)
            # redis delete
            result = redis.srem('stocks', info['ticker'])

            if result:
                await bot.send_message(message.chat.id, f"{info['name']} with ticker: {info['ticker']} removed from wallet")
            else:
                logging.info("Looks like wallet doesnt have it")
                await bot.send_message(message.chat.id, "Looks like wallet doesnt have it")
        else:
            await bot.send_message(message.chat.id, "We didnt find something close to this name")
    else:
        raise ApiException('Send name of stock to remove it from wallet')


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


async def create_foo(settings):
    foo = EchoWebsocket()
    await foo._init()
    # print(foo.websocket)
    # print('end')
    return foo


class EchoWebsocket:
    async def _init(self):
        # print('wo')
        logging.info('connect to websocket')
        self._conn = connect(f"wss://ws.finnhub.io?token={stock_api_token}")
        self.websocket = await self._conn.__aenter__()
        # print(self.websocket)
        # print('socket')

    # async def __aenter__(self):
    #     print("hello")
    #     self._conn = await connect(f"wss://ws.finnhub.io?token={stock_api_token}")
    #     self.websocket = await self._conn.__aenter__()
    #     print('wo')
    #     print('here we go') 
    #     print(self.websocket)       
    #     return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def send(self, message):
        # await asyncio.sleep(5)
        try:
            await self.websocket.send(message)
        except ConnectionClosedOK as e:
            logging.info(e)
            logging.info('reconnect to websocket')

            await self._init()
            await define_stocks(self)

            await self.websocket.send(message)


    async def receive(self):
        try:
            return await self.websocket.recv()
        except ConnectionClosedOK as e:
            logging.info(e)
            logging.info('reconnect to websocket')

            await self._init()
            await define_stocks(self)
            return await self.websocket.recv()



## WARINNG check logic with alerts and in create_alert func
async def get_echo(echo):
    response =  await echo.receive()
    answer = []
    # print(response)
    response = json.loads(response).get('data', [])
    objes = dict()
    tickers_set = set()
    for j in redis.smembers('stocks'):
        tickers_set.add(j.decode("utf-8") )
    for data in response:
        if data['s'] in tickers_set:
            objes[data['s']] = data['p'] # t - timestamp, s - ticker, p - price
    print(objes)
    for key, val in objes.items():
        redis.set(key + "_price", val)

    print('alerts')
    for key in redis.smembers('alerts'):
        # print(key)
        key_utf = key.decode("utf-8")
        # print(key_utf)
        price_alert = redis.lrange(key_utf + "_alert", 0, -1)
        cur_price = objes.get(key_utf, float(redis.get(key_utf + "_price")))
        print(f"cur_price: {cur_price}")
        print(f"price_alert: {price_alert}")
        # print(float(price_alert[1]))
        if price_alert:
            if float(price_alert[1]) < cur_price and price_alert[0].decode("utf-8") == "1": # {key}_price in redis
                # print('we in 1')
                await bot.send_message(-634163567, f"alert {key_utf} {cur_price}") 
                redis.delete(key_utf + "_alert")
                redis.srem('alerts', 1, key_utf)
            elif float(price_alert[1]) > cur_price and price_alert[0].decode("utf-8") == "0":
                # print('we in 2')
                await bot.send_message(-634163567, f"alert {key_utf} {cur_price}")
                redis.delete(key_utf + "_alert")
                redis.srem('alerts', 1, key_utf)
        else:   
            print('strange no price alert but in list of alerts')

    return answer

async def define_stocks(echo):
    # records = select_stocks(cursor)
    tickers_set = set()
    for j in redis.smembers('stocks'):
        tickers_set.add(j.decode("utf-8") )
    # print(redis.smembers('stocks'))
    # tickers_set = set()
    # for j in records:
    #     tickers_set.add(j[1])
    # print(tickers_set)
    # for j in tickers_set:
    #     await echo.send('{"type":"subscribe","symbol":" '+ j +'"}')
    for j in tickers_set:
        # print('{"type":"subscribe","symbol":"' + j.upper() + '"}')
        await echo.send('{"type":"subscribe","symbol":"' + j.upper() + '"}')
    # for j in ticker_set:
        # await echo.send('{"type":"subscribe","symbol":"AAPL"}')



# print(echo)

async def websocket_shit():
    # async with EchoWebsocket() as echo:
        # await echo.send('{"type":"subscribe","symbol":"AAPL"}')
    global echo

    echo = await create_foo("asd")
    # print(echo)
    await define_stocks(echo)
    # await get_echo(echo)
    while True:
        data = await get_echo(echo)
        # await bot.send_message(-634163567, data) # our chat id
        # print(data)

            # print('s')
        # resp = await echo.receive()  # "Hello!"
        # print(resp)
    print('we out')

def _handle_task_result(task: asyncio.Task) -> None:
    try:

        res = task.result()
        print(res)
    except asyncio.CancelledError:
        print('we here after cancel build')
        pass  # Task cancellation should not be logged as an error.
    except Exception:  # pylint: disable=broad-except
        
        logging.exception('Exception raised by task = %r', task)
        print('some shit heppened')
        # restart webhook
        logging.info("Websocket restarting")
        loop = asyncio.get_event_loop()
        my_task = loop.create_task(websocket_shit())
        my_task.add_done_callback(_handle_task_result)
        logging.info("Websocket restarted")


if __name__ == '__main__':
    redis.delete("alerts")
    redis.delete("NVDA_alert")

    if on_heroku():
        logging.info("Websocket starting")
        loop = asyncio.get_event_loop()
        my_task = loop.create_task(websocket_shit())
        my_task.add_done_callback(_handle_task_result)
        logging.info("Websocket started")

        PROJECT_NAME = os.environ['PROJECT_NAME']

        # Domain name or IP addres which your bot is located.
        WEBHOOK_URL = f'https://{PROJECT_NAME}.herokuapp.com/'
        WEBAPP_HOST = '0.0.0.0'
        WEBAPP_PORT = os.environ['PORT']
    else:
        # ATTENTION 
        # websocket_shit create websocket, but cause of api maximum count of live sockets is 1,
        # so this should be turned on only in prod
        # need smart tests with fixtures without actually starting websocket_shit on dev
        # for adding functionality with websockets responses
        
        # logging.info("Websocket starting")
        # loop = asyncio.get_event_loop()
        # my_task = loop.create_task(websocket_shit())
        # my_task.add_done_callback(_handle_task_result)
        # logging.info("Websocket started")
        # For local start specify https url from ngrok
        WEBHOOK_URL = 'https://7726-109-252-81-136.ngrok.io'
        WEBAPP_HOST = '0.0.0.0'
        WEBAPP_PORT = 5000

        # logger.setLevel(logging.DEBUG)

    WEBHOOK_PATH = ""
    # ws.run_forever()

    

    
    # loop.run_until_complete(main())


    start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

