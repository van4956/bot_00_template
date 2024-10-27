from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер будет срабатывать на команду "/delmenu"
# и удалять кнопку Menu c командами
@router.message(Command(commands='delmenu'))
async def del_main_menu(message: Message, bot: Bot):
    await bot.delete_my_commands()
    await message.answer(text=LEXICON_RU['delmenu'])

# Этот хэндлер будет срабатывать на любые ваши сообщения,
# кроме команд "/start" и "/help"
@router.message()
async def send_echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)  # ответ тем же апдейтом в тот же чат
        # await message.answer(message.text)  # простой ответ
        # await message.reply(message.text)  # ответ с цитированием

    except Exception:
        await message.answer(text=LEXICON_RU['no_echo'])
