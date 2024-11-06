import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from typing import Any
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from database.orm_users import orm_get_locale


# Класс LocaleFromDBMiddleware, наследуемый от BaseMiddleware, предназначен для определеня локали из бд, и передачи ее в FSMContext
class LocaleFromDBMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        # logger.info("class LocaleFromDBMiddleware __init__")

    async def __call__(self, handler, event: TelegramObject, data: dict) -> Any:
        # logger.info("class LocaleFromDBMiddleware __call__")
        try:
            # Проверяем, есть ли локаль в FSM
            fsm_context = data.get("state")
            fsm_data = await fsm_context.get_data()
            current_locale = fsm_data.get("locale")

            # Если локаль уже есть в FSM, передаем обработку дальше
            if current_locale:
                # logger.info("Локаль уже установлена в FSM: %s", current_locale)
                return await handler(event, data)

            # Получаем сессию БД
            session = data.get("session")
            if not session:
                logger.error("Сессия БД не найдена в middleware - LocaleFromDBMiddleware.")
                return await handler(event, data)

            # Проверяем, является ли событие сообщением от пользователя
            if hasattr(event, 'message') and hasattr(event.message, 'from_user'):
                user_id = event.message.from_user.id
                locale = await orm_get_locale(session, user_id)

                # Если локаль найдена, устанавливаем ее в FSMContext
                if locale:
                    logger.info("Установлена локаль '%s' для пользователя %s", locale, user_id)
                    await fsm_context.update_data(locale=locale)

            # Передаем обработку дальше
            return await handler(event, data)

        except Exception as e:
            logger.exception("Ошибка в middleware CustomI18nMiddleware: %s", str(e))
