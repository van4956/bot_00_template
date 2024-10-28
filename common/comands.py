# список команд которые мы отправляем боту
# команды в кнопке "Меню", либо через знак "/"

from aiogram.types import BotCommand

private = [
    BotCommand(command='start',description='restart the bot'),
    BotCommand(command='help',description='help on using the bot'),
    BotCommand(command='donat',description='donate to the author'),
]

admin_private = [
    BotCommand(command='start',description='restart the bot'),
    BotCommand(command='help',description='help on using the bot'),
    BotCommand(command='donat',description='donate to the author'),
    BotCommand(command='admin',description='admin mode'),
]
