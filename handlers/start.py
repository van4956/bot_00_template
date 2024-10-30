import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram import F, Router, html, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from database.orm_users import orm_add_user



# Инициализируем роутер уровня модуля
start_router = Router()

# команда /start
@start_router.message(CommandStart())
async def start_cmd(message: Message, session: AsyncSession, bot: Bot):
    user_id = message.from_user.id
    user_name = message.from_user.username if message.from_user.username else 'None'
    full_name = message.from_user.full_name if message.from_user.full_name else 'None'
    locale = message.from_user.language_code if message.from_user.language_code else 'ru'
    data = {'user_id':user_id,
                            'user_name':user_name,
                            'full_name':full_name,
                            'locale':locale,
                            'status':'member',
                            'flag':1}

    await orm_add_user(session, data)
    # await bot.send_message(chat_id = -4197834633, text = f"Пользователь {user_name} {user_id} подписался на бота ✅")
    try:
        await bot.send_message(chat_id = -4197834633, text = f"Пользователь {user_name} {user_id} подписался на бота ✅")
    except Exception as e:
        logger.error("Ошибка при отправке сообщения: %s", str(e))

    start_text = f'Приветствую вас {full_name}'
    await message.answer(start_text)
