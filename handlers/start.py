import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)


from aiogram import F, Router, html, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated
from aiogram.utils.i18n import gettext as _

from database.orm_users import orm_add_user, orm_get_ids, orm_get_users, orm_update_status
from common import keyboard


# Инициализируем роутер уровня модуля
start_router = Router()

# Функция стартовой клавиатуры
def start_keyboard():
    return keyboard.get_keyboard(_("кнопка 1"), _("кнопка 2"), _("кнопка 3"), _("кнопка 4"), sizes=(2, 2, ), placeholder='⬇️')

# Команда /start
@start_router.message(CommandStart())
async def start_cmd(message: Message, session: AsyncSession, bot: Bot, state: FSMContext):
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

    try:
        list_users = [user_id for user_id in await orm_get_ids(session)]
        chat_id = bot.home_group[0]
        if user_id not in list_users:
            await bot.send_message(chat_id=chat_id, text=_("✅ Пользователь <code>@{user_name}</code> - подписался на бота").format(user_name=user_name,
                                                                                                                                     user_id=user_id))
    except Exception as e:
        logger.error("Ошибка при отправке сообщения: %s", str(e))

    await message.answer(_('Бот активирован!'), reply_markup=keyboard.del_kb)

    analytics = state.workflow_data['analytics']
    await analytics(user_id=user_id, command_name="/start")

# Этот хэндлер будет срабатывать на блокировку бота пользователем
@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated, session: AsyncSession, bot: Bot):
    user_id = event.from_user.id
    chat_id = bot.home_group[0]
    user_name = event.from_user.username if event.from_user.username else 'NaN'
    await orm_update_status(session, user_id, 'kicked')
    await bot.send_message(chat_id = chat_id, text = _("⛔️ Пользователь <code>@{user_name}</code> - заблокировал бота ").format(user_name=user_name,
                                                                                                                              user_id=user_id))

# Этот хэндлер будет срабатывать на разблокировку бота пользователем
@start_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def process_user_unblocked_bot(event: ChatMemberUpdated, session: AsyncSession, bot: Bot):
    user_id = event.from_user.id
    chat_id = bot.home_group[0]
    full_name = event.from_user.full_name if event.from_user.full_name else "NaN"
    user_name = event.from_user.username if event.from_user.username else 'NaN'
    await orm_update_status(session, user_id, 'member')
    await bot.send_message(chat_id = user_id, text = _('{full_name}, Добро пожаловать обратно!').format(full_name=full_name))
    await bot.send_message(chat_id = chat_id, text = _("♻️ Пользователь <code>@{user_name}</code> - разблокировал бота ").format(user_name=user_name,
                                                                                                                               user_id=user_id))
