from icecream import ic as debug

debug.disable()  # Отключить вывод
debug.enable()  # Включить вывод
debug.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')

a = 10
b = 20

debug(a, b, a+b)