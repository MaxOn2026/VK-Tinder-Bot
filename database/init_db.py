"""Скрипт для инициализации базы данных."""
from database.db_manager import db_manager
from database.models.user import BotUser
from database.models.profile import VKProfile
from database.models.interaction import UserInteraction, MutualLike
from database.models.match import Match, Message
from database.models.interest import Interest
from database.models.location import Location


def init_database():
    print("🔧 Инициализация базы данных...")
    
    try:
        db_manager.initialize()
        print("✅ Подключение к БД установлено")
        
        db_manager.create_tables()
        print("✅ Таблицы созданы")
        
        db_manager.close()
        print("✅ База данных готова к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise


if __name__ == '__main__':
    init_database()