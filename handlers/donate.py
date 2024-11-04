import logging
from typing import Any

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from datetime import datetime, timedelta, timezone
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _



# Инициализируем роутер уровня модуля
donate_router = Router()

# Фильтрация сообщений для обработки только в приватных чатах
donate_router.message.filter(F.chat.type == "private")

# Определение класс состояний для валюты
class Donate(StatesGroup):
    donate = State()

# Условие для возврата: возврат возможен только в течение 30 дней после доната
REFUND_PERIOD_DAYS = 30


# Обработчики
@donate_router.message(Command("donate"))
async def cmd_donate(message: Message, command: CommandObject, state: FSMContext):
    # Проверяем, чтобы сумма была от 1 до 2500 звёзд (таковы лимиты Telegram API)
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        await message.answer(text=_('Поддержать автора донатом.\n\n'
                                    'Ввведите произвольную сумму в формате <code>/donate [ЧИСЛО]</code>\n'
                                    'где [ЧИСЛО] это сумма доната, от 1 до 2500 ⭐️ \n\n'
                                    'Примеры:\n'
                                    '• <code>/donate 10</code> - задонатить 10 ⭐️\n'
                                    '• <code>/donate 100</code> - задонатить 100 ⭐️'))
        return

    # Сумма доната
    amount = int(command.args)

    # Формируем клавиатуру с кнопками для оплаты и отмены операции
    kb = InlineKeyboardBuilder()
    kb.button(text=_("Оплатить {amount} XTR").format(amount=amount), pay=True)  # pay=True важный параметр, указывающий что кнопка предназначена для оплаты
    kb.button(text=_("Отменить"), callback_data="donate_cancel")
    kb.adjust(1)

    # Формируем инвойс для оплаты
    prices = [LabeledPrice(label="XTR", amount=amount)]
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    await message.answer_invoice(
        title=_("Донат"),
        description=_("Поддержать на сумму {amount} ⭐️").format(amount=amount),
        prices=prices,
        provider_token="",
        payload=timestamp,  # Добавляем временную метку в payload
        currency="XTR",
        reply_markup=kb.as_markup()
    )

    await state.set_state(Donate.donate)


# Обработка отмены доната, выводим сообщение об отмене и удаляем сообщение
@donate_router.callback_query(Donate.donate, F.data == "donate_cancel")
async def on_donate_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer(_("😢 Донат отменен."))
    await callback.message.delete()
    await state.clear()

@donate_router.message(Command('refundd'))
async def command_refund_handler(message: Message, bot: Bot, command: CommandObject) -> None:
    transaction_id = command.args if command.args else ''
    user_id = message.from_user.id
    try:
        await bot.refund_star_payment(user_id=user_id, telegram_payment_charge_id=transaction_id)
    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        print("Ошибка:", e)

@donate_router.message(Command("refund"))
async def cmd_refund(message: Message, bot: Bot, command: CommandObject, state: FSMContext):
    # ID транзакции для возврата средств
    t_id = command.args

    # Проверяем, указан ли ID транзакции
    if t_id is None:
        await message.answer(_("Пожалуйста, укажите идентификатор транзакции в формате <code>/refund [id]</code>, "
                                "где <code>[id]</code> это идентификатор транзакции, который вы получили после доната.\n\n"
                                "/paysupport - поддержка оплаты\n"
                                "/terms - условия использования"))
        return

    # Проверяем, не истек ли срок возврата
    try:
        # Извлекаем временную метку из donate_info
        data = await state.get_data()
        donate_info: dict = data.get('donate_info', {})
        timestamp: Any = donate_info.get(t_id, '')  # получаем временную метку в формате строки, по id транзакции

        # Парсим строку в объект datetime
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d-%H-%M-%S")

        # Получаем текущую дату и время
        current_time = datetime.now()

        # Вычисляем разницу во времени
        time_difference = current_time - timestamp

        if time_difference > timedelta(days=REFUND_PERIOD_DAYS):
            await message.answer(_("Срок для возврата средств истек. Возврат возможен только в течение 30 дней после доната."))
            return

    # Если не удалось распарсить временную метку, выводим сообщение об ошибке
    except (ValueError, IndexError) as e:
        logger.error("Ошибка: %s", str(e))
        await message.answer(_("Неверный формат идентификатора транзакции."))
        return

    # Пытаемся сделать возврат средств
    try:
        await bot.refund_star_payment(user_id=message.from_user.id, telegram_payment_charge_id=t_id)
        await message.answer(_("Рефанд произведен успешно. Потраченные звёзды уже вернулись на ваш счёт в Telegram."))

    except TelegramBadRequest as e:
        logger.error("Ошибка: %s", str(e))
        err_text = _("Транзакция с указанным идентификатором не найдена. Пожалуйста, проверьте введенные данные и повторите ещё раз.")

        if "CHARGE_ALREADY_REFUNDED" in e.message:
            err_text = _("Рефанд по этой транзакции уже был ранее произведен.")

        await message.answer(err_text)
        return


