""" Crypto Classes """
import logging
from typing import Dict, List

import aiohttp

from api_tokens import crypto_api_token, crypto_coinmarketcap_api_token
from config import crypto_api_url, crypto_coinmarketcap_api_url
from exceptions import ApiException
from models.interfaces import ExternalApi


# TODO: decide which cryptocurrency API to use
class CryptoApi(ExternalApi):

    crypto_api_token = crypto_api_token
    crypto_api_url = crypto_api_url
    CRYPTO_ERROR_MSG = 'Something went wrong. Are you sure that such a cryptocurrency exists?'

    async def get_price(self, crypto_name: str, convert_output_names: List[str] = ['RUB', 'USD']):
        output_names = ','.join(map(str, convert_output_names))

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.crypto_api_url}'
                f'fsym={crypto_name}'
                f'&tsyms={output_names}'
                f'&api_key={self.crypto_api_token}'
            ) as response:
                return self.process_response(await response.json())

    def process_response(self, data: Dict):
        if data.get('Response') == 'Error':
            logging.exception(data)
            raise ApiException(self.CRYPTO_ERROR_MSG)
        return data


class CoinMarketApi:

    crypto_coinmarketcap_api_token = crypto_coinmarketcap_api_token
    crypto_coinmarketcap_api_url = crypto_coinmarketcap_api_url

    async def return_data(self, headers, params, template):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                f'{self.crypto_coinmarketcap_api_url}{template}', params=params
            ) as response:
                return await response.json()

    async def gainers_losers(self, convert="RUB", start=1, limit=20, time_period="24h"):

        template = 'cryptocurrency/trending/gainers-losers'
        headers = {'X-CMC_PRO_API_KEY': self.crypto_coinmarketcap_api_token}
        params = {'start': start, 'limit': limit, 'convert': convert}

        return await self.return_data(headers, params, template)

    async def all_coins(self, convert="RUB", start=1, limit=20, time_period="24h"):

        template = 'cryptocurrency/trending/gainers-losers'
        headers = {'X-CMC_PRO_API_KEY': self.crypto_coinmarketcap_api_token}
        params = {'start': start, 'limit': limit, 'convert': convert}

        return await self.return_data(headers, params, template)

    async def few_coins(self, symbol='BTC,ETH', convert="RUB"):

        template = 'cryptocurrency/quotes/latest'
        headers = {'X-CMC_PRO_API_KEY': self.crypto_coinmarketcap_api_token}
        params = {'convert': convert, 'symbol': symbol}

        response = await self.return_data(headers, params, template)
        answer = {}
        for key, value in response['data'].items():
            answer[key] = {
                "price": f"{int(value['quote'][convert]['price'])} RUB",
                "24h_change": f"{round(value['quote'][convert]['percent_change_24h'], 2)}%",
                "7d_change": f"{round(value['quote'][convert]['percent_change_7d'], 2)}%",
            }
        return answer
