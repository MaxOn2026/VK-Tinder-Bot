"""Модель анкеты ВКонтакте (кого предлагаем для знакомств)."""
from typing import Optional, List
from sqlalchemy import String, Integer, Index, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base
from database.models.interest import Interest


class VKProfile(Base):
    """Модель анкеты пользователя ВКонтакте (целевая аудитория для знакомств).

    Атрибуты:
        vk_id: ID анкеты ВКонтакте (уникальный идентификатор).
        first_name: Имя анкеты.
        last_name: Фамилия анкеты.
        birth_year: Год рождения (опционально).
        gender: Пол (0-не указан, 1-женщина, 2-мужчина).
        city: Город (опционально).
        photo_urls: Список URL фотографий (опционально).
        relation: Семейное положение (опционально).
        education: Информация об образовании (опционально).

    Связи:
        interests: Список связанных объектов Interest (многие-ко-многим).
    """

    __tablename__ = "vk_profiles"

    # Основные поля
    vk_id: Mapped[int] = mapped_column(
        Integer, 
        unique=True, 
        nullable=False, 
        index=True,
        comment="ID пользователя ВКонтакте"
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    gender: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        nullable=False, 
        index=True,
        comment="0-не указан, 1-женщина, 2-мужчина"
    )
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Фото (массив URL)
    photo_urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Дополнительные данные
    relation: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # семейное положение
    education: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Связи
    # Many-to-many с интересами
    interests: Mapped[List["Interest"]] = relationship(
        "Interest",
        secondary="profile_interests",
        back_populates="profiles",
        lazy="selectin"
    )

    __table_args__ = (
        Index("idx_profile_city_gender_age", "city", "gender", "birth_year"),
        Index("idx_profile_full_name", "first_name", "last_name"),
    )

    @property
    def age(self) -> Optional[int]:
        """Вычисляет текущий возраст по году рождения.

        Возвращает:
            Optional[int]: Возраст в годах, или None, если год рождения не установлен.
        """
        if not self.birth_year:
            return None
        from datetime import date
        return date.today().year - self.birth_year

    @property
    def full_name(self) -> str:
        """Возвращает полное имя анкеты.

        Возвращает:
            str: Конкатенация first_name и last_name.
        """
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<VKProfile(id={self.id}, vk_id={self.vk_id}, name={self.first_name})>"
