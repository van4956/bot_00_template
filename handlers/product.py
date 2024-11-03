import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram import F, Router, html, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.i18n import gettext as _



# Инициализируем роутер уровня модуля
product_router = Router()

# Фильтрация сообщений для обработки только в приватных чатах
product_router.message.filter(F.chat.type == "private")

# Клавиатура магазина
def product_keyboard():
    button_1 = InlineKeyboardButton(text=_('Добавить 1 товар'), callback_data='add_pressed_1')
    button_2 = InlineKeyboardButton(text=_('Добавить 3 товара'), callback_data='add_pressed_3')
    button_3 = InlineKeyboardButton(text=_('Убрать 1 товар'), callback_data='remove_pressed')
    return InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])



# Этот хэндлер срабатывает на команду /product
@product_router.message(Command('product'))
async def process_start_command(message: Message, state: FSMContext):
    await state.update_data(items_num=0)
    username = html.quote(message.from_user.full_name)

    # Отправляем сообщение пользователю
    await message.answer(text=_('Привет, {username}.\n\nДобавьте товары в корзину').format(username=username),
                         reply_markup=product_keyboard())



# Этот хэндлер срабатывает на нажатие инлайн-кнопки удаления товара
@product_router.callback_query(F.data == 'remove_pressed')
async def process_remove_button_click(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items_num = data.get('items_num',0)
    if items_num > 0:
        items_num -= 1
        await callback.answer(text=_('Вы удалили товар'))
        await state.update_data(items_num=items_num)
        await callback.message.edit_text(text=_('В корзине {} товар','В корзине {} товаров', items_num).format(items_num),
                                         reply_markup=product_keyboard())
    else:
        await callback.answer(text=_('В корзине пусто'))


# Этот хэндлер срабатывает на нажатие инлайн-кнопки добавить товар/товары
@product_router.callback_query(F.data.startswith("add_pressed_"))
async def process_button_click(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items_num = data.get('items_num', 0)
    if callback.data == 'add_pressed_1':
        items_num += 1
        await callback.answer(text=_('Вы добавили товар'))
    elif callback.data == 'add_pressed_3':
        items_num += 3
        await callback.answer(text=_('Вы добавили товары'))
    await state.update_data(items_num=items_num)
    await callback.message.edit_text(text=_('В корзине {} товар', 'В корзине {} товаров', items_num).format(items_num),
                                     reply_markup=product_keyboard())
