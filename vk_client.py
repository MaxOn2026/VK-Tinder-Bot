"""Модуль для работы с VK API."""

import logging
import vk_api
from vk_api import VkApi
from config import Config

logger = logging.getLogger(__name__)


def get_vk_session():
    """Получает сессию VK API с групповым токеном.

    Используется для:
    - Отправки сообщений от имени бота
    - Работы с Long Poll API
    - Управления сообществом
    """
    return VkApi(token=Config.GROUP_TOKEN)


def get_vk_user_session():
    """Получает сессию VK API с пользовательским токеном.

    Используется для:
    - Поиска кандидатов (больше прав)
    - Получения информации о пользователях
    - Работы с закрытыми профилями (если есть доступ)
    """
    return VkApi(token=Config.USER_TOKEN)


def check_message_permissions(user_id: int) -> bool:
    """Проверяет, можно ли отправить сообщение пользователю.

    Args:
        user_id: ID пользователя ВКонтакте

    Returns:
        bool: True если можно отправить сообщение, False если нет
    """
    try:
        vk = get_vk_session().get_api()
        # Пытаемся получить информацию о пользователе
        user_info = vk.users.get(user_ids=user_id, fields="can_write_private_message")
        if user_info:
            return user_info[0].get("can_write_private_message", 0) == 1
        return False
    except Exception as e:
        logger.warning(f"⚠️ Не удалось проверить права для пользователя {user_id}: {e}")
        return False
