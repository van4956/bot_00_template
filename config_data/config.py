from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    """
    Класс для хранения информации о телеграм-боте.
    """
    token: str  # Токен для доступа к телеграм-боту

@dataclass
class Config:
    """
    Основной класс конфигурации приложения.
    """
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    """
    Функция загрузки конфигурации из файла окружения.
    """
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))
