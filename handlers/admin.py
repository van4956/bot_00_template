from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.is_owner import IsOwnerFilter


admin_router = Router()
admin_router.message.filter(F.chat.type == "private", IsOwnerFilter(is_owner=True)) # разрешить действия администратора бота только владельцу бота




# Here is some example !ping command ...
@admin_router.message(IsOwnerFilter(is_owner=True), Command(commands=["ping"]),)
async def cmd_ping_bot(message: Message):
    await message.reply("ping-msg")
