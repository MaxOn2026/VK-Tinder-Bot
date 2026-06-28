"""Базовый класс для всех моделей SQLAlchemy."""

from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Абстрактный базовый класс, предоставляющий общие поля для всех моделей базы данных.

    Этот класс расширяет DeclarativeBase из SQLAlchemy и предоставляет
    стандартные поля (id, created_at, updated_at), которые включены
    во все модели.

    Атрибуты:
        id: Автоинкрементный первичный ключ.
        created_at: Время создания записи.
        updated_at: Время последнего обновления.

    Пример:
        ```python
        class MyModel(Base):
            __tablename__ = "my_table"
            name: Mapped[str] = mapped_column(String(100))
        ```
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Преобразует экземпляр модели в словарь.

        Возвращает:
            dict: Словарь с именами столбцов в качестве ключей и значениями столбцов.
                Подходит для сериализации в JSON.

        Пример:
            ```python
            user = User(id=1, name="Иван")
            user_dict = user.to_dict()
            # {'id': 1, 'name': 'Иван', 'created_at': ..., 'updated_at': ...}
            ```
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
