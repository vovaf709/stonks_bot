from aiogram.types import Message


class ApiException(Exception):
    """Exception raised for various API errors"""

    def __init__(self, error_msg: str):
        super().__init__(error_msg)


def catch_and_send(bot, exception: Exception):
    def wrapper(func):
        async def inner(message: Message):
            try:
                return await func(message)
            except exception as e:
                await bot.send_message(message.chat.id, e)

        return inner

    return wrapper
