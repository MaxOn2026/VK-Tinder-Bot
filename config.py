"""Модуль конфигурации для VK-Tinder-Bot.

Этот модуль загружает переменные окружения и предоставляет классы конфигурации
для приложения. Он обрабатывает настройки подключения к базе данных и учетные
данные API ВКонтакте через переменные окружения.

Пример:
    ```python
    from config import Config
    
    # Доступ к значениям конфигурации
    db_host = Config.HOST
    vk_token = Config.VK_GROUP_TOKEN
    ```
"""
from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    """Класс конфигурации для приложения VK-Tinder-Bot.
    
    Этот класс предоставляет централизованное управление конфигурацией для приложения,
    загружая значения из переменных окружения с разумными значениями по умолчанию,
    где это применимо.
    
    Атрибуты:
        HOST (str): Адрес хоста базы данных. По умолчанию 'localhost'.
        PORT (int): Номер порта базы данных. По умолчанию 5432.
        DATABASE (str): Имя базы данных. Обязательно, нет значения по умолчанию.
        USER (str): Имя пользователя базы данных. Обязательно, нет значения по умолчанию.
        PASSWORD (str): Пароль базы данных. Обязательно, нет значения по умолчанию.
        VK_GROUP_TOKEN (str): Токен группы ВКонтакте для операций бота.
            Обязательно для отправки сообщений. Нет значения по умолчанию.
        VK_USER_TOKEN (str): Токен пользователя ВКонтакте для операций API.
            Обязательно для доступа к данным пользователя. Нет значения по умолчанию.
        VK_TOKEN (str): Алиас для VK_USER_TOKEN для обратной совместимости.
        VK_API_VERSION (str): Версия API ВКонтакте. По умолчанию '5.199'.
        DB_ECHO (bool): Включить логирование SQL-запросов. По умолчанию False.
        DB_ECHO_POOL (bool): Включить логирование пула соединений. По умолчанию False.
    
    Пример:
        ```python
        from config import Config
        
        print(f"База данных: {Config.DATABASE}")
        print(f"VK Токен: {Config.VK_GROUP_TOKEN}")
        ```
    """
    
    HOST = os.getenv('HOST', 'localhost')
    PORT = os.getenv('PORT', '5432')
    DATABASE = os.getenv('DATABASE')
    USER = os.getenv('DB_USER')
    PASSWORD = os.getenv('PASSWORD')

    VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
    VK_USER_TOKEN = os.getenv('VK_USER_TOKEN')
    VK_TOKEN = os.getenv('VK_TOKEN')
    VK_API_VERSION = os.getenv('VK_API_VERSION', '5.199')
    DB_ECHO = os.getenv('DB_ECHO', 'false').lower() == 'true'
    DB_ECHO_POOL = os.getenv('DB_ECHO_POOL', 'false').lower() == 'true'
