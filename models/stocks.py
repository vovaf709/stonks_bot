""" Stocks Classes """

import aiohttp

from api_tokens import stock_api_token
from config import stock_api_url


class StocksApi:

    stock_api_token = stock_api_token
    stock_api_url = stock_api_url

    async def get_price(self, stock_name: str = 'AAPL'):

        template = 'quote?'

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.stock_api_url}'
                f'{template}'
                f'&symbol={stock_name}'
                f'&token={self.stock_api_token}'
            ) as response:
                info = await response.json()

                return {'name': stock_name, 'price': f'{info["c"]} USD'}
                """ c
                    Current price

                    d
                    Change

                    dp
                    Percent change

                    h
                    High price of the day

                    l
                    Low price of the day

                    o
                    Open price of the day

                    pc
                    Previous close price"""
