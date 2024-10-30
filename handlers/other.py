import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.i18n import gettext as _


# Инициализируем роутер уровня модуля
other_router = Router()

# Этот хэндлер срабатывает на команду /help
@other_router.message(Command('help'))
async def process_help_command(message: Message):
    await message.answer(
        text=_('Доступные команды:\n\n'
               '/start - перезапустить бота\n'
               '/product - тестовая функция\n'
               '/help - справка по работе бота\n'
               '/donat - донат автору\n'
               '/terms - условия обслуживания\n'
               '/refund - возврат платежа\n'
               '/paysupport - поддержка оплаты')
    )

# Этот хэндлер будет срабатывать на любые сообщения и отправлять пользователю их копию
@other_router.message()
async def send_echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text=_('Данный тип апдейтов не поддерживается методом send_copy'))
