from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    """
    Класс для хранения информации о телеграм-боте.
    """
    token: str
    owner: list[int]
    admin_list: list[int]
    home_group: list[int]

@dataclass
class DataBase:
    """
    Класс для хранения информации о базе данных.
    """
    db_post: str
    db_lite: str

@dataclass
class Config:
    """
    Основной класс конфигурации приложения.
    """
    tg_bot: TgBot
    db: DataBase


# Функция загрузки конфигурации из файла окружения
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    owner = map(int, env('OWNER').split(','))
    admin_list = map(int, env('ADMIN_LIST').split(','))
    home_group = map(int, env('HOME_GROUP').split(','))

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               owner=list(owner),
                               admin_list=list(admin_list),
                               home_group=list(home_group)),
                  db=DataBase(db_post=env('DB_POST'),
                              db_lite=env('DB_LITE')))
