from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class CustomI18nMiddleware(BaseMiddleware):
    """
    Промежуточный обработчик для интеграции интернационализации.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Вызывается при каждом событии Telegram.
        Передает данные в основной обработчик, предоставляя возможность предварительной обработки.
        :param handler: Основной обработчик, который должен быть вызван.
        :param event: Событие Telegram, которое нужно обработать.
        :param data: Дополнительные данные, доступные обработчику.
        :return: Результат работы основного обработчика.
        """
        return await handler(event, data)
