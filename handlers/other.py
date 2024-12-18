import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)


from aiogram import Router, F, Bot
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.i18n import gettext as _

from database.orm_users import orm_update_locale
from common import keyboard

# Инициализируем роутер уровня модуля
other_router = Router()


# Этот хэндлер срабатывает на команду /help
@other_router.message(Command('help'))
async def process_help_command(message: Message):
    await message.answer(
        text=_('Доступные команды:\n\n'
               '/start - перезапустить бота\n'
               '/help - справка по работе бота\n'
               '/lang - сменить язык\n\n'
               '/llm - языковая модель\n'
               '/product - выборт товаров\n'
               '/payments - оплата товаров\n'
               '/questionnaire - анкетирование\n\n'
               '/donate - отправить донат\n'
               '/refund - возврат доната')
    )


# Клавиатура выбора языка
def keyboard_language():
    button_1 = InlineKeyboardButton(text=_('🇺🇸 Английский'), callback_data='locale_en')
    button_2 = InlineKeyboardButton(text=_('🇷🇺 Русский'), callback_data='locale_ru')
    button_3 = InlineKeyboardButton(text=_('🇩🇪 Немецкий'), callback_data='locale_de')
    # button_4 = InlineKeyboardButton(text=_('🇫🇷 Французский'), callback_data='locale_fr')
    # button_5 = InlineKeyboardButton(text=_('🇯🇵 Японский'), callback_data='locale_ja')

    return InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])


# Это хендлер будет срабатывать на команду locale
@other_router.message(Command('lang'))
async def locale_cmd(message: Message):
    await message.answer(_("Настройки языка"), reply_markup=keyboard.del_kb)
    await message.answer(text=_('Выберите язык'),
                         reply_markup=keyboard_language())


@other_router.callback_query(F.data.startswith("locale_"))
async def update_locale_cmd(callback: CallbackQuery, session: AsyncSession, state: FSMContext, workflow_data: dict):
    user_id = callback.from_user.id

    if callback.data == 'locale_en':
        await orm_update_locale(session, user_id, 'en')  # Обновляем локаль в бд
        await state.update_data(locale='en')  # Обновляем локаль в контексте
        await callback.message.edit_text('Choose a language ', reply_markup=None)  # Редактируем сообщение, скрываем inline клавиатуру
        await callback.answer("Selected: 🇺🇸 English")  # Отправляем всплывашку
        await callback.message.answer("Current language \n\n 🇺🇸 English") # Отправляем новое сообщение

    elif callback.data == 'locale_ru':
        await orm_update_locale(session, user_id, 'ru')  # Обновляем локаль в бд
        await state.update_data(locale='ru')  # Обновляем локаль в контексте
        await callback.message.edit_text('Выберите язык ', reply_markup=None)   # Редактируем сообщение, скрываем inline клавиатуру
        await callback.answer("Выбран: 🇷🇺 Русский язык")  # Отправляем всплывашку
        await callback.message.answer("Текущий язык \n\n 🇷🇺 Русский") # Отправляем новое сообщение

    elif callback.data == 'locale_de':
        await orm_update_locale(session, user_id, 'de')  # Обновляем локаль в бд
        await state.update_data(locale='de')  # Обновляем локаль в контексте
        await callback.message.edit_text('Wählen Sie eine Sprache ', reply_markup=None)  # type: ignore # Редактируем сообщение,скрываем клавиатуру
        await callback.answer("Ausgewählt 🇩🇪 Deutsch")  # Отправляем всплывашку
        await callback.message.answer("Aktuelle Sprache \n\n 🇩🇪 Deutsch")   # Отправляем новое сообщение

    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/options",
                    command_name="/language")

# секретный хендлер, покажет содержимое data пользователя
@other_router.message(Command("data"))
async def data_cmd(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(str(data))

# хендлер на команду "Назад на главную ↩️"
@other_router.message(StateFilter("*"), F.text == "Назад на главную ↩️")
async def back_cmd(message: Message, state: FSMContext):
    await state.set_state(None)
    await message.answer("Бот активирован!", reply_markup=keyboard.start_keyboard())
