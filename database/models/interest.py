"""Модель интересов пользователей."""
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Table, Column, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

if TYPE_CHECKING:
    from database.models.user import BotUser
    from database.models.profile import VKProfile


# Промежуточная таблица: пользователь <-> интерес
user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("bot_users.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", Integer, ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
)


# Промежуточная таблица: профиль ВК <-> интерес
profile_interests = Table(
    "profile_interests",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("vk_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", Integer, ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
)


class Interest(Base):
    """Модель интереса (хобби, увлечение)."""

    __tablename__ = "interests"

    title: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Название интереса"
    )

    # Many-to-many с пользователями
    users: Mapped[List["BotUser"]] = relationship(
        "BotUser",
        secondary=user_interests,
        back_populates="interests",
        lazy="selectin"
    )

    # Many-to-many с профилями ВК
    profiles: Mapped[List["VKProfile"]] = relationship(
        "VKProfile",
        secondary=profile_interests,
        back_populates="interests",
        lazy="selectin"
    )

    __table_args__ = (
        Index("idx_interest_title_trigram", "title", postgresql_using="gin", postgresql_ops={"title": "gin_trgm_ops"}),
    )

    def __repr__(self) -> str:
        return f"<Interest(id={self.id}, title='{self.title}')>"