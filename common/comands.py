# список команд которые мы отправляем боту
# команды в кнопке "Меню", либо через знак "/"

from aiogram.types import BotCommand

private = [
    BotCommand(command='start',description='start'),
    BotCommand(command='help',description='help'),
]

admin_private = [
    BotCommand(command='start',description='start'),
    BotCommand(command='help',description='help'),
    BotCommand(command='admin',description='admin'),
]
