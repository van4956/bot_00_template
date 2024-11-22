import logging
from typing import Any

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)



from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, PhotoSize
from aiogram.utils.i18n import gettext as _
from icecream import ic as debug

# debug.disable()  # Отключить вывод
# debug.enable()  # Включить вывод
debug.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')

# Инициализируем роутер уровня модуля
questionnaire_router = Router()

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool | Any]] = {}


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_age = State()         # Состояние ожидания ввода возраста
    fill_gender = State()      # Состояние ожидания выбора пола
    upload_photo = State()     # Состояние ожидания загрузки фото
    fill_education = State()   # Состояние ожидания выбора образования
    fill_wish_news = State()   # Состояние ожидания выбора получать ли новости


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@questionnaire_router.message(Command('questionnaire'), StateFilter(default_state))
async def process_fsm_command(message: Message):
    await message.answer(
        text=_('Чтобы перейти к заполнению анкеты - '
             'отправьте команду /fillform\n\n'
             'Чтобы прервать заполнение анкеты - отправьте команду /cancel')
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@questionnaire_router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text=_('Отменять нечего. Вы вне машины состояний\n\n'
             'Чтобы перейти к заполнению анкеты - '
             'отправьте команду /fillform')
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@questionnaire_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text=_('Вы вышли из машины состояний\n\n'
             'Чтобы снова перейти к заполнению анкеты - '
             'отправьте команду /fillform')
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    # await state.clear()

    # Завершаем машину состояний, но не удаляем данные из словаря FSMContext
    await state.set_state(None)


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@questionnaire_router.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text=_('Пожалуйста, введите ваше имя'))
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@questionnaire_router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text=_('Спасибо!\n\nА теперь введите ваш возраст'))
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_age)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@questionnaire_router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text=_('То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel'))


