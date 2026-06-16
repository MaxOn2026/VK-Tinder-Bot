"""Модели интересов и связей многие-ко-многим."""
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import Integer
from sqlalchemy import String, Table, Column, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

if TYPE_CHECKING:
    from database.models.user import BotUser
    from database.models.profile import VKProfile


# Промежуточная таблица: пользователи бота ↔ интересы
user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("user_id", ForeignKey("bot_users.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)

# Промежуточная таблица: анкеты ВК ↔ интересы
profile_interests = Table(
    "profile_interests",
    Base.metadata,
    Column("profile_id", ForeignKey("vk_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Interest(Base):
    """Модель интереса/хобби (справочник для сопоставления пользователей и профилей).

    Атрибуты:
        title: Название интереса (уникальное).
        category: Категория (music, sport, books, movies и т.д.).
        vk_external_id: ID группы/страницы ВКонтакте, связанной с интересом (опционально).

    Связи:
        users: Список связанных объектов BotUser (многие-ко-многим).
        profiles: Список связанных объектов VKProfile (многие-ко-многим).
    """

    __tablename__ = "interests"

    title: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Название интереса (например, 'рок', 'футбол', 'python')"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True, 
        index=True,
        comment="Категория: music, sport, books, movies и т.д."
    )
    vk_external_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True,
        comment="ID группы/страницы ВКонтакте, связанной с интересом"
    )

    # Связи
    users: Mapped[List["BotUser"]] = relationship(
        "BotUser",
        secondary=user_interests,
        back_populates="interests",
        lazy="selectin"
    )

    profiles: Mapped[List["VKProfile"]] = relationship(
        "VKProfile",
        secondary=profile_interests,
        back_populates="interests",
        lazy="selectin"
    )

    __table_args__ = (
        Index("idx_interest_title_trigram", "title", postgresql_using="gin", 
            postgresql_ops={"title": "gin_trgm_ops"}),
    )

    def __repr__(self) -> str:
        return f"<Interest(id={self.id}, title={self.title})>"
