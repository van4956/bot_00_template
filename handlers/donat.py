import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from datetime import datetime, timedelta, timezone
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _



# Объявление маршрутизатора
donat_router = Router()
# Фильтрация сообщений для обработки только в приватных чатах
donat_router.message.filter(F.chat.type == "private")


# Условие для возврата: возврат возможен только в течение 30 дней после доната
REFUND_PERIOD_DAYS = 30

# Обработчики
@donat_router.message(Command("donate", "donat", "донат"))
async def cmd_donate(message: Message, command: CommandObject):
    # Проверяем, передан ли аргумент суммы звёзд для доната
    # Если аргумент не указан или сумма некорректна, выводим сообщение об ошибке
    # Также проверяем, чтобы сумма была от 1 до 2500 звёзд (лимиты Telegram API)
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        text = ('Пожалуйста, введите сумму в формате <code>/donate [ЧИСЛО]</code>\n'
                'где [ЧИСЛО] это сумма доната, от 1 до 2500 ⭐️ \n\n'

                'Примеры:\n'
                '• <code>/donate 100</code> - задонатить 100 ⭐️\n'
                '• <code>/donate 500</code> - задонатить 500 ⭐️\n'
                '• <code>/donate 1000</code> - задонатить 1000 ⭐️')
        await message.answer(text=_(text))
        return

    # Сумма доната
    amount = int(command.args)

    # Формируем клавиатуру с кнопками для оплаты и отмены операции
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_("Оплатить {amount} XTR").format(amount=amount),
        pay=True  # Важный параметр, указывающий, что кнопка предназначена для оплаты
    )
    kb.button(text=_("Отменить"), callback_data="donate_cancel")
    kb.adjust(1)  # Все кнопки в один ряд

    # Формируем инвойс для оплаты
    prices = [LabeledPrice(label="XTR", amount=amount)]

    await message.answer_invoice(
        title=_("Донат автору"),
        description=_("На сумму в {amount} звёзд").format(amount=amount),
        prices=prices,
        provider_token="",
        payload=f"{amount}_stars_{datetime.now(timezone.utc).isoformat()}",  # Добавляем временную метку к payload
        currency="XTR",
        reply_markup=kb.as_markup()
    )


@donat_router.callback_query(F.data == "donate_cancel")
async def on_donate_cancel(callback: CallbackQuery):
    # Обработка отмены доната, выводим сообщение об отмене и удаляем сообщение
    await callback.answer(_("😢 Донат отменен."))
    await callback.message.delete()


# Отправляем сообщение с инструкциями по поддержке покупок
@donat_router.message(Command("paysupport"))
async def cmd_paysupport(message: Message, state: FSMContext):
    data = await state.get_data()
    t_id = data.get('t_id')
    await message.answer(
        text=_('Если вы хотите оформить возврат, воспользуйтесь командой /refund \n\n🤓 Вам понадобится ID транзакции.\n<code>{t_id}</code>').format(t_id=t_id))


# Отправляем условия использования бота (Terms of Service)
@donat_router.message(Command("terms"))
async def cmd_terms(message: Message):
    terms_text = (
        "<b>Terms of Service</b>\n\n"
        "1. Донаты являются добровольными и могут быть возвращены только в течение 30 дней после совершения платежа.\n\n"
        "2. Для возврата средств необходимо предоставить идентификатор транзакции. Получить ID транзакции /paysupport\n\n"
        "3. После истечения 30 дней возврат средств невозможен.\n\n"
        "4. Использование бота подразумевает согласие с данными условиями.\n\n"
    )
    await message.answer(_(terms_text))


@donat_router.message(Command("refund"))
async def cmd_refund(message: Message, bot: Bot, command: CommandObject):
    # ID транзакции для возврата средств
    # Используем для определения, какой товар или услугу пользователь хочет вернуть
    t_id = command.args

    # Проверяем, указан ли ID транзакции
    if t_id is None:
        text = "Пожалуйста, укажите идентификатор транзакции в формате <code>/refund [id]</code>, где [id] это идентификатор транзакции, который вы получили после доната."
        await message.answer(_(text))
        return

    # Проверяем, не истек ли срок возврата, Извлекаем временную метку из payload
    try:
        timestamp_str = t_id.split("_")[-1]
        transaction_time = datetime.fromisoformat(timestamp_str)
        if datetime.utcnow() > transaction_time + timedelta(days=REFUND_PERIOD_DAYS):
            await message.answer(_("Срок для возврата средств истек. Возврат возможен только в течение 30 дней после доната."))
            return

    # Если не удалось распарсить временную метку, выводим сообщение об ошибке
    except (ValueError, IndexError):
        await message.answer(_("Неверный формат идентификатора транзакции."))
        return

    # Пытаемся сделать возврат средств
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=t_id
        )
        await message.answer(_("Рефанд произведен успешно. Потраченные звёзды уже вернулись на ваш счёт в Telegram."))

    except TelegramBadRequest as e:
        err_text = _("Транзакция с указанным идентификатором не найдена. Пожалуйста, проверьте введенные данные и повторите ещё раз.")

        if "CHARGE_ALREADY_REFUNDED" in e.message:
            err_text = _("Рефанд по этой транзакции уже был ранее произведен.")

        await message.answer(err_text)
        return


@donat_router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    # Проверка перед оплатой, бот должен ответить в течение 10 секунд
    # Мы всегда отвечаем положительно, так как это просто донат
    await query.answer(ok=True)

    # Если по какой-то причине нужно отказать в проведении платежа, можно использовать:
    # await query.answer(ok=False, error_message="Причина отказа в проведении платежа")


@donat_router.message(F.successful_payment)
async def on_successfull_payment(message: Message, state: FSMContext):
    # Обработка успешного платежа
    # Получаем объект message.successful_payment с ID транзакции и другим важным содержимым
    t_id = message.successful_payment.telegram_payment_charge_id
    await state.update_data(t_id=t_id)
    await message.answer(
        text=_("<b>🫡 Спасибо!</b>\n"
               "Ваш донат успешно принят.\n"
                "ID транзакции ,code>{t_id}</code>").format(t_id=t_id),
        message_effect_id="5159385139981059251"
    )
        # другие реакции (если надо)
        # 🔥 огонь - 5104841245755180586
        # 👍 лайк - 5107584321108051014
        # 👎 дизлайк - 5104858069142078462
        # ❤️ сердечко - 5159385139981059251
        # 🎉 праздник - 5046509860389126442
        # 💩 какаха - 5046589136895476101
