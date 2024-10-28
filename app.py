# source venv/Scripts/activate
# ctrl + B                        -  запуск скрипта из любого файла проекта
# ctrl + I                        -  варианты эмодзи

import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode  # импорт типов разметки сообщений для бота
from config_data.config import Config, load_config

from common.comands import private, admin_private
from dispatcher import dp

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)

# Выводим в консоль информацию о начале запуска бота
logger.info('Starting bot')

# Функция конфигурирования и запуска бота
async def main() -> None:

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот
    logger.info('Инициализируем бот')
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    bot.owner = [459148628]
    bot.admin_list = [459148628]
    bot.home_group = [-4197834633]


    # удаляем вебхуки (то что бот получил пока спал)
    await bot.delete_webhook(drop_pending_updates=True)

    # удаляем ранее установленные команды для бота во всех личных чатах
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())

    # добавляем команды
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())

    for admin_id in bot.admin_list:
        await bot.set_my_commands(commands=admin_private, scope=types.BotCommandScopeChat(chat_id=admin_id))

    # запускаем polling, отбираем только используемые события по роутерам
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    # # start polling
    # try:
    #     await dp.start_polling(bot, skip_updates=False) # Не пропускаем обновления, если наш бот будет обрабатывать платежи или другие важные вещи.
    # finally:
    #     await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
