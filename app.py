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

from handlers import other, admin, product, group, questionnaire, start, owner, donate, payments
from common.comands import private, admin_private
from database.models import Base
from middlewares import counter, db, locale, throttle

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

# Создаем движок бд, создаем ассинхроную сессию
# engine = create_async_engine(config.db.db_lite, echo=False)  # SQLite
engine = create_async_engine(config.db.db_post, echo=False)  # PostgreSQL
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Помещаем нужные объекты в workflow_data диспетчера
some_var_1 = 1
some_var_2 = 'Some text'
dp.workflow_data.update({'my_int_var': some_var_1, 'my_text_var': some_var_2})

# Подключаем мидлвари
dp.update.outer_middleware(throttle.ThrottleMiddleware())  # тротлинг чрезмерно частых действий пользователей
dp.update.outer_middleware(counter.CounterMiddleware())  # просто счетчик
dp.update.outer_middleware(db.DataBaseSession(session_pool=session_maker))  # мидлварь для прокидывания сессии БД
dp.update.outer_middleware(locale.LocaleFromDBMiddleware())  # определяем локаль из БД и передам ее в FSMContext

i18n = I18n(path="locales", default_locale="ru", domain="bot_00_template")  # создаем объект I18n
dp.update.middleware(FSMI18nMiddleware(i18n=i18n))  # получяем язык на каждый апдейт, через обращение к FSMContext

# dp.update.middleware(ConstI18nMiddleware(locale='ru', i18n=i18n))  # задаем локаль как принудительно устанавливаемую константу
# dp.update.middleware(SimpleI18nMiddleware(i18n=i18n))  # сообщаем язык общения по значению поля "language_code" апдейта

# Подключаем роутеры
dp.include_router(start.start_router)
dp.include_router(owner.owner_router)
dp.include_router(admin.admin_router)
dp.include_router(donate.donate_router)
dp.include_router(product.product_router)
dp.include_router(payments.payments_router)
dp.include_router(group.group_router)
dp.include_router(questionnaire.questionnaire_router)

dp.include_router(other.other_router)


# Типы апдейтов которые будем отлавливать ботом
# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query',]  # Отбираем определенные типы апдейтов
ALLOWED_UPDATES = dp.resolve_used_update_types()  # Отбираем только используемые события по роутерам

# Функция сработает при запуске бота
async def on_startup():
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    await bot.send_message(chat_id = bot.home_group[0], text = f"🕊  <code>@{bot_username}</code>  -  запущен!")

# Функция сработает при остановке работы бота
async def on_shutdown():
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    await bot.send_message(chat_id = bot.home_group[0], text = f"☠️  <code>@{bot_username}</code>  -  лег!")

# Главная функция конфигурирования и запуска бота
async def main() -> None:

    # Удаление предыдущей версии базы, и создание новых таблиц заново
    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    # Регистрируем функцию, которая будет вызвана автоматически при запуске/остановке бота
    dp.startup.register(on_startup)
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
                            #    skip_updates=False)  # Если бот будет обрабатывать платежи, НЕ пропускаем обновления!
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
