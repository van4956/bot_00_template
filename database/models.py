# Модуль с ORM-моделями базы данных, то есть
# Отображаем базы данных в виде объекта с атрибутами, совпадающими с полями базы данных
# Через эти объекты можно обращаться к базе данных и как-то взаимодействовать с ней, обращаясь к атрибутам и методам объектов

from sqlalchemy import DateTime, Float, String, Text, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# создаем первичный класс, от него дальше будут наследоваться все остальные
class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

# class Users соответствует таблице users в базе данных
class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(150), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    active: Mapped[int] = mapped_column(Integer, nullable=False)
    block: Mapped[int] = mapped_column(Integer, nullable=False)
