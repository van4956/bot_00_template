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
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage #, Redis
from redis.asyncio.client import Redis
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.i18n import ConstI18nMiddleware, I18n, SimpleI18nMiddleware, FSMI18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config_data.config import Config, load_config

from handlers import other, admin, product, donat, group, start, owner, aiogram_dialog, FSMtest
from common.comands import private, admin_private
from database.models import Base
from middlewares import counter, db, locale

# Устанавливаем политику событийного цикла для Windows
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем объект хранилища
storage = MemoryStorage()  # хранится исключительно в оперативной памяти, при перезапуске бота все данные стираются (для тестов и разработки)
# redis = Redis(host='localhost')  # инициализируем Redis
# storage = RedisStorage(redis=redis)  # хранится на отдельном сервере

logger.info('Инициализируем бот и диспетчер')
bot = Bot(token=config.tg_bot.token,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML,
                                       link_preview=None,
                                       link_preview_is_disabled=None,
                                       link_preview_prefer_large_media=None,
                                       link_preview_prefer_small_media=None,
                                       link_preview_show_above_text=None))
bot.owner = config.tg_bot.owner
bot.admin_list = config.tg_bot.admin_list
bot.home_group = config.tg_bot.home_group

dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT,
                storage=storage)
# USER_IN_CHAT  -  для каждого юзера, в каждом чате ведется своя запись состояний (по дефолту)
# GLOBAL_USER  -  для каждого юзера везде ведется своё состояние

# Создаем движок бд
engine = create_async_engine(config.db.db_lite, echo=False)  # SQLite
# engine = create_async_engine(config.db.db_post, echo=False)  # PostgreSQL
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Помещаем нужные объекты в workflow_data диспетчера
some_var_1 = 1
some_var_2 = 'Some text'
dp.workflow_data.update({'my_int_var': some_var_1, 'my_text_var': some_var_2})

# Подключаем мидлварь счетчика
dp.update.outer_middleware(counter.CounterMiddleware())

# Подключаем мидлварь для сессии БД
dp.update.middleware(db.DataBaseSession(session_pool=session_maker))

# Подключаем мидлварь для локали
i18n = I18n(path="locales", default_locale="ru", domain="bot_00_template")
dp.update.middleware(locale.CustomI18nMiddleware(i18n=i18n))  # кастомная мидлвари, определение локали из бд, помещение в FSMContext
dp.update.middleware(FSMI18nMiddleware(i18n=i18n))  # получение языка на каждый апдейт, через обращение к FSMContext
# dp.update.middleware(ConstI18nMiddleware(locale='ru', i18n=i18n))  # задаем локаль как принудительно устанавливаемую константу
# dp.update.middleware(SimpleI18nMiddleware(i18n=i18n))  # сообщаем язык общения по значению поля "language_code" апдейта

# Подключаем роутеры
dp.include_router(start.start_router)
dp.include_router(owner.owner_router)
dp.include_router(admin.admin_router)
dp.include_router(product.product_router)
dp.include_router(donat.donat_router)
dp.include_router(group.group_router)
dp.include_router(aiogram_dialog.aiogram_dialog_router)
dp.include_router(FSMtest.fsmtest_router)

dp.include_router(other.other_router)


# Типы объектов которые будем отлавливать ботом
# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query',]  # Отбираем определенные типы апдейтов
ALLOWED_UPDATES = dp.resolve_used_update_types()  # Отбираем только используемые события по роутерам

# Функция сработает при остановке работы бота
async def on_shutdown():
    print('---   Бот лег!  ','-'*80)

# Главная функция конфигурирования и запуска бота
async def main() -> None:

    # Удаление предыдущей версии базы, и создание новых таблиц заново
    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)

    # Пропускаем накопившиеся апдейты - удаляем вебхуки (то что бот получил пока спал)
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
                               allowed_updates=ALLOWED_UPDATES,)
                            #    skip_updates=False)  # Если бот будет обрабатывать платежи или другие важные вещи, НЕ пропускаем обновления!
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
