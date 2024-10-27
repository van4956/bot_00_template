# Модуль в котором создаем движок базы данных
# Функцию create_db() и drop_db() прописываем в главном файле main.py

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from environs import Env

from database.models import Base

env = Env()
env.read_env()
db_lite = env('DB_LITE')

# Создаем движок базы данных, echo=True чтобы выводить все sql запросы в терминал
engine = create_async_engine(db_lite) #, echo=True)

# Создаем ассинхронную сессию
# Позволяет выполнять операции с базой данных без блокировки основного потока выполнения
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Ассинхронная функция, создаем все таблицы наследники Base
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функцию удаления всех таблиц
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
