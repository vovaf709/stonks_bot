""" Stocks Classes """
import logging
from typing import Dict

import aiohttp

from api_tokens import stock_api_token
from config import stock_api_url
from exceptions import ApiException
from models.interfaces import ExternalApi


class StocksApi(ExternalApi):

    stock_api_token = stock_api_token
    stock_api_url = stock_api_url
    STOCK_ERROR_MSG = 'Something went wrong. Are you sure that such a stock exists?'

    async def get_price(self, stock_name: str):

        template = 'quote?'

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.stock_api_url}'
                f'{template}'
                f'&symbol={stock_name.upper()}'
                f'&token={self.stock_api_token}'
            ) as response:
                info = self.process_response(await response.json())
                # print("LADLG", info)

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

    async def get_lookup(self, search_string: str):

        template = 'search?'

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.stock_api_url}'
                f'{template}'
                f'&q={search_string}'
                f'&token={self.stock_api_token}'
            ) as response:
                info = self.process_response(await response.json(), param='count')
                if info['count'] > 0:
                    return {"name": info["result"][0]["description"], "ticker": info["result"][0]["symbol"]}
                # else something like error

    def process_response(self, data: Dict, param='d'):
        # TODO: figure out more sophisticated way to identify invalid stock
        if data.get(param) is None:
            logging.exception(data)
            raise ApiException(self.STOCK_ERROR_MSG)
        return data
