"""Модуль админ-панели."""
import logging
from vk_client import get_vk_session
from database.db_manager import db_manager
from database.models.user import BotUser
from database.models.interaction import UserInteraction
from database.models.match import Match
from sqlalchemy import func

logger = logging.getLogger(__name__)

# ID администратора (замени на свой VK ID)
ADMIN_ID = 232206603


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    return user_id == ADMIN_ID


def get_all_users() -> list:
    """Получает список всех пользователей бота."""
    with db_manager.get_session() as session:
        users = session.query(BotUser).all()
        return [
            {
                'vk_id': user.vk_id,
                'name': f"{user.name} {user.surname}",
                'is_active': user.is_active,
                'created_at': user.created_at
            }
            for user in users
        ]


def get_user_statistics(user_id: int) -> dict:
    """Получает детальную статистику пользователя."""
    with db_manager.get_session() as session:
        user = session.query(BotUser).filter(BotUser.vk_id == user_id).first()
        
        if not user:
            return None
        
        likes_count = session.query(func.count(UserInteraction.id)).filter(
            UserInteraction.user_id == user.id,
            UserInteraction.action == 'like'
        ).scalar()
        
        blocks_count = session.query(func.count(UserInteraction.id)).filter(
            UserInteraction.user_id == user.id,
            UserInteraction.action == 'block'
        ).scalar()
        
        matches_count = session.query(func.count(Match.id)).filter(
            (Match.user1_id == user.id) | (Match.user2_id == user.id)
        ).scalar()
        
        return {
            'vk_id': user.vk_id,
            'name': f"{user.name} {user.surname}",
            'likes': likes_count,
            'blocks': blocks_count,
            'matches': matches_count,
            'is_active': user.is_active
        }


def toggle_user_status(user_id: int) -> bool:
    """Блокирует/разблокирует пользователя."""
    with db_manager.get_session() as session:
        user = session.query(BotUser).filter(BotUser.vk_id == user_id).first()
        
        if not user:
            return False
        
        user.is_active = not user.is_active
        session.commit()
        
        return user.is_active


def send_broadcast(message: str) -> int:
    """Отправляет сообщение всем активным пользователям."""
    with db_manager.get_session() as session:
        users = session.query(BotUser).filter(BotUser.is_active == True).all()
        
        vk = get_vk_session().get_api()
        sent_count = 0
        
        for user in users:
            try:
                vk.messages.send(
                    user_id=user.vk_id,
                    message=message,
                    random_id=0
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Ошибка отправки пользователю {user.vk_id}: {e}")
        
        return sent_count