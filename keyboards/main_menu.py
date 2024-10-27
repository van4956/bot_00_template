# Модуль для установки команд в нативную кнопку "Menu"

from aiogram.types import BotCommand


main_menu_commands = [
    BotCommand(command='start',description='Старт'),
    BotCommand(command='menu',description='Меню'),
    BotCommand(command='about',description='О нас'),
    BotCommand(command='help',description='Помощь'),
    BotCommand(command='command_1',description='command_1 desription'),
    BotCommand(command='command_2',description='command_2 desription'),
    BotCommand(command='command_3',description='command_3 desription'),
    BotCommand(command='command_4',description='command_4 desription'),
]
