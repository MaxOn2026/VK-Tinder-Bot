"""Модель профиля ВК (анкета, которую ищут)."""
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from database.base import Base

if TYPE_CHECKING:
    from database.models.interaction import UserInteraction
    from database.models.interest import Interest


class VKProfile(Base):
    """Модель анкеты ВК (кандидата для поиска)."""

    __tablename__ = "vk_profiles"

    vk_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="ID пользователя ВКонтакте"
    )
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birth_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    photo_urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    relation: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    education: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Связи
    interactions: Mapped[List["UserInteraction"]] = relationship(
        "UserInteraction",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Many-to-many с интересами
    interests: Mapped[List["Interest"]] = relationship(
        "Interest",
        secondary="profile_interests",
        back_populates="profiles",
        lazy="selectin"
    )

    __table_args__ = (
        Index("idx_profile_city_gender", "city", "gender"),
        Index("idx_profile_age", "birth_year"),
    )

    def __repr__(self) -> str:
        return f"<VKProfile(id={self.id}, vk_id={self.vk_id})>"