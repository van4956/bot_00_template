import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')

import os
from openai import OpenAI

from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.filters import  StateFilter, or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from common import keyboard
from filters.chat_type import ChatTypeFilter
from config_data.config import load_config

# создаем роутер
llm_router = Router()
llm_router.message.filter(ChatTypeFilter(['private']))

# Получаем API ключ для работы с OpenAI
API_GPT = load_config().tg_bot.api_gpt


# Определяем класс состояния LLMs
class LLMs(StatesGroup):
    """Класс состояний для LLMs"""
    dialog_start = State()
    dialog_sistem_promt = State()
    dialog_process = State()

# Создаем константы для текстов, которые используются в декораторах
LLM = __("LLMs 🤖")
START_NEW_DIALOG = __("Начать новый диалог 🤖")
BACK_TO_MAIN = __("Назад на главную ↩️")
FINISH_DIALOG = __("Закончить диалог")


@llm_router.message(StateFilter(None), or_f(F.text == LLM, F.text == START_NEW_DIALOG, Command('llm')))
async def llm_dialog_start(message: Message, state: FSMContext):

    try:
        await message.answer(_("Введите системный промт"))
        await message.answer(_("Например:\n\n<code>Ты полезный помощник. Твой тон должен быть официальным. Ответы должны быть краткими и понятными.</code>"),
                             reply_markup=keyboard.get_keyboard(_("Сразу к запросу ▶️"), _("Назад на главную ↩️"),
                                                                sizes=(1, 1,),
                                                                placeholder='⬇️'))
        await state.set_state(LLMs.dialog_start)

    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        text = str(e)
        await message.answer(text,
                             reply_markup=keyboard.get_keyboard(_("Начать новый диалог 🤖"), _("Назад на главную ↩️"),
                                                                sizes=(1, 1,),
                                                                placeholder='⬇️'))

@llm_router.message(LLMs.dialog_start, F.text)
async def llm_dialog_sistem_promt(message: Message, state: FSMContext):
    model = "gpt-4o"
    await state.update_data(llm_model=model)
    sistem_promt = ('Answering Rules\n\n'
                    'Follow in the strict order:\n\n'
                    '1. USE the language of my message.\n'
                    '2. ONCE PER CHAT assign a real-world expert role to yourself before answering, e.g., "I will answer as a world-famous historical expert <detailed topic> with <most prestigious LOCAL topic REAL award>" or "I will answer as a world-famous <specific science> expert in the <detailed topic> with <most prestigious LOCAL topic award>" etc.\n'
                    '3. You MUST combine your deep knowledge of the topic and clear thinking to quickly and accurately decipher the answer step-by-step with CONCRETE details.\n'
                    '4. I am going to tip $1,000,000 for the best reply.\n'
                    '5. Your answer is critical for my career.\n'
                    '6. Answer the question in a natural, human-like manner.\n'
                    '7. ALWAYS use an answering example for a first message structure.\n'
                    '8. Responses should be output without using Markdown formatting symbols such as hash marks (#) or asterisks (*).\n'
                    '9. Use only these HTML tags for formatting: <b></b>, <i></i>, <code></code>\n'
                    '10. DO NOT use any other HTML tags.\n\n'
                    'Answering in English example\n\n'
                    '<b>I will answer as the world-famous</b> "specific field" scientists with "most prestigious LOCAL award"\n'
                    '"Deep knowledge step-by-step answer, with CONCRETE details"'
                    )

    text = message.text
    try:
        if text == _("Сразу к запросу ▶️"):
            messages_context = [{"role": "system", "content": sistem_promt}]
            await state.update_data(llm_messages_context=messages_context)
        else:
            text = text if text else ' '
            sistem_promt = str(sistem_promt) + '\n\n' + text
            messages_context = [{"role": "system", "content": sistem_promt}]
            await state.update_data(llm_messages_context=messages_context)

        await message.answer(text=_("Введите ваш запрос"),
                            reply_markup=keyboard.get_keyboard(_("Назад на главную ↩️"),
                                                                sizes=(1, 1,),
                                                                placeholder='⬇️'))
        await state.set_state(LLMs.dialog_process)

    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        text = f"Error: {str(e)}"
        await message.answer(text,
                             reply_markup=keyboard.get_keyboard(_("Назад на главную ↩️"),
                                                                sizes=(1, 1,),
                                                                placeholder='⬇️'))

@llm_router.message(LLMs.dialog_process, F.text == FINISH_DIALOG)
async def llm_dialog_finish(message: Message, state: FSMContext):
    await message.answer(_("Диалог завершен.\nЧто дальше?"),
                         reply_markup=keyboard.get_keyboard(_("Начать новый диалог 🤖"),
                                                   _("Назад на главную ↩️"),
                                                    sizes=(1, 1,),
                                                    placeholder='⬇️'))
    await state.update_data(llm_messages_context=None, llm_model=None)
    await state.set_state(None)

@llm_router.message(LLMs.dialog_process, F.text)
async def llm_dialog_process(message: Message, state: FSMContext, workflow_data: dict):
    user_id = message.from_user.id
    state_data = await state.get_data()
    model = state_data['llm_model']
    messages_context = state_data['llm_messages_context']

    try:
        client = OpenAI(api_key=API_GPT)
        role = 'user'
        content = message.text
        messages_context.append({"role": role, "content": content})

        try:
            response = client.chat.completions.create(model=model, messages=messages_context)
            content = response.choices[0].message.content
            messages_context.append({"role": "system", "content": content})
            await state.update_data(llm_messages_context=messages_context)
            answer = f"{model}\n\n{content}"

        except Exception as e:
            logger.error("Ошибка: %s", str(e))
            answer = f"<code>{model}</code>\n\nError: {str(e)}"

    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        answer = f"Connection error to LLM:\n\n{str(e)}"

    # обрезаем ответ, если он превышает 4096 символа
    if len(answer) > 4096:
        answer = answer[:4096] + "..."
    try:
        await message.answer(answer,
                             reply_markup=keyboard.get_keyboard(_("Закончить диалог"),
                                                            sizes=(1,),
                                                            placeholder=_('Введите следующий запрос')))
    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        await message.answer("Error: " + str(e))

    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/expense",
                    command_name="/llm")
