from typing import Dict, Union

from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import hbold, hitalic


EMOJI_POINT = ':point_right:'
EMOJI_RED = ':red_circle:'
EMOJI_GREEN = ':green_circle:'


def format_output(data: Union[Dict, str, None]):
    if data is None:
        return None

    message = ""
    if isinstance(data, dict):
        for key, val in data.items():
            message += f'\n{hitalic(key)}'
            message += format_output(val)
    else:
        if '%' == str(data)[-1]:
            emoji_color = EMOJI_RED if float(data[:-1]) < 0 else EMOJI_GREEN
        else:
            emoji_color = ""
        message += f'{EMOJI_POINT} {hbold(data)} {emoji_color}'

    return emojize(message)
