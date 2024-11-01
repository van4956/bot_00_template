import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)


from aiogram import Router, F, Bot
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.i18n import gettext as _

from database.orm_users import orm_update_locale, orm_update_status

# Инициализируем роутер уровня модуля
other_router = Router()


# Этот хэндлер срабатывает на команду /help
@other_router.message(Command('help'))
async def process_help_command(message: Message):
    await message.answer(
        text=_('Доступные команды:\n\n'
               '/start - перезапустить бота\n'
               '/locale - сменить язык\n'
               '/help - справка по работе бота\n'
               '/product - тестовая функция\n'
               '/donat - донат автору\n'
               '/refund - возврат платежа\n')
    )


# Клавиатура
def get_keyboard():
    button_1 = InlineKeyboardButton(text=_('🇺🇸 Английский язык'), callback_data='locale_en')
    button_2 = InlineKeyboardButton(text=_('🇷🇺 Русский язык'), callback_data='locale_ru')
    button_3 = InlineKeyboardButton(text=_('🇩🇪 Немецкий язык'), callback_data='locale_de')
    button_4 = InlineKeyboardButton(text=_('🇯🇵 Японский язык'), callback_data='locale_jp')

    return InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4]])


# Это хендлер будет срабатывать на команду locale
@other_router.message(Command('locale'))
async def locale_cmd(message: Message):
    await message.answer(text=_('Выберите язык'),
                         reply_markup=get_keyboard())


@other_router.callback_query(F.data.startswith("locale_"))
async def update_locale_cmd(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_id = callback.from_user.id
    current_language = ''

    if callback.data == 'locale_en':
        current_language = _('🇺🇸 Английский язык')
        await orm_update_locale(session, user_id, 'en')
        await callback.answer(_("Выбран 🇺🇸 Английский язык"))
        await state.update_data(locale='en')
    elif callback.data == 'locale_ru':
        current_language = _('🇷🇺 Русский язык')
        await orm_update_locale(session, user_id, 'ru')
        await callback.answer(_("Выбран 🇷🇺 Русский язык"))
        await state.update_data(locale='ru')
    elif callback.data == 'locale_de':
        current_language = _('🇩🇪 Немецкий язык')
        await orm_update_locale(session, user_id, 'de')
        await callback.answer(_("Выбран 🇩🇪 Немецкий язык"))
        await state.update_data(locale='de')
    elif callback.data == 'locale_jp':
        current_language = _('🇯🇵 Японский язык')
        await orm_update_locale(session, user_id, 'ja')
        await callback.answer(_("Выбран 🇯🇵 Японский язык"))
        await state.update_data(locale='ja')

    # Скрываем клавиатуру, отправляя новое сообщение
    await callback.message.edit_reply_markup(reply_markup=None)

    # Отправляем сообщение с информацией о текущем языке
    await callback.message.answer(text=_("Выбран: \n{current_language}").format(current_language=current_language))


@other_router.message(Command("get_id"))
async def get_chat_id_cmd(message: Message):
    await message.answer(f"ID: <code>{message.chat.id}</code>")


# Этот хэндлер будет срабатывать на любые сообщения и отправлять пользователю их копию
@other_router.message()
async def send_echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text=_('Данный тип апдейтов не поддерживается методом send_copy'))
