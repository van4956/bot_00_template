from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import Bot



class IsOwnerFilter(BaseFilter):
    """
    Фильтр, является ли пользователь владельцем бота.
    """
    def __init__(self, is_owner: bool):
        self.is_owner = is_owner

    async def __call__(self, message: Message, bot: Bot) -> bool:

        # Проверяем, находится ли ID пользователя, отправившего сообщение, в списке владельцев
        return message.from_user.id in bot.owner
