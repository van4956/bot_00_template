import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)


import operator
from aiogram import F, Router, html, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.kbd import Column, Radio
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _




# Инициализируем роутер уровня модуля
aiogram_dialog_router = Router()





class LangSG(StatesGroup):
    start = State()


# Геттер
async def get_languages(dialog_manager: DialogManager, **kwargs):
    checked = dialog_manager.find('radio_lang').get_checked()
    language = {
        '1': 'en',
        '2': 'ru',
        '3': 'fr'
    }
    chosen_lang = language['2' if not checked else checked]
    lang = {
        'ru': {
            '1': '🇬🇧 Английский',
            '2': '🇷🇺 Русский',
            '3': '🇫🇷 Французский',
            'text': 'Выберите язык'
        },
        'en': {
            '1': '🇬🇧 English',
            '2': '🇷🇺 Russian',
            '3': '🇫🇷 French',
            'text': 'Choose language'
        },
        'fr': {
            '1': '🇬🇧 Anglais',
            '2': '🇷🇺 Russe',
            '3': '🇫🇷 Français',
            'text': 'Choisissez la langue'
        }
    }
    languages = [
        (f"{lang[chosen_lang]['1']}", '1'),
        (f"{lang[chosen_lang]['2']}", '2'),
        (f"{lang[chosen_lang]['3']}", '3'),
    ]
    return {"languages": languages,
            'text': lang[chosen_lang]['text']}


start_dialog = Dialog(
    Window(
        Format(text='{text}'),
        Column(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_lang',
                item_id_getter=operator.itemgetter(1),
                items="languages",
            ),
        ),
        state=LangSG.start,
        getter=get_languages
    ),
)

@aiogram_dialog_router.message(Command('lang'))
async def command_start_process(dialog_manager: DialogManager):
    await dialog_manager.start(state=LangSG.start,
                               mode=StartMode.RESET_STACK,
                               show_mode=ShowMode.AUTO)
