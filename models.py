""" Classes """
from typing import List

import aiohttp

from config import crypto_api_token, crypto_api_url


class CryptoApi:

    crypto_api_token = crypto_api_token
    crypto_api_url = crypto_api_url

    async def get_price(
        self,
        crypto_name: str = 'BTC',
        convert_output_names: List[str] = ['RUB', 'USD'],
    ) -> str:
        output_names = ','.join(map(str, convert_output_names))

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.crypto_api_url}'
                f'fsym={crypto_name}'
                f'&tsyms={output_names}'
                f'&{self.crypto_api_token}'
            ) as response:
                return await response.text()
