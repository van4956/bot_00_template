# Файл с конфигурационными данными для бота, базы данных, сторонних сервисов и т.п.

from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    db_lite: str          # Название мини лайт бд
    database: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


# Функция, которая будет читать файл .env и возвращать
# экземпляр класса Config с заполненными полями token и admin_ids
def load_config(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(
                tg_bot=TgBot(token=env('BOT_TOKEN'),
                            admin_ids=list(map(int, env.list('ADMIN_IDS')))
                            ),
                db=DatabaseConfig(db_lite=env('DB_LITE'),
                                database=env('DATABASE'),
                                db_host=env('DB_HOST'),
                                db_user=env('DB_USER'),
                                db_password=env('DB_PASSWORD')
                                )
                            )
