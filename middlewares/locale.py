import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from typing import Any
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n
from database.orm_users import orm_get_locale



class CustomI18nMiddleware(BaseMiddleware):
    def __init__(self, i18n: I18n):
        super().__init__()
        self.i18n = i18n

    async def __call__(self, handler, event: TelegramObject, data: dict) -> Any:
        # Получаем сессию БД из middleware контекста
        session = data.get("session")
        if not session:
            logger.warning("Сессия БД не найдена в middleware контексте.")
            return await handler(event, data)

        # Проверяем тип апдейта и получаем user_id
        if hasattr(event, 'from_user'):
            user_id = event.from_user.id
            locale = await orm_get_locale(session, user_id)

            # Если locale найден, задаем его для i18n
            if locale:
                logger.info("Установлена локаль '%s' для пользователя %s", locale, user_id)
                data["i18n"] = self.i18n
                data["locale"] = locale
                self.i18n.current_locale.set(locale)

        # Передаем обработку дальше
        return await handler(event, data)
