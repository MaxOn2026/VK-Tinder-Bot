"""Модуль для операций с базой данных — публичный API."""
from database.base import Base
from database.db_manager import db_manager
from database.models.user import BotUser
from database.models.profile import VKProfile
from database.models.interest import Interest, user_interests, profile_interests
from database.models.interaction import UserInteraction, MutualLike
from database.models.match import Match, Message
from database.models.location import Location

__all__ = [
    # Базовые классы
    "Base",
    "db_manager",

    # Модели
    "BotUser",
    "VKProfile",
    "Interest",
    "UserInteraction",
    "MutualLike",
    "Match",
    "Message",
    "Location",

    # Промежуточные таблицы
    "user_interests",
    "profile_interests",
]

# Инициализация БД при импорте (опционально)
def init_db(db_url: str | None = None, drop_tables: bool = False) -> None:
    """Инициализирует базу данных и создаёт таблицы.

    Args:
        db_url: Необязательная строка подключения к PostgreSQL. Если не указана,
            используются значения из config.py.
        drop_tables: Если True, удаляет существующие таблицы перед созданием новых.
    """
    db_manager.initialize(db_url)
    db_manager.create_tables(drop_first=drop_tables)
