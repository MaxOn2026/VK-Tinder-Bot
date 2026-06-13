"""Модуль для работы с VK API."""
import vk_api
from config import GROUP_TOKEN, USER_TOKEN


def get_vk_session():
    """Создаёт сессию для группового токена (отправка сообщений)."""
    session = vk_api.VkApi(token=GROUP_TOKEN)
    return session


def get_vk_user_session():
    """Создаёт сессию для пользовательского токена (поиск людей)."""
    if not USER_TOKEN:
        raise ValueError("USER_TOKEN не задан в .env")
    return vk_api.VkApi(token=USER_TOKEN)


def get_group_id(session):
    """Получает ID группы."""
    return session.method('groups.getById')[0]['id']