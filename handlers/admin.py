import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _

from filters.is_admin import IsAdminGroupFilter, IsAdminListFilter
from filters.chat_type import ChatTypeFilter
from common import keyboard
from database.orm_users import orm_get_users


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdminListFilter(is_admin=True))


# команда /admin
@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, bot: Bot):
    if message.from_user.id in bot.admin_list:
        await message.answer(text=_('Админка:\n\n'
                                    '/admin - режим адменистратора\n'
                                    '/start - перезапустить бота\n'
                                    '/data - состояние FSMContext\n'
                                    '/get_id - id диалога\n'
                                    '/ping - количество апдейтов\n'
                                    '/users - пользователи\n'
                                    '/admins - админы\n'),
                            reply_markup=keyboard.del_kb
                            )


# команда /users, показывает полную информацию всех зарегистрированных пользователей
@admin_router.message(Command("users"))
async def get_users_info(message: Message, session: AsyncSession):
    all_info = ['Информация зарегистрированных пользователей:\n']
    cnt_users = 0
    for user in await orm_get_users(session):
        info = f"<code>{user.user_id: <11}</code> | <code>{user.status[0]}</code> | {user.flag} | {user.locale} | @{user.user_name}"
        all_info.append(info)
        cnt_users += 1

    text = "\n".join(all_info)

    # Обрезаем запись, если она превышает 1000 символов
    if len(text) > 1000:
        text = text[:995] + "..."

    text = text + f"\n\nВсего {cnt_users} пользователей"

    await message.answer(text)


# Here is some example !ping command ...
@admin_router.message(IsAdminListFilter(is_admin=True), Command(commands=["ping"]),)
async def cmd_ping_bot(message: Message, counter):
    await message.reply(f"ping-{counter}")


# Этот хендлер показывает ID чата в котором запущена команда
@admin_router.message(Command("get_id"))
async def get_chat_id_cmd(message: Message):
    await message.answer(f"ID: <code>{message.chat.id}</code>")

# команда /admins, показывает состав всех админов
@admin_router.message(Command("admins"))
async def get_admins_info(message: Message, bot: Bot):
    list_admins = '\n'.join([f"<code>{str(id)}</code>" for id in bot.admin_list])
    await message.answer(f"Админы:\n\n{list_admins}")
