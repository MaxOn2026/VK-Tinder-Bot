"""Фикстуры для тестов."""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database.base import Base
from database.db_manager import DatabaseManager


@pytest.fixture
def test_engine():
    """Создаёт тестовый движок SQLite."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Включаем поддержку JSON для SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
    
    # Создаём таблицы
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Создаёт тестовую сессию."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)


@pytest.fixture
def test_db_manager(test_engine):
    """Создаёт тестовый DatabaseManager."""
    manager = DatabaseManager()
    manager.engine = test_engine
    manager.session_factory = sessionmaker(bind=test_engine)
    manager.scoped_session = sessionmaker(bind=test_engine)
    return manager