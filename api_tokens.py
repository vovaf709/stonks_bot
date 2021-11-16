import os


def on_heroku():
    return 'DYNO' in os.environ

crypto_api_token = os.environ['CRYPTO_TOKEN']
crypto_coinmarketcap_api_token = os.environ['COIN_TOKEN']
stock_api_token = os.environ['STOCK_TOKEN']
DATABASE_URL = os.environ['DATABASE_URL']
REDIS_URL = os.environ['REDIS_URL']
if on_heroku():
    bot_api_token = os.environ['BOT_TOKEN']
else:
    bot_api_token = os.environ['DEV_BOT_TOKEN']
