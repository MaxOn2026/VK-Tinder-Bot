"""Модуль для работы с VK API."""
import vk_api
from config import Config


def get_vk_session():
    """Создаёт сессию для группового токена (отправка сообщений)."""
    if not Config.VK_GROUP_TOKEN:
        raise ValueError("VK_GROUP_TOKEN не задан в .env")
    session = vk_api.VkApi(token=Config.VK_GROUP_TOKEN)
    return session


def get_vk_user_session():
    """Создаёт сессию для пользовательского токена (поиск людей)."""
    if not Config.VK_USER_TOKEN:
        raise ValueError("VK_USER_TOKEN не задан в .env")
    return vk_api.VkApi(token=Config.VK_USER_TOKEN)


def get_group_id(session):
    """Получает ID группы."""
    return session.method('groups.getById')[0]['id']