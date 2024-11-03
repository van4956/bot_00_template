import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram import F, Router, html, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.i18n import gettext as _

# Инициализируем роутер уровня модуля
payments_router = Router()

# Фильтрация сообщений для обработки только в приватных чатах
payments_router.message.filter(F.chat.type == "private")

# Токен и валюта для провайдера
PROVIDER_TOKEN = '1744374395:TEST:91f0953d6a84fd73f0a9'
CURRENCY = 'RUB'



# Этот хэндлер срабатывает на нажатие инлайн-кнопки "Оплатить все товары"
# @product_router.callback_query(F.data == 'pay_all_products')
# async def process_pay_button_click(callback: CallbackQuery, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     items_num = data.get('items_num', 0)

#     description = f"Оплатить {items_num} товаров"
#     prices = [LabeledPrice(label="Оплата заказа", amount=items_num * 100)]

#     try:
#         if prices:
#             await bot.send_invoice(
#                 chat_id=callback.from_user.id,
#                 title='Оплата всех товаров',
#                 description=description,
#                 payload='sub1',
#                 provider_token=PROVIDER_TOKEN,
#                 currency='RUB',
#                 prices=prices
#             )
#     except Exception as e:
#         print("e:", e)
#         await callback.message.delete()
#         await callback.message.answer(text=f'Ошибка оплаты: {e}')

# prices
PRICE = LabeledPrice(label="Подписка на 1 месяц", amount=500*100)  # в копейках (руб)

# buy
@payments_router.callback_query(F.data.startswith("pay_all_products"))
async def buy(callback: CallbackQuery, bot: Bot):
    if PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(callback.from_user.id, "Тестовый платеж!!!")

    await bot.send_invoice(callback.from_user.id,
                           title="Подписка на бота",
                           description="Активация подписки на бота на 1 месяц",
                           provider_token=PROVIDER_TOKEN,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")

# pre checkout  (must be answered in 10 seconds)
# @product_router.pre_checkout_query_handler(lambda query: True)
# async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
#     await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

# successful payment
@payments_router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")

# find token
async def func()


@payments_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot) -> None:
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# @product_router.message(F.successful_payment)
# async def process_successful_payment(message: Message) -> None:
#     payload_to_message = {
#         'sub1': 'Подписка 1',
#         'sub2': 'Подписка 2',
#     }

#     response_message = payload_to_message.get(message.successful_payment.invoice_payload, 'Оплата успешна!')
#     await message.answer(response_message)
