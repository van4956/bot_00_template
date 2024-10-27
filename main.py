# source venv/Scripts/activate    -  запустить виртуальное окружение через GitBash
# venv\Scripts\activate           -  запустить виртуальное окружение через Windows
# ctrl + B                        -  запуск скрипта из любого файла проекта
# ctrl + I                        -  варианты эмодзи

import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.redis import RedisStorage, Redis
# from aiogram.fsm.storage.memory import MemoryStorage  # если с редис будут проблемы

# Импортируем конфиг
from config_data.config import Config, load_config
from database.engine import create_db, drop_db, session_maker # должен идти после загрузки .env
# Импортируем роутеры
from handlers import other_handlers, user_handlers
# Импортируем миддлвари
# ...
# Импортируем вспомогательные функции для создания нужных объектов
from keyboards.main_menu import main_menu_commands


# Инициализируем логгер
logger = logging.getLogger(__name__)

# Асинхронная функция запуска / создания таблиц
async def on_startup():
    run_param = False
    if run_param:
        await drop_db()
    await create_db()

# Функция конфигурирования и запуска бота
async def main():

    # Настраиваем форматер логирования
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] #%(levelname)-8s -  %(name)s:%(lineno)d  -  %(message)s')

    # Настраиваем логирование для SQLAlchemy (если надо)
    # sqlalchemy_logger = logging.getLogger('sqlalchemy')
    # sqlalchemy_logger.setLevel(logging.INFO)

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()
    db_lite = config.db.db_lite
    admin_ids = config.tg_bot.admin_ids

    # Выводим значения полей экземпляра класса Config на печать,
    # чтобы убедиться, что все данные, получаемые из переменных окружения, доступны
    print('BOT_TOKEN:', config.tg_bot.token)
    print('ADMIN_IDS:', config.tg_bot.admin_ids)
    print()
    print('DATABASE:', config.db.database)
    print('DB_HOST:', config.db.db_host)
    print('DB_USER:', config.db.db_user)
    print('DB_PASSWORD:', config.db.db_password)

    # Инициализируем Redis
    redis = Redis(host='localhost')

    # Инициализируем объект хранилища
    storage = RedisStorage(redis=redis)
    # storage = MemoryStorage()  # если с редис будут проблемы

    # Типы объектов которые будет отлавливать бот
    ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']

    # Инициализируем бот и диспетчер
    logger.info('Инициализируем объекты Бот и Диспетчер')
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.USER_IN_CHAT)
    # USER_IN_CHAT  - для каждого юзера, в каждом чате ведется своя запись состояний (по дефолту)
    # GLOBAL_USER  - для каждого юзера везде ведется своё состояние

    # Инициализируем другие объекты (пул соединений с БД, кеш и т.п.)
    logger.info('Инициализируем другие объекты')
    dp.startup.register(on_startup)

    # Помещаем нужные объекты в workflow_data диспетчера
    logger.info('Загружаем workflow_data')
    dp.workflow_data.update({'db_lite':db_lite, 'admin_ids':admin_ids})

    # Регистриуем роутеры
    logger.info('Подключаем роутеры')
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # Регистрируем миддлвари
    logger.info('Подключаем миддлвари')
    # ...

    # Пропускаем накопившиеся апдейты, настраиваем главное меню
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=main_menu_commands, scope=types.BotCommandScopeAllPrivateChats())

    # Запускаем polling
    logger.info('Запускаем polling')
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())
