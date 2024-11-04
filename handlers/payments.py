import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

import asyncio
from aiogram import F, Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, LabeledPrice, ShippingOption, ShippingQuery, PreCheckoutQuery, ContentType

# Инициализируем роутер уровня модуля
payments_router = Router()


# -----------------------------------------------< тексты >---------------------------------

help_message = '''
Через этого бота можно купить машину времени, чтобы посмотреть, как происходит покупка и оплата в Telegram.\n
Отправьте команду /buy, чтобы перейти к покупке.\n
Узнать правила и положения команда /terms_payments.
'''

start_message = 'Привет! Это демонстрация работы платежей в Telegram!\n' + help_message

pre_buy_demo_alert = '''\
Запущен тестовый режим, для оплаты используйте карту \n\n<code>4242 4242 4242 4242</code>\n<code>12/24</code>  <code>000</code>\n
Счёт для оплаты:
'''

terms = '''\
<b>Спасибо, что выбрали нашего бота. Мы надеемся, вам понравится ваша новая машина времени!</b>

1. Если машина времени не будет доставлена вовремя, пожалуйста, произведите переосмысление вашей концепции времени и попробуйте снова.\n
2. Если вы обнаружите, что машина времени не работает, будьте добры связаться с нашими сервисными мастерскими будущего с экзопланеты Trappist-1e. Они будут доступны в любом месте в период с мая 2075 года по ноябрь 4000 года нашей эры.\n
3. Если вы хотите вернуть деньги, будьте так любезны подать заявку вчера, и мы немедленно совершим возврат.
'''

tm_description = '''\
Хотите познакомиться со своими пра-пра-пра-пра-бабушкой и дедушкой?\n
Сделать состояние на ставках?\n
Пожать руку Хаммурапи и прогуляться по Висячим садам Семирамиды?\n
Закажите Машину Времени у нас прямо сейчас!
'''

AU_error = '''\
К сожалению, наши курьеры боятся кенгуру, а телепорт не может так далеко отправлять.
Попробуйте выбрать другой адрес!
'''

wrong_email = '''\
Нам кажется, что указанный имейл не действителен.
Попробуйте указать другой имейл
'''

successful_payment = '''
Ура! Платеж на сумму <code>{total_amount} {currency}</code> совершен успешно! Приятного пользования новенькой машиной времени!\n
Правила возврата средств смотрите в /terms_payments\n
Купить ещё одну машину времени своему другу - /buy
'''


# --------------------------------------------------------------------------------



TIME_MACHINE_IMAGE_URL = 'http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg'

PAYMASTER_PROVIDER_TOKEN = '1744374395:TEST:91f0953d6a84fd73f0a9'
CURRENCY = 'RUB'



# Настройка цен
PRICES = [LabeledPrice(label='Настоящая Машина Времени', amount=4200000),
                                LabeledPrice(label='Подарочная упаковка', amount=30000),
                                LabeledPrice(label='Товары', amount=1000 * 100)]

# Настройка вариантов доставки
TELEPORTER_SHIPPING_OPTION = ShippingOption(id='teleporter', title='Всемирный телепорт', prices=[LabeledPrice(label='Телепорт', amount=1000000)])

RUSSIAN_POST_SHIPPING_OPTION = ShippingOption(id='ru_post', title='Почтой России', prices=[LabeledPrice(label='Деревянный ящик с амортизирующей подвеской внутри', amount=100000),
                                                                                           LabeledPrice(label='Срочное отправление (5-10 дней)', amount=500000)])

PICKUP_SHIPPING_OPTION = ShippingOption(id='pickup', title='Самовывоз', prices=[LabeledPrice(label='Самовывоз в Москве', amount=50000)])


@payments_router.message(Command('payments'))
async def process_start_command(message: Message):
    await message.answer(start_message)


@payments_router.message(Command('help_payments'))
async def process_help_command(message: Message):
    await message.answer(help_message)


@payments_router.message(Command('terms_payments'))
async def process_terms_command(message: Message):
    await message.answer(terms, disable_web_page_preview=True)

# Формируем / отправляем платежку
@payments_router.message(Command('buy'))
async def process_buy_command(message: Message, bot: Bot):
    # Если это тестовая платежка, предупреждаем
    if PAYMASTER_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await message.answer(text=pre_buy_demo_alert)

    await bot.send_invoice(chat_id=message.chat.id,
                           title='Настоящая Машина Времени',
                           description=tm_description,
                           provider_token=PAYMASTER_PROVIDER_TOKEN,
                           currency='rub',
                           photo_url=TIME_MACHINE_IMAGE_URL,
                           photo_height=512,  # !=0/None or picture won't be shown
                           photo_width=512,
                           photo_size=512,
                           need_email=True,  # будет запрошена электронная почта при заполнении информации для доставки
                           need_phone_number=True,  # аналогично, номер телефона
                        #    need_shipping_address=False,
                           is_flexible=True,  # True, если вам нужно настроить стоимость доставки
                           prices=PRICES,
                           start_parameter='time-machine-example',
                           payload='some-invoice-payload-for-our-internal-use')

# При сохранении адреса доставки будет отправлен апдейт, ловим его и обрабатываем
@payments_router.shipping_query()
async def process_shipping_query(shipping_query: ShippingQuery, bot: Bot):
    # Обрабатывает отказ платежа с нашей стороны
    if shipping_query.shipping_address.country_code == 'AU':
        await bot.answer_shipping_query(shipping_query_id=shipping_query.id,
                                        ok=False,
                                        error_message=AU_error
                                        )
        return

    # Способы доставки
    shipping_options = [TELEPORTER_SHIPPING_OPTION]

    # Если код страны 'RU', добавляем способ доставки Почту России
    if shipping_query.shipping_address.country_code == 'RU':
        shipping_options.append(RUSSIAN_POST_SHIPPING_OPTION)
        # Если город Москва, добавляем еще несколько способов доставки
        if shipping_query.shipping_address.city == 'Москва':
            shipping_options.append(PICKUP_SHIPPING_OPTION)

    await bot.answer_shipping_query(shipping_query_id=shipping_query.id,
                                    ok=True,
                                    shipping_options=shipping_options
                                    )

# Необходимо ещё раз подтвердить платеж
@payments_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    # Получаем информацию о платеже через order_info
    print('order_info')
    print(pre_checkout_query.order_info)

    # Проверяем валидность указанной информации, исключаем почту 'vasya@pupkin.com'
    if hasattr(pre_checkout_query.order_info, 'email') and (pre_checkout_query.order_info.email == 'vasya@pupkin.com'):
        await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                            ok=False,
                                            error_message=wrong_email
                                            )
        return

    # В случае если все норм, подтверждаем платеж
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                        ok=True)


@payments_router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    await message.answer(text= successful_payment.format(total_amount=message.successful_payment.total_amount // 100,
                                                         currency=message.successful_payment.currency)
                                                         )
