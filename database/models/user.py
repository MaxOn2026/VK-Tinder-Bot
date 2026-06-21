"""Модель пользователя бота (кто ищет знакомства)."""
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from sqlalchemy import String, Integer, Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

if TYPE_CHECKING:
    from database.models.interaction import UserInteraction
    from database.models.match import Match
    from database.models.interest import Interest


class BotUser(Base):
    """Модель пользователя бота, ищущего знакомства.

    Атрибуты:
        vk_id: ID пользователя ВКонтакте (уникальный идентификатор).
        name: Имя пользователя.
        surname: Фамилия пользователя.
        birthdate: Дата рождения пользователя (опционально).
        gender: Пол пользователя (0-не указан, 1-женщина, 2-мужчина).
        looking_for: Предпочтительный пол для знакомств
            (0-не важно, 1-женщины, 2-мужчины).
        city: Город проживания (опционально).
        age_min: Минимальный приемлемый возраст для мэтчей.
        age_max: Максимальный приемлемый возраст для мэтчей.
        max_distance: Максимальное расстояние в километрах для сопоставления.
        is_active: Активен ли аккаунт пользователя.
        last_active: Дата последней активности пользователя (опционально).

    Связи:
        interactions: Список записей UserInteraction.
        matches_as_user1: Список записей Match, где пользователь — user1.
        matches_as_user2: Список записей Match, где пользователь — user2.
        interests: Список связанных объектов Interest (многие-ко-многим).
    """

    __tablename__ = "bot_users"

    # Основные поля
    vk_id: Mapped[int] = mapped_column(
        Integer, 
        unique=True, 
        nullable=False, 
        index=True,
        comment="ID пользователя ВКонтакте"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    birthdate: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Поля для поиска
    gender: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        nullable=False,
        comment="0-не указан, 1-женщина, 2-мужчина"
    )
    looking_for: Mapped[int] = mapped_column(
        Integer, 
        default=2, 
        nullable=False,
        comment="0-не важно, 1-женщины, 2-мужчины"
    )
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    age_min: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    age_max: Mapped[int] = mapped_column(Integer, default=99, nullable=False)
    max_distance: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    # Статус
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    last_active: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Состояние пользователя (временные данные для навигации)
    state_mode: Mapped[str] = mapped_column(
        String(50),
        default="main_menu",
        nullable=False,
        comment="Текущий режим: partners, favorites, blocked, matches, main_menu"
    )
    state_current_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Текущий индекс в списке"
    )
    state_candidates: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="JSON-список кандидатов для поиска"
    )
    state_favorites_list: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="JSON-список избранных пользователей"
    )
    state_blocked_list: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="JSON-список заблокированных пользователей"
    )
    state_matches_list: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="JSON-список матчей"
    )
    state_user_info: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="JSON-данные о пользователе для поиска"
    )

    # Связи (реляционная магия)
    # Один пользователь → много взаимодействий
    interactions: Mapped[List["UserInteraction"]] = relationship(
        "UserInteraction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Один пользователь → много мэтчей (как первый участник)
    matches_as_user1: Mapped[List["Match"]] = relationship(
        "Match",
        foreign_keys="Match.user1_id",
        back_populates="user1",
        cascade="all, delete-orphan"
    )

    # Один пользователь → много мэтчей (как второй участник)
    matches_as_user2: Mapped[List["Match"]] = relationship(
        "Match",
        foreign_keys="Match.user2_id",
        back_populates="user2",
        cascade="all, delete-orphan"
    )

    # Many-to-many с интересами (через промежуточную таблицу)
    interests: Mapped[List["Interest"]] = relationship(
        "Interest",
        secondary="user_interests",
        back_populates="users",
        lazy="selectin"
    )

    __table_args__ = (
        Index("idx_user_looking_gender", "looking_for", "gender"),
        Index("idx_user_age_range", "age_min", "age_max"),
        Index("idx_user_city_gender", "city", "gender"),
    )

    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя.

        Возвращает:
            str: Конкатенация имени и фамилии.
        """
        return f"{self.name} {self.surname}"

    @property
    def age(self) -> Optional[int]:
        """Вычисляет текущий возраст пользователя.

        Возвращает:
            Optional[int]: Возраст в годах, или None, если дата рождения не установлена.
        """
        if not self.birthdate:
            return None
        today = date.today()
        return today.year - self.birthdate.year - (
            (today.month, today.day) < (self.birthdate.month, self.birthdate.day)
        )

    def __repr__(self) -> str:
        return f"<BotUser(id={self.id}, vk_id={self.vk_id}, name={self.name})>"