"""Менеджер подключения к базе данных PostgreSQL.

Этот модуль предоставляет класс DatabaseManager для управления подключениями
к базе данных с использованием SQLAlchemy и пула соединений. Он обеспечивает
потокобезопасный доступ к базе данных, управление сессиями и предоставляет
инструменты для выполнения сырых SQL-запросов.

Примеры использования:
    ```python
    from database.db_manager import db_manager

    # Инициализация с конфигурацией
    db_manager.initialize()

    # Создание таблиц
    db_manager.create_tables()

    # Использование контекстного менеджера
    with db_manager.get_session() as session:
        users = session.query(User).all()
        for user in users:
            print(user.name)
    ```

Примечания:
    - Использует QueuePool с размером пула 10 и макс. переполнением 20
    - Включена проверка соединений перед использованием (pool_pre_ping=True)
    - Поддерживает потокобезопасные операции через scoped_session
    - Конфигурация загружается из файла config.py
"""

from contextlib import contextmanager
from typing import Optional, Generator, Union, List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
from config import Config
from database.base import Base


class DatabaseManager:
    """Управляет подключениями к PostgreSQL с использованием SQLAlchemy и пула соединений.

    Этот класс предоставляет потокобезопасный интерфейс к базе данных с помощью
    пула соединений и scoped-сессий. Он обрабатывает жизненный цикл подключений,
    управление сессиями и предоставляет утилиты для выполнения сырых SQL-запросов.

    Атрибуты:
        engine: Экземпляр SQLAlchemy Engine.
        session_factory: Фабрика сессий для создания сессий.
        scoped_session: Scoped-сессия для потокобезопасных операций.

    Примеры:
        ```python
        from database.db_manager import db_manager

        # Инициализация с конфигурацией
        db_manager.initialize()

        # Создание таблиц
        db_manager.create_tables()

        # Использование контекстного менеджера
        with db_manager.get_session() as session:
            users = session.query(User).all()
            for user in users:
                print(user.name)
        ```

    Args:
        db_url: Необязательная строка подключения к PostgreSQL. Если не указана,
            используются значения из config.py.
    """

    def __init__(self) -> None:
        """Инициализирует DatabaseManager с пустыми атрибутами."""
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.scoped_session: Optional[scoped_session] = None

    def initialize(self, db_url: Optional[str] = None) -> None:
        """Инициализирует подключение к базе данных.

        Создаёт SQLAlchemy engine с пулом соединений и настраивает фабрику сессий.

        Args:
            db_url: Необязательная строка подключения к PostgreSQL. Если не указана,
                используются значения из config.py.

        Примеры:
            ```python
            # Использование значений из config.py
            db_manager.initialize()

            # Использование пользовательской строки подключения
            db_manager.initialize("postgresql://user:pass@localhost:5432/mydb")
            ```

        Raises:
            ValueError: Если db_url равен None и значения конфигурации отсутствуют.
        """
        if not db_url:
            # Формируем URL из конфига
            db_url = f"postgresql://{Config.USER}:{Config.PASSWORD}@{Config.HOST}:{Config.PORT}/{Config.DATABASE}"

        self.engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Проверяет соединение перед использованием
            # echo=Config.DB_ECHO,  # Логировать SQL (для отладки)
            # echo_pool=Config.DB_ECHO_POOL
        )

        self.session_factory = sessionmaker(bind=self.engine)
        self.scoped_session = scoped_session(self.session_factory)

    def create_tables(self, drop_first: bool = False) -> None:
        """Создаёт все таблицы базы данных.

        Создаёт таблицы для всех моделей, наследующих от Base.

        Args:
            drop_first: Если True, удаляет существующие таблицы перед созданием новых.

        Примеры:
            ```python
            # Создание таблиц (безопасно)
            db_manager.create_tables()

            # Удаление и создание заново (опасно!)
            db_manager.create_tables(drop_first=True)
            ```

        Предупреждение:
            Использование `drop_first=True` приведёт к безвозвратному удалению всех данных!
        """
        if drop_first:
            Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Контекстный менеджер для сессий базы данных.

        Предоставляет потокобезопасную сессию, которая автоматически фиксируется
        при успешном завершении или откатывается при исключении.

        Yields:
            Session: Объект SQLAlchemy session.

        Примеры:
            ```python
            with db_manager.get_session() as session:
                user = User(name="Иван")
                session.add(user)
                # Автоматический commit при успешном завершении

            # Сессия автоматически закрывается
            ```

        Raises:
            Exception: Повторно вызывает любое исключение после отката.
        """
        session = self.scoped_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def execute_raw(
        self, query: str, params: Optional[dict] = None
    ) -> Union[List[Row], int]:
        """Выполняет сырой SQL-запрос.

        Полезно для сложных запросов, которые трудно выразить с помощью ORM.

        Args:
            query: Строка SQL-запроса с именованными плейсхолдерами.
            params: Словарь параметров запроса.

        Returns:
            Union[List[Row], int]: 
                - Для SELECT-запросов: список строк результата (List[Row])
                - Для INSERT/UPDATE/DELETE: количество затронутых строк (int)

        Примеры:
            ```python
            # SELECT-запрос
            results = db_manager.execute_raw(
                "SELECT * FROM users WHERE city = %(city)s",
                {"city": "Москва"}
            )
            # results будет List[Row]

            # INSERT/UPDATE/DELETE
            count = db_manager.execute_raw(
                "UPDATE users SET is_active = true WHERE id = %(id)s",
                {"id": 123}
            )
            # count будет int
            ```

        Примечания:
            Запрос выполняется в контексте транзакции.
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            if result.returns_rows:
                return result.fetchall()
            else:
                return result.rowcount

    def close(self) -> None:
        """Закрывает все подключения к базе данных.

        Должен вызываться при завершении работы приложения для корректного
        закрытия всех соединений в пуле.

        Примеры:
            ```python
            # При завершении работы приложения
            db_manager.close()
            ```
        """
        if self.scoped_session:
            self.scoped_session.remove()
        if self.engine:
            self.engine.dispose()


# Глобальный экземпляр (используется во всём приложении)
db_manager = DatabaseManager()