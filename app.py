# source venv/Scripts/activate
# ctrl + B                        -  запуск скрипта из любого файла проекта
# ctrl + I                        -  варианты эмодзи

import logging

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(level=logging.INFO, format='  -  [%(asctime)s] #%(levelname)-5s -  %(name)s:%(lineno)d  -  %(message)s')
logger = logging.getLogger(__name__)

# Настраиваем логгер для SQLAlchemy
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging.INFO)  # Устанавливаем нужный уровень (например, INFO)
sqlalchemy_logger.propagate = True  # Отключаем передачу сообщений основному логгеру, чтобы не задваивать их

import asyncio
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.strategy import FSMStrategy
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode  # импорт типов разметки сообщений для бота
from aiogram.utils.i18n import ConstI18nMiddleware, I18n
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config_data.config import Config, load_config

from handlers import other, admin, product, donat, group, start
from common.comands import private, admin_private
from database.models import Base
from middlewares import counter, db

# Устанавливаем политику событийного цикла для Windows
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Загружаем конфиг в переменную config
config: Config = load_config()


logger.info('Создаем объект Bot')
bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.owner = config.tg_bot.owner
bot.admin_list = config.tg_bot.admin_list
bot.home_group = config.tg_bot.home_group


logger.info('Инициализация диспетчера')
dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)
# USER_IN_CHAT  -  для каждого юзера, в каждом чате ведется своя запись состояний (по дефолту)
# GLOBAL_USER  -  для каждого юзера везде ведется своё состояние

dp.update.outer_middleware(counter.CounterMiddleware())

dp.include_router(start.start_router)
dp.include_router(admin.admin_router)
dp.include_router(product.product_router)
dp.include_router(donat.donat_router)
dp.include_router(group.group_router)
dp.include_router(other.other_router)

i18n = I18n(path="locales", default_locale="ru", domain="bot_00_template")
dp.update.middleware(ConstI18nMiddleware(locale='ru', i18n=i18n))


logger.info('База данных')
engine = create_async_engine(config.db.db_post, echo=False)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

dp.update.middleware(db.DataBaseSession(session_pool=session_maker))



# Главная функция конфигурирования и запуска бота
async def main() -> None:

    # Удаление предыдущей версии базы, и создание новых таблиц заново
    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    # Удаляем вебхуки (то что бот получил пока спал)
    await bot.delete_webhook(drop_pending_updates=True)

    # Удаляем ранее установленные команды для бота во всех личных чатах
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())

    # Добавляем свои команды
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())

    for admin_id in bot.admin_list:
        await bot.set_my_commands(commands=admin_private, scope=types.BotCommandScopeChat(chat_id=admin_id))


    # Запускаем polling
    try:
        await dp.start_polling(bot,
                               allowed_updates=dp.resolve_used_update_types(),)  # Отбираем только используемые события по роутерам
                            #    skip_updates=False)  # Если бот будет обрабатывать платежи или другие важные вещи, НЕ пропускаем обновления!
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
