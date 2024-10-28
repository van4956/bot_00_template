from aiogram import F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.i18n import gettext as _

# Инициализируем роутер уровня модуля
user_router = Router()


def get_keyboard():
    # Создаем объекты инлайн-кнопок
    button_1 = InlineKeyboardButton(
        text=_('Добавить 1 товар'),
        callback_data='add_1_pressed'
    )
    button_2 = InlineKeyboardButton(
        text=_('Добавить 3 товара'),
        callback_data='add_3_pressed'
    )
    button_3 = InlineKeyboardButton(
        text=_('Убрать 1 товар'),
        callback_data='remove_pressed'
    )
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])


# Этот хэндлер срабатывает на команду /start
@user_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.update_data(items_num=0)
    username = html.quote(message.from_user.full_name)

    # Отправляем сообщение пользователю
    await message.answer(
        text=_('Привет, {username}.\n\n'
               'Добавьте товары в корзину').format(username=username),
        reply_markup=get_keyboard()
    )


# Этот хэндлер срабатывает на команду /help
@user_router.message(Command('help'))
async def process_help_command(message: Message):
    await message.answer(
        text=_('Это бот для демонстрации процесса интернационализации\n\n'
               'Доступные команды:\n\n'
               '/start - перезапуск бота\n'
               '/help - справка по работе бота')
    )


# Этот хэндлер срабатывает на нажатие инлайн-кнопки удаления товара
@user_router.callback_query(F.data == 'remove_pressed')
async def process_remove_button_click(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items_num = data.get('items_num')
    if items_num > 0:
        items_num -= 1
        await callback.answer(text=_('Вы удалили товар'))
        await state.update_data(items_num=items_num)
        await callback.message.edit_text(text=_(
            'В корзине {} товар',
            'В корзине {} товаров', items_num).format(items_num),
        reply_markup=get_keyboard())
    else:
        await callback.answer(text=_('В корзине пусто'))


# Этот хэндлер срабатывает на нажатие инлайн-кнопки
@user_router.callback_query()
async def process_button_click(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items_num = data.get('items_num')
    if callback.data == 'add_1_pressed':
        items_num += 1
        await callback.answer(text=_('Вы добавили товар'))
    else:
        items_num += 3
        await callback.answer(text=_('Вы добавили товары'))
    await state.update_data(items_num=items_num)
    await callback.message.edit_text(text=_(
        'В корзине {} товар',
        'В корзине {} товаров', items_num).format(items_num),
        reply_markup=get_keyboard())
