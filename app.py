import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import ConstI18nMiddleware, I18n
from config_data.config import Config, load_config
from handlers.other import other_router
from handlers.user import user_router

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s')

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main() -> None:

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_router)
    dp.include_router(other_router)

    i18n = I18n(path="locales", default_locale="ru", domain="i18n_example_bot")

    # Здесь будем регистрировать миддлвари
    dp.update.middleware(ConstI18nMiddleware(locale='rr', i18n=i18n))

    # Запускаем polling
    await dp.start_polling(bot)


asyncio.run(main())
