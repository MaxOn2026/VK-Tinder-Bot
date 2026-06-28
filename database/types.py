"""Пользовательские типы для SQLAlchemy, совместимые с PostgreSQL и SQLite."""
from sqlalchemy import TypeDecorator, String, JSON, Text
from sqlalchemy.dialects.postgresql import ARRAY
import json


class JsonArray(TypeDecorator):
    """Тип для хранения массивов строк.
    
    В PostgreSQL используется ARRAY(String).
    В SQLite и других БД используется JSON.
    """
    
    impl = Text
    cache_ok = True
    
    def __init__(self, item_type=None):
        super().__init__()
        self.item_type = item_type or String()
    
    def load_dialect_impl(self, dialect):
        """Выбирает тип в зависимости от диалекта БД."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(self.item_type))
        else:
            # Для SQLite, MySQL и других используем JSON
            return dialect.type_descriptor(JSON())
    
    def process_bind_param(self, value, dialect):
        """Преобразует Python значение для сохранения в БД."""
        if value is not None:
            if dialect.name == 'postgresql':
                return value  # PostgreSQL сам обработает массив
            else:
                return json.dumps(value)  # Для SQLite сохраняем как JSON
        return value
    
    def process_result_value(self, value, dialect):
        """Преобразует значение из БД в Python."""
        if value is not None:
            if dialect.name == 'postgresql':
                return value  # PostgreSQL сам вернёт список
            else:
                if isinstance(value, str):
                    return json.loads(value)
                return value
        return value