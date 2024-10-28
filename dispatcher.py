import logging
from aiogram import Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.i18n import ConstI18nMiddleware, I18n

from handlers import other, admin, product, donat, group

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s')

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)

# Инициализация диспетчера
logger.info('Инициализация диспетчера')
dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)
# USER_IN_CHAT  -  для каждого юзера, в каждом чате ведется своя запись состояний (по дефолту)
# GLOBAL_USER  -  для каждого юзера везде ведется своё состояние

# Регистриуем роутеры
logger.info('Регистриуем роутеры')
dp.include_router(admin.admin_router)
dp.include_router(product.product_router)
dp.include_router(donat.donat_router)
dp.include_router(group.group_router)
dp.include_router(other.other_router)

# Регистрируем миддлвари
i18n = I18n(path="locales", default_locale="ru", domain="bot_00_template")
dp.update.middleware(ConstI18nMiddleware(locale='ru', i18n=i18n))
