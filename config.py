"""Конфигурация приложения."""
from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    """Конфигурация из .env файла."""
    
    # База данных PostgreSQL
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = os.getenv('DB_PORT', '5432')
    DATABASE = os.getenv('DB_NAME', 'vkinder_db')
    USER = os.getenv('DB_USER', 'postgres')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # VK API токены
    GROUP_TOKEN = os.getenv('GROUP_TOKEN')
    USER_TOKEN = os.getenv('USER_TOKEN')
    GROUP_ID = os.getenv('GROUP_ID')  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
    
    # Настройки БД
    DB_ECHO = False
    DB_ECHO_POOL = False
    
    @classmethod
    def get_database_url(cls) -> str:
        """Возвращает URL для подключения к БД."""
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"