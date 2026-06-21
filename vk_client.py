"""Модуль для работы с VK API."""
import vk_api
from vk_api import VkApi
from config import Config


def get_vk_session():
    """Получает сессию VK API с групповым токеном."""
    return VkApi(token=Config.GROUP_TOKEN)


def get_vk_user_session():
    """Получает сессию VK API с пользовательским токеном."""
    return VkApi(token=Config.USER_TOKEN)