# Этот хэндлер будет срабатывать, если введен корректный возраст
# и переводить в состояние выбора пола
@questionnaire_router.message(StateFilter(FSMFillForm.fill_age),
            lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем возраст в хранилище по ключу "age"
    await state.update_data(age=message.text)
    # Создаем объекты инлайн-кнопок
    male_button = InlineKeyboardButton(
        text=_('Мужской ♂'),
        callback_data='male'
    )
    female_button = InlineKeyboardButton(
        text=_('Женский ♀'),
        callback_data='female'
    )
    undefined_button = InlineKeyboardButton(
        text=_('🤷 Пока не ясно'),
        callback_data='undefined_gender'
    )
    # Добавляем кнопки в клавиатуру (две в одном ряду и одну в другом)
    keyboard: list[list[InlineKeyboardButton]] = [
        [male_button, female_button],
        [undefined_button]
    ]
    # Создаем объект инлайн-клавиатуры
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=_('Спасибо!\n\nУкажите ваш пол'),
        reply_markup=markup
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_gender)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@questionnaire_router.message(StateFilter(FSMFillForm.fill_age))
async def warning_not_age(message: Message):
    await message.answer(
        text=_('Возраст должен быть целым числом от 4 до 120\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе пола и переводить в состояние отправки фото
@questionnaire_router.callback_query(StateFilter(FSMFillForm.fill_gender), F.data.in_(['male', 'female', 'undefined_gender']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender"
    await state.update_data(gender=callback.data)
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка фото
    # чтобы у пользователя не было желания тыкать кнопки
    await callback.message.delete()
    await callback.message.answer(
        text=_('Спасибо! А теперь загрузите, пожалуйста, ваше фото')
    )
    # Устанавливаем состояние ожидания загрузки фото
    await state.set_state(FSMFillForm.upload_photo)


# Этот хэндлер будет срабатывать, если во время выбора пола
# будет введено/отправлено что-то некорректное
@questionnaire_router.message(StateFilter(FSMFillForm.fill_gender))
async def warning_not_gender(message: Message):
    await message.answer(
        text=_('Пожалуйста, пользуйтесь кнопками '
             'при выборе пола\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')
    )


# Этот хэндлер будет срабатывать, если отправлено фото
# и переводить в состояние выбора образования
@questionnaire_router.message(StateFilter(FSMFillForm.upload_photo), F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,
                             state: FSMContext,
                             largest_photo: PhotoSize):
    # Cохраняем данные фото (file_unique_id и file_id) в хранилище
    # по ключам "photo_unique_id" и "photo_id"
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )
    # Создаем объекты инлайн-кнопок
    secondary_button = InlineKeyboardButton(
        text=_('Среднее'),
        callback_data='secondary'
    )
    higher_button = InlineKeyboardButton(
        text=_('Высшее'),
        callback_data='higher'
    )
    no_edu_button = InlineKeyboardButton(
        text=_('🤷 Нету'),
        callback_data='no_edu'
    )
    # Добавляем кнопки в клавиатуру (две в одном ряду и одну в другом)
    keyboard: list[list[InlineKeyboardButton]] = [
        [secondary_button, higher_button],
        [no_edu_button]
    ]
    # Создаем объект инлайн-клавиатуры
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=_('Спасибо!\n\nУкажите ваше образование'),
        reply_markup=markup
    )
    # Устанавливаем состояние ожидания выбора образования
    await state.set_state(FSMFillForm.fill_education)


# Этот хэндлер будет срабатывать, если во время отправки фото
# будет введено/отправлено что-то некорректное
@questionnaire_router.message(StateFilter(FSMFillForm.upload_photo))
async def warning_not_photo(message: Message):
    await message.answer(
        text=_('Пожалуйста, на этом шаге отправьте '
             'ваше фото\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')
    )


# Этот хэндлер будет срабатывать, если выбрано образование
# и переводить в состояние согласия получать новости
@questionnaire_router.callback_query(StateFilter(FSMFillForm.fill_education),
                   F.data.in_(['secondary', 'higher', 'no_edu']))
async def process_education_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем данные об образовании по ключу "education"
    await state.update_data(education=callback.data)
    # Создаем объекты инлайн-кнопок
    yes_news_button = InlineKeyboardButton(
        text=_('Да'),
        callback_data='yes_news'
    )
    no_news_button = InlineKeyboardButton(
        text=_('Нет, спасибо'),
        callback_data='no_news')
    # Добавляем кнопки в клавиатуру в один ряд
    keyboard: list[list[InlineKeyboardButton]] = [
        [yes_news_button, no_news_button]
    ]
    # Создаем объект инлайн-клавиатуры
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Редактируем предыдущее сообщение с кнопками, отправляя
    # новый текст и новую клавиатуру
    await callback.message.edit_text(
        text=_('Спасибо!\n\nОстался последний шаг.\n'
             'Хотели бы вы получать новости?'),
        reply_markup=markup
    )
    # Устанавливаем состояние ожидания выбора получать новости или нет
    await state.set_state(FSMFillForm.fill_wish_news)


# Этот хэндлер будет срабатывать, если во время выбора образования
# будет введено/отправлено что-то некорректное
@questionnaire_router.message(StateFilter(FSMFillForm.fill_education))
async def warning_not_education(message: Message):
    await message.answer(
        text=_('Пожалуйста, пользуйтесь кнопками при выборе образования\n\n'
             'Если вы хотите прервать заполнение анкеты - отправьте '
             'команду /cancel')
    )


# Этот хэндлер будет срабатывать на выбор получать или
# не получать новости и выводить из машины состояний
@questionnaire_router.callback_query(StateFilter(FSMFillForm.fill_wish_news), F.data.in_(['yes_news', 'no_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем данные о получении новостей по ключу "wish_news"
    await state.update_data(wish_news=callback.data == 'yes_news')

    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя
    user_dict[callback.from_user.id] = await state.get_data()
    debug(user_dict)

    users = await state.get_data()
    debug(users)

    # Завершаем машину состояний, но не удаляем данные из словаря FSMContext
    await state.set_state(None)

    # Отправляем в чат сообщение о выходе из машины состояний
    await callback.message.edit_text(
        text=_('Спасибо! Ваши данные сохранены!\n\n'
             'Вы вышли из машины состояний')
    )
    # Отправляем в чат сообщение с предложением посмотреть свою анкету
    await callback.message.answer(
        text=_('Чтобы посмотреть данные вашей '
             'анкеты - отправьте команду /showdata')
    )


# Этот хэндлер будет срабатывать, если во время согласия на получение
# новостей будет введено/отправлено что-то некорректное
@questionnaire_router.message(StateFilter(FSMFillForm.fill_wish_news))
async def warning_not_wish_news(message: Message):
    await message.answer(
        text=_('Пожалуйста, воспользуйтесь кнопками!\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')
    )


# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@questionnaire_router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message, state: FSMContext):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'], # type: ignore
            caption=_('Имя: {name}\n'
                       'Возраст: {age}\n'
                        'Пол: {gender}\n'
                        'Образование: {education}\n'
                        'Получать новости: {wish_news}').format(name=user_dict[message.from_user.id]["name"],
                                                                age=user_dict[message.from_user.id]["age"],
                                                                gender=user_dict[message.from_user.id]["gender"],
                                                                education=user_dict[message.from_user.id]["education"],
                                                                wish_news=user_dict[message.from_user.id]["wish_news"])
        )
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(
            text=_('Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /fillform')
        )

    data = await state.get_data()
    debug(data)
    await message.answer(str(data))