# Проверка перед оплатой, бот должен ответить в течение 10 секунд
@donate_router.pre_checkout_query(Donate.donate)
async def pre_checkout_query(query: PreCheckoutQuery):
    # Мы всегда отвечаем положительно, так как это просто донат
    await query.answer(ok=True)

    # Если по какой-то причине нужно отказать в проведении платежа, можно использовать:
    # Добавляем условие для проверки ..
    # await query.answer(ok=False, error_message="Причина отказа в проведении платежа")


# Обработка успешного платежа
@donate_router.message(Donate.donate, F.successful_payment)
async def on_successfull_payment(message: Message, state: FSMContext):
    # Получаем объект message.successful_payment
    t_id = message.successful_payment.telegram_payment_charge_id  # ID транзакции
    invoice_payload = message.successful_payment.invoice_payload  # payload который мы установили ранее, там временная метка

    data = await state.get_data()
    donate_info = data.get('donate_info', {})
    donate_info[t_id] = invoice_payload
    await state.update_data(donate_info=donate_info)

    await message.answer(
        text=_("<b>Спасибо!</b>\n"
               "Ваш донат успешно принят.\n\n"
                "ID транзакции:\n<code>{t_id}</code>").format(t_id=t_id),
        message_effect_id="5104841245755180586"
    )
        # другие реакции (если надо)
        # 🔥 огонь - 5104841245755180586
        # 👍 лайк - 5107584321108051014
        # 👎 дизлайк - 5104858069142078462
        # ❤️ сердечко - 5159385139981059251
        # 🎉 праздник - 5046509860389126442
        # 💩 какаха - 5046589136895476101

    await state.clear()



# Отправляем сообщение с инструкциями по поддержке покупок
@donate_router.message(Command("paysupport"))
async def cmd_paysupport(message: Message, state: FSMContext):
    data = await state.get_data()
    donate_info = data.get('donate_info', {})
    print('donate_info:', donate_info)
    t_id = max(donate_info, key=donate_info.get) if donate_info else _('ID транзакции не найден')
    await message.answer(
        text=_('Чтобы оформить возврат, вам понадобится ID транзакции.\n\nID последней вашей транзакции:\n<code>{t_id}</code>').format(t_id=t_id))


# Отправляем условия использования бота (Terms of Service)
@donate_router.message(Command("terms"))
async def cmd_terms(message: Message):
    await message.answer(_("<b>Условия использования</b>\n\n"
                            "1. Донаты являются добровольными и могут быть возвращены в течение 30 дней после совершения платежа.\n\n"
                            "2. Для возврата средств необходимо предоставить идентификатор транзакции. Получить ID транзакции /paysupport\n\n"
                            "3. После истечения 30 дней возврат средств невозможен.\n\n"
                            "4. Использование бота подразумевает согласие с данными условиями.\n\n")
                            )
