import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.is_owner import IsOwnerFilter
from filters.chat_type import ChatTypeFilter


owner_router = Router()
owner_router.message.filter(ChatTypeFilter(["private"]), IsOwnerFilter(is_owner=True))


