import os

crypto_api_token = os.environ['CRYPTO_TOKEN']
crypto_coinmarketcap_api_token = os.environ['COIN_TOKEN']
stock_api_token = os.environ['STOCK_TOKEN']
if 'DYNO' in os.environ:
	bot_api_token = os.environ['BOT_TOKEN']
else:
	bot_api_token = os.environ['DEV_BOT_TOKEN']
