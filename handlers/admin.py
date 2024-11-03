import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.is_admin import IsAdminGroupFilter, IsAdminListFilter
from filters.chat_type import ChatTypeFilter


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdminListFilter(is_admin=True))




# Here is some example !ping command ...
@admin_router.message(IsAdminListFilter(is_admin=True), Command(commands=["ping"]),)
async def cmd_ping_bot(message: Message, counter):
    await message.reply(f"ping-msg-{counter}")


# Этот хендлер показывает ID чата в котором запущена команда
@admin_router.message(Command("get_id"))
async def get_chat_id_cmd(message: Message):
    await message.answer(f"ID: <code>{message.chat.id}</code>")