""" Crypto Classes """
from typing import List

import aiohttp

from api_tokens import crypto_api_token
from config import crypto_api_url  # noqa TODO: fix flake8 configuration


class CryptoApi:

    crypto_api_token = crypto_api_token
    crypto_api_url = crypto_api_url

    async def get_price(
        self,
        crypto_name: str = 'BTC',
        convert_output_names: List[str] = ['RUB', 'USD'],
    ):
        output_names = ','.join(map(str, convert_output_names))

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.crypto_api_url}'
                f'fsym={crypto_name}'
                f'&tsyms={output_names}'
                f'&api_key={self.crypto_api_token}'
            ) as response:
                return await response.json()
