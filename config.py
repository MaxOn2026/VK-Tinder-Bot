"""Модуль конфигурации. Загружает переменные окружения."""
import os
from dotenv import load_dotenv

load_dotenv()

GROUP_TOKEN = os.getenv('GROUP_TOKEN')
USER_TOKEN = os.getenv('USER_TOKEN')

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')