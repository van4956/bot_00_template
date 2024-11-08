import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

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
    work_group: list[int]

@dataclass
class DataBase:
    """
    Класс для хранения информации о базе данных
    """
    db_post: str
    db_lite: str

@dataclass
class InfluxDB:
    """
    Класс для хранения информации о InfluxDB
    """
    admin: str
    password: str
    url: str
    token: str
    bucket: str
    org: str

@dataclass
class Config:
    """
    Основной класс конфигурации всего приложения
    """
    tg_bot: TgBot
    db: DataBase
    influx: InfluxDB


# Функция загрузки конфигурации из файла окружения .env
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    owner = map(int, env('OWNER').split(','))
    admin_list = map(int, env('ADMIN_LIST').split(','))
    home_group = map(int, env('HOME_GROUP').split(','))
    work_group = map(int, env('WORK_GROUP').split(','))

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               owner=list(owner),
                               admin_list=list(admin_list),
                               home_group=list(home_group),
                               work_group=list(work_group)),
                  db=DataBase(db_post=env('DB_POST'),
                              db_lite=env('DB_LITE')),
                  influx=InfluxDB(admin=env('INFLUXDB_ADMIN_USER'),
                                  password=env('INFLUXDB_ADMIN_PASSWORD'),
                                  url=env('INFLUXDB_URL'),
                                  token=env('INFLUXDB_TOKEN'),
                                  bucket=env('INFLUXDB_BUCKET'),
                                  org=env('INFLUXDB_ORG'))
                                  )
