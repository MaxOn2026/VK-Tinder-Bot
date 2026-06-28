"""Пользовательские типы для тестов."""
from sqlalchemy import TypeDecorator, String, JSON
from sqlalchemy.dialects.postgresql import ARRAY


class ArrayType(TypeDecorator):
    """Тип для хранения массивов, совместимый с SQLite и PostgreSQL."""
    
    impl = String
    cache_ok = True
    
    def __init__(self, item_type=None, *args, **kwargs):
        super().__init__()
        self.item_type = item_type or String()
    
    def load_dialect_impl(self, dialect):
        """Выбирает тип в зависимости от диалекта."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(self.item_type))
        else:
            # Для SQLite используем JSON
            return dialect.type_descriptor(JSON())
    
    def process_bind_param(self, value, dialect):
        """Преобразует значение для сохранения в БД."""
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                import json
                return json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Преобразует значение при чтении из БД."""
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                import json
                return json.loads(value)
        return